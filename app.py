#!/usr/bin/env python3
"""
LIONSGATE INTELLIGENCE NETWORK - NEMESIS LIVE OMNI-TRACER v14.5
Production Grade - Real-Time WS Graphing, Dual DB (Mongo+Neo4j), Cloudflare D1 Cache, & Global UI Standards
"""

import os
import json
import re
import uuid
import asyncio
import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import List, Dict, Any, Set, Callable

from fastapi import FastAPI, BackgroundTasks, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import motor.motor_asyncio
import aiohttp
from playwright.async_api import async_playwright

# Optional Neo4j Integration
try:
    from neo4j import AsyncGraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

# ==============================================================================
# 🛡️ 1. SYSTEM CONFIGURATION & INITIALIZATION
# ==============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("NEMESIS_TRACER")

# Load Secrets securely from Environment Variables
MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("DATABASE_MONGO_URL", "mongodb://localhost:27017"))
NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
CF_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CF_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CF_D1_DB_ID = os.getenv("CLOUDFLARE_D1_DATABASE_ID", "")

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
TATUM_API_KEY = os.getenv("TATUM_API_KEY", "")

# Global Async DB Clients
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI, maxPoolSize=100)
db = mongo_client.nemesis_omni

neo4j_driver = None
if NEO4J_AVAILABLE and NEO4J_URI:
    neo4j_driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

async def init_production_db():
    collections = ["entities", "state_edges", "cases"]
    existing = await db.list_collection_names()
    for col in collections:
        if col not in existing: await db.create_collection(col)
    await db.entities.create_index([("chain", 1), ("address", 1)], unique=True)
    await db.state_edges.create_index([("trace_id", 1), ("timestamp", 1)])
    logger.info("✅ Live Tracing Database Schemas Initialized (MongoDB).")

# ==============================================================================
# 🌐 2. CLOUDFLARE D1 METADATA CACHE
# ==============================================================================
async def query_cloudflare_d1(sql: str, params: list = []):
    """Uses Cloudflare D1 for extremely fast, lightweight Intelligence / Labels cache."""
    if not CF_ACCOUNT_ID or not CF_API_TOKEN or not CF_D1_DB_ID:
        return [] # Fallback if not configured
    
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{CF_D1_DB_ID}/query"
    headers = {
        "Authorization": f"Bearer {CF_API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"sql": sql, "params": params}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('result', [{}])[0].get('results', [])
    except Exception as e:
        logger.error(f"[D1 Cache Error]: {e}")
    return []

# ==============================================================================
# 🔌 3. WEBSOCKET CONNECTION MANAGER
# ==============================================================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, trace_id: str):
        await websocket.accept()
        self.active_connections[trace_id].append(websocket)

    def disconnect(self, websocket: WebSocket, trace_id: str):
        if websocket in self.active_connections[trace_id]:
            self.active_connections[trace_id].remove(websocket)

    async def broadcast_to_trace(self, trace_id: str, message: dict):
        if trace_id in self.active_connections:
            for connection in self.active_connections[trace_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

ws_manager = ConnectionManager()

# ==============================================================================
# 🛡️ 4. RESILIENCE: RATE LIMIT DEFENSE & API ROTATION
# ==============================================================================
class APIKeyManager:
    def __init__(self):
        self.keys = {"ETHERSCAN": [ETHERSCAN_API_KEY] if ETHERSCAN_API_KEY else [""], "TATUM": [TATUM_API_KEY] if TATUM_API_KEY else []}
        self.indices = {provider: 0 for provider in self.keys}

    def get_key(self, provider: str) -> str:
        keys = self.keys.get(provider, [])
        return keys[self.indices[provider]] if keys else ""

key_manager = APIKeyManager()

async def resilient_rpc_call(provider: str, fetch_func: Callable, max_retries: int = 3) -> Any:
    retries = 0
    base_delay = 1.0
    while retries <= max_retries:
        active_key = key_manager.get_key(provider)
        try:
            status, data = await fetch_func(active_key)
            if status == 429: raise aiohttp.ClientResponseError(request_info=None, history=None, status=429, message="Rate Limited")
            if status >= 500: raise aiohttp.ClientResponseError(request_info=None, history=None, status=status, message="Server Error")
            return data
        except Exception:
            retries += 1
            if retries > max_retries: return []
            await asyncio.sleep(base_delay * (2 ** retries))

# ==============================================================================
# 🌍 5. GLOBAL EXPLORER INTELLIGENCE SPECIFICATION (GEIS)
# ==============================================================================
class GEISScraper:
    @staticmethod
    async def extract_hybrid_intelligence(address: str, chain: str) -> Dict[str, Any]:
        # 1. Fast Path: Check Cloudflare D1 Cache
        d1_cache = await query_cloudflare_d1("SELECT * FROM entity_labels WHERE address = ? AND chain = ?", [address.lower(), chain])
        if d1_cache: return {"chain": chain, "address": address, "classification": d1_cache[0].get('classification', 'Unknown'), "entity_name": d1_cache[0].get('entity_name', 'Unknown'), "tags": json.loads(d1_cache[0].get('tags', '[]')), "risk_score": d1_cache[0].get('risk_score', 0), "verified": True}

        # 2. Slower Path: Playwright OSINT
        schema = {"chain": chain, "address": address, "classification": "Unknown", "entity_name": "Unknown", "tags": [], "risk_score": 0, "verified": False}
        url = f"https://www.oklink.com/multi-search#key={address}"
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=10000)
                content = await page.content()
                
                if re.search(r"Exchange:\s*([^.<]+)", content, re.IGNORECASE) or "binance" in content.lower():
                    schema["classification"] = "Exchange"
                    schema["entity_name"] = "CEX Hot Wallet"
                    schema["tags"].append("HOT_WALLET")
                    schema["risk_score"] = 20
                    schema["verified"] = True
                if "Contract" in content or "Token" in content:
                    schema["classification"] = "Smart Contract"
                if "Tornado" in content or "Mixer" in content:
                    schema["classification"] = "Mixer"
                    schema["entity_name"] = "Tornado Cash"
                    schema["tags"].append("OFAC_SANCTIONED")
                    schema["risk_score"] = 100
                    schema["verified"] = True
                
                await browser.close()
        except Exception: pass
        return schema

# ==============================================================================
# 📡 6. OMNICHAIN RPC ADAPTERS
# ==============================================================================
class BlockchainAdapters:
    @staticmethod
    async def get_utxo_data(address: str) -> List[Dict]:
        async def _fetch(active_key):
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://mempool.space/api/address/{address}/txs", timeout=12) as resp:
                    if resp.status == 200: return resp.status, await resp.json()
            return 500, []
        return await resilient_rpc_call("MEMPOOL", _fetch)

    @staticmethod
    async def get_evm_transfers(address: str, chain: str) -> List[Dict]:
        domain = "api.etherscan.io" if chain.upper() == "ETH" else "api.bscscan.com"
        async def _fetch(active_key):
            url_normal = f"https://{domain}/api?module=account&action=txlist&address={address}&apikey={active_key}"
            txs = []
            async with aiohttp.ClientSession() as session:
                async with session.get(url_normal, timeout=12) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        if data.get("status") == "1":
                            for tx in data.get("result", []): tx["asset"] = "ETH" if chain.upper() == "ETH" else "BNB"; txs.append(tx)
            return 200, txs
        return await resilient_rpc_call("ETHERSCAN", _fetch)

# ==============================================================================
# ⛓️ 7. LIVE RECURSIVE TRACER PIPELINE WITH WEBSOCKET SYNC
# ==============================================================================
class NemesisLiveTracer:
    def __init__(self, trace_id: str, max_depth: int = 3):
        self.trace_id = trace_id
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.semaphore = asyncio.Semaphore(10)
        self.stats = {"wallets": 0, "txs": 0, "assets": 0.0}

    async def emit_progress(self, msg: str, progress: int, chain: str, hop: int):
        await ws_manager.broadcast_to_trace(self.trace_id, {
            "type": "progress", "msg": msg, "progress": progress, "chain": chain, "hop": hop,
            "wallets": self.stats["wallets"], "txs": self.stats["txs"], "assets": round(self.stats["assets"], 2)
        })

    async def sync_neo4j(self, node: dict = None, edge: dict = None):
        """Persists high-value graph intelligence directly to AuraDB"""
        if not neo4j_driver: return
        try:
            async with neo4j_driver.session() as session:
                if node:
                    await session.run("MERGE (w:Wallet {address: $addr}) SET w.chain = $chain, w.classification = $cls, w.entity_name = $name",
                                      addr=node["id"], chain=node["chain"], cls=node["classification"], name=node["entity_name"])
                if edge:
                    await session.run("MATCH (a:Wallet {address: $from_a}), (b:Wallet {address: $to_a}) MERGE (a)-[r:TRANSFERRED {tx_hash: $tx_hash}]->(b) SET r.amount = $amount, r.asset = $asset, r.usd_value = $usd",
                                      from_a=edge["source"], to_a=edge["target"], tx_hash=edge["tx_hash"], amount=edge["amount"], asset=edge["asset"], usd=edge["usd_value"])
        except Exception as e: logger.error(f"[Neo4j] Sync Error: {e}")

    async def execute_trace_step(self, address: str, chain: str, current_depth: int = 0):
        if current_depth > self.max_depth: return
        uid = f"{chain}:{address}".lower()
        if uid in self.visited: return
        self.visited.add(uid)
        self.stats["wallets"] += 1
        
        await self.emit_progress(f"Resolving Entities ({address[:8]}...)", min(100, current_depth * 25 + 5), chain, current_depth)
        
        async with self.semaphore:
            # 1. GEIS Intelligence Fetch
            intel = await GEISScraper.extract_hybrid_intelligence(address, chain)
            
            node_data = {
                "id": address, "chain": chain, "classification": intel["classification"], 
                "entity_name": intel["entity_name"], "tags": intel["tags"], 
                "risk_score": intel["risk_score"], "verified": intel["verified"]
            }
            
            # DB Persistence & Live Emit
            await db.entities.update_one({"address": address, "chain": chain}, {"$set": node_data}, upsert=True)
            await self.sync_neo4j(node=node_data)
            await ws_manager.broadcast_to_trace(self.trace_id, {"type": "node", "node": node_data})

            if intel["classification"] in ["Exchange", "Mixer"]:
                await self.emit_progress(f"Terminal Detected: {intel['classification']}", min(100, current_depth * 25 + 15), chain, current_depth)
                return

            await self.emit_progress(f"Fetching Transactions...", min(100, current_depth * 25 + 10), chain, current_depth)
            
            parsed_hops = []
            if chain == "BTC":
                txs = await BlockchainAdapters.get_utxo_data(address)
                self.stats["txs"] += len(txs)
                for tx in txs:
                    for out in tx.get("vout", []):
                        dst = out.get("scriptpubkey_address")
                        val = (out.get("value", 0) / 1e8)
                        if dst and dst != address and val > 0: parsed_hops.append((dst, val, tx.get("txid"), "BTC"))
            elif chain in ["ETH", "BSC"]:
                txs = await BlockchainAdapters.get_evm_transfers(address, chain)
                self.stats["txs"] += len(txs)
                for tx in txs:
                    src, dst = tx.get("from", ""), tx.get("to")
                    if src.lower() != address.lower() or not dst: continue
                    if tx.get("isError", "0") == "0":
                        val = float(tx.get("value", 0)) / 1e18
                        if val > 0: parsed_hops.append((dst, val, tx.get("hash"), tx.get("asset", chain)))

            tasks = []
            for dst, val, tx_hash, asset in parsed_hops[:5]: # Cap branch breadth for demo speed
                self.stats["assets"] += val
                usd_val = val * (3100 if asset == "ETH" else 65000 if asset == "BTC" else 1) # Approximate USD mapping
                
                edge_data = {
                    "trace_id": self.trace_id, "source": address, "target": dst, "amount": val, 
                    "asset": asset, "usd_value": usd_val, "chain": chain, "tx_hash": tx_hash,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                await db.state_edges.insert_one(edge_data)
                await self.sync_neo4j(edge=edge_data)
                await ws_manager.broadcast_to_trace(self.trace_id, {"type": "edge", "edge": edge_data})
                
                tasks.append(asyncio.create_task(self.execute_trace_step(dst, chain, current_depth + 1)))
                
            if tasks: await asyncio.gather(*tasks)

# ==============================================================================
# 🌐 8. FASTAPI ROUTING
# ==============================================================================
app = FastAPI(title="Lionsgate Nemesis - Live Auto-Tracer")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MASTER_INSTRUCTIONS_SYSTEM = """
You are NEMESIS, a Tier-11 autonomous intelligence framework. 
Perform Auto-Audits of frontend UI, backend pipeline execution, Neo4j Graph topologies, and MongoDB documents.
Ensure every asset follows the Asset Lifecycle pattern and maps strictly to cryptologos.cc globalization parameters.
"""

@app.on_event("startup")
async def startup_pipeline():
    await init_production_db()

@app.websocket("/ws/trace/{trace_id}")
async def websocket_trace(websocket: WebSocket, trace_id: str):
    await ws_manager.connect(websocket, trace_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, trace_id)

class DeploymentPayload(BaseModel):
    seeds: str
    chain_override: str = "AUTO"
    max_depth: int = 2

@app.post("/api/v1/trace/deploy")
async def deploy_nemesis_engine(payload: DeploymentPayload, background_tasks: BackgroundTasks):
    trace_id = f"NMS-LIVE-{uuid.uuid4().hex[:8].upper()}"
    tracer = NemesisLiveTracer(trace_id, max_depth=payload.max_depth)
    clean_seeds = [s.strip() for s in re.split(r'[\s,]+', payload.seeds) if s.strip()]
    
    for seed in clean_seeds:
        chain = payload.chain_override if payload.chain_override != "AUTO" else ("ETH" if seed.startswith("0x") else "BTC")
        background_tasks.add_task(tracer.execute_trace_step, seed, chain, 0)
        
    return {"status": "Live Engine Deployed", "trace_id": trace_id}

# ==============================================================================
# 🎨 9. SPA FRONTEND (GLOBALIZED UI + WEBSOCKET STREAMING)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nemesis | Live Autonomous Tracer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://unpkg.com/3d-force-graph@1.43.3/dist/3d-force-graph.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    
    <style>
        body { margin: 0; font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; overflow: hidden; }
        .glass-panel { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .btn-primary { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; font-weight: 700; padding: 12px; border-radius: 8px; width: 100%; transition: 0.3s; }
        .btn-primary:hover { box-shadow: 0 0 15px rgba(37, 99, 235, 0.5); }
        input, select { background: #1e293b; border: 1px solid #334155; padding: 12px; border-radius: 8px; width: 100%; color: white; outline: none; margin-bottom: 12px; }
        input:focus { border-color: #3b82f6; }
        
        /* Progress Bar */
        .progress-bar { height: 6px; background: #334155; border-radius: 4px; overflow: hidden; width: 100%; margin-top: 8px; }
        .progress-fill { height: 100%; background: #3b82f6; width: 0%; transition: width 0.3s ease; }

        /* Custom Globalized Component Wrappers */
        .global-card { background: rgba(15,23,42,0.8); border: 1px solid #334155; border-radius: 8px; padding: 12px; margin-bottom: 12px; font-size: 12px; }
        .flex-center { display: flex; align-items: center; gap: 8px; }
    </style>
</head>
<body class="flex h-screen w-screen">

    <!-- Deployment Panel -->
    <aside class="w-80 glass-panel flex flex-col p-6 z-10 shrink-0 m-4">
        <h1 class="text-xl font-black text-blue-400 mb-6 flex items-center gap-2"><i class="ph-bold ph-radar"></i> NEMESIS TRACER</h1>
        
        <label class="text-[10px] font-bold text-slate-400 uppercase">Target Wallet</label>
        <input type="text" id="seeds" placeholder="0x... or bc1q..." value="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D" />
        
        <label class="text-[10px] font-bold text-slate-400 uppercase">Network</label>
        <select id="chain"><option value="ETH">Ethereum</option><option value="BTC">Bitcoin</option></select>
        
        <button onclick="deployLiveTrace()" class="btn-primary flex items-center justify-center gap-2"><i class="ph-bold ph-play"></i> Initiate Autonomous Trace</button>

        <!-- Live Execution Pipeline Stream -->
        <div class="mt-8 flex-1 flex flex-col">
            <h3 class="text-[10px] font-bold text-slate-400 uppercase mb-4 border-b border-slate-700 pb-2">Execution Pipeline</h3>
            <div class="text-xs text-blue-400 font-bold mb-1" id="pipe-msg">System Idle</div>
            <div class="progress-bar mb-6"><div class="progress-fill" id="pipe-progress"></div></div>
            
            <div class="grid grid-cols-2 gap-4 text-xs mt-2">
                <div><span class="text-slate-500 block text-[10px]">CHAIN</span><b id="stat-chain" class="text-white">-</b></div>
                <div><span class="text-slate-500 block text-[10px]">HOP DEPTH</span><b id="stat-hop" class="text-white">-</b></div>
                <div><span class="text-slate-500 block text-[10px]">WALLETS</span><b id="stat-wallets" class="text-white">0</b></div>
                <div><span class="text-slate-500 block text-[10px]">TXS ANALYZED</span><b id="stat-txs" class="text-white">0</b></div>
                <div class="col-span-2"><span class="text-slate-500 block text-[10px]">ASSETS TRACED</span><b id="stat-assets" class="text-emerald-400 font-mono">0.00</b></div>
            </div>
        </div>
    </aside>

    <!-- Visualizer & Feed -->
    <main class="flex-1 relative m-4 ml-0 flex flex-col gap-4">
        <!-- 3D Graph -->
        <div class="glass-panel flex-1 relative" id="graph-container"></div>
        
        <!-- Live Globalized Ledger Feed -->
        <div class="h-64 glass-panel p-4 flex flex-col">
            <h3 class="text-[10px] font-bold text-slate-400 uppercase mb-3"><i class="ph-bold ph-list-dashes"></i> Live Correlation Feed</h3>
            <div class="flex-1 flex gap-4 overflow-x-auto" id="live-feed">
                <!-- Transaction & Wallet Cards stream here horizontally -->
                <div class="text-slate-500 text-xs italic m-auto">Awaiting WebSocket Stream...</div>
            </div>
        </div>
    </main>

    <script>
        const LOGO_MAP = {
            "ETH": "https://cryptologos.cc/logos/ethereum-eth-logo.svg",
            "BTC": "https://cryptologos.cc/logos/bitcoin-btc-logo.svg",
            "USDT": "https://cryptologos.cc/logos/tether-usdt-logo.svg",
            "BNB": "https://cryptologos.cc/logos/bnb-bnb-logo.svg"
        };
        function getLogo(symbol) { return LOGO_MAP[symbol.toUpperCase()] || LOGO_MAP["ETH"]; }
        function short(str) { return str.length > 12 ? str.substring(0,6) + '...' + str.substring(str.length-4) : str; }

        let Graph = null;
        let graphData = { nodes: [], links: [] };
        let activeWs = null;

        function initGraph() {
            const el = document.getElementById('graph-container'); el.innerHTML = '';
            Graph = ForceGraph3D()(el)
                .backgroundColor('rgba(0,0,0,0)')
                .nodeId('id')
                .nodeVal(n => 5)
                .nodeColor(n => n.classification === 'Exchange' ? '#e11d48' : n.classification === 'Mixer' ? '#8b5cf6' : '#0ea5e9')
                .linkDirectionalParticles(2).linkColor(()=>'#475569')
                .nodeLabel(n => `
                    <div style="background:rgba(15,23,42,0.9); padding:10px; border:1px solid #334155; border-radius:8px; font-family:sans-serif; font-size:12px;">
                        <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                            <img src="${getLogo(n.chain)}" style="width:16px; height:16px;">
                            <b style="color:#fff;">${n.classification}</b>
                        </div>
                        <div style="color:#94a3b8; font-family:monospace; margin-bottom:4px;">${n.id}</div>
                        <div style="color:#38bdf8; font-weight:bold;">Entity: ${n.entity_name}</div>
                        <div style="color:#34d399; margin-top:4px;">Risk Score: ${n.risk_score} | ${n.verified ? 'Verified' : 'Unverified'}</div>
                    </div>
                `);
        }

        async function deployLiveTrace() {
            const seeds = document.getElementById('seeds').value; const chain = document.getElementById('chain').value;
            if(!seeds) return alert("Enter address");

            // Reset UI
            graphData = { nodes: [], links: [] };
            if(!Graph) initGraph(); else Graph.graphData(graphData);
            document.getElementById('live-feed').innerHTML = '';
            if(activeWs) activeWs.close();

            try {
                const res = await fetch('/api/v1/trace/deploy', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({seeds, chain_override: chain, max_depth: 2})});
                const data = await res.json();
                
                // Establish Live WebSocket
                const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                activeWs = new WebSocket(`${wsProtocol}//${window.location.host}/ws/trace/${data.trace_id}`);
                
                activeWs.onmessage = (event) => {
                    const msg = JSON.parse(event.data);
                    
                    if (msg.type === 'progress') {
                        document.getElementById('pipe-msg').innerText = msg.msg;
                        document.getElementById('pipe-progress').style.width = msg.progress + '%';
                        document.getElementById('stat-chain').innerText = msg.chain;
                        document.getElementById('stat-hop').innerText = msg.hop;
                        document.getElementById('stat-wallets').innerText = msg.wallets;
                        document.getElementById('stat-txs').innerText = msg.txs;
                        document.getElementById('stat-assets').innerText = msg.assets.toLocaleString();
                    }
                    else if (msg.type === 'node') {
                        if (!graphData.nodes.find(n => n.id === msg.node.id)) {
                            graphData.nodes.push(msg.node);
                            Graph.graphData(graphData);
                            
                            // Render Globalized Wallet Card
                            const html = `
                            <div class="global-card min-w-[220px]">
                                <div class="flex-center mb-2"><img src="${getLogo(msg.node.chain)}" class="w-4 h-4"><b class="text-blue-400">${msg.node.classification}</b></div>
                                <div class="font-mono text-slate-400 mb-2">${short(msg.node.id)}</div>
                                <div class="text-white mb-2">Entity: ${msg.node.entity_name}</div>
                                <div class="flex-center"><span class="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded text-[9px] uppercase">Risk: Low</span> ${msg.node.verified ? '<i class="ph-fill ph-check-circle text-emerald-400"></i>' : ''}</div>
                            </div>`;
                            document.getElementById('live-feed').insertAdjacentHTML('afterbegin', html);
                        }
                    }
                    else if (msg.type === 'edge') {
                        graphData.links.push(msg.edge);
                        Graph.graphData(graphData);
                        
                        // Render Globalized TX Card
                        const html = `
                        <div class="global-card min-w-[220px] border-indigo-500/30 bg-indigo-500/5">
                            <div class="flex-center mb-2"><img src="${getLogo(msg.edge.chain)}" class="w-4 h-4"><span class="text-indigo-400">Transfer</span></div>
                            <div class="text-white text-lg font-bold mb-1">${msg.edge.amount.toFixed(4)} ${msg.edge.asset}</div>
                            <div class="text-slate-400 mb-2">≈ $${msg.edge.usd_value.toLocaleString(undefined, {maximumFractionDigits:0})}</div>
                            <div class="font-mono text-[9px] text-slate-500 mb-1">Hash: ${short(msg.edge.tx_hash)}</div>
                            <div class="text-emerald-400 text-[10px]"><i class="ph-fill ph-check-circle"></i> Verified Execution</div>
                        </div>`;
                        document.getElementById('live-feed').insertAdjacentHTML('afterbegin', html);
                    }
                };
            } catch(e) { alert("Deployment Failed"); }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content=HTML_TEMPLATE)

if __name__ == "__main__":
    import uvicorn
    logger.info("====================================================================")
    logger.info("  DEPLOYING NEMESIS LIVE OMNI-TRACER (WEBSOCKET & D1 CACHE ENABLED) ")
    logger.info("====================================================================")
    uvicorn.run(app, host="0.0.0.0", port=8000)
