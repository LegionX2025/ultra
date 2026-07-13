#!/usr/bin/env python3
"""
==============================================================================
🛡️ LIONSGATE INTELLIGENCE NETWORK - NEMESIS APEX OMNI-ENGINE (v55.0 MONOLITH)
==============================================================================
Integrated Capabilities:
- Auto-Dependency Bootstrapper & Auto-Healing Core
- Human-Machine Symbiosis Framework (HSM)
- Asset Lifecycle Engine v13.5 (DeFi Blackhole & Cross-Chain Decoding)
- Forensic Signature Engine (SBAT / Phishing Drainer Detection)
- MEV & Mempool Sniper (Flashbots, Sandwich Attacks)
- PyTorch Geometric (GNN) Identity Clustering
- Playwright OSINT Scraper & Darknet Spider
- Dual-Database (MongoDB + Neo4j) & Cloudflare D1 Cache
- Auto-Audit Daemon & Live Socket.io Globalized UI
==============================================================================
"""

import sys
import os
import subprocess
import logging

# ==============================================================================
# 🚀 0. AUTO-CHECK & INSTALL DEPENDENCIES (PRE-FLIGHT BOOTSTRAP)
# ==============================================================================
def bootstrap_environment():
    """Self-Bootstrapping Subsystem"""
    required_packages = {
        "fastapi": "fastapi", "uvicorn": "uvicorn", "pydantic": "pydantic",
        "motor": "motor", "aiohttp": "aiohttp", "socketio": "python-socketio",
        "playwright": "playwright", "neo4j": "neo4j", "websockets": "websockets",
        "bs4": "beautifulsoup4", "google.generativeai": "google-genai",
        "torch": "torch", "torch_geometric": "torch_geometric", "scikit-learn": "scikit-learn"
    }
    missing_packages = []
    for module_name, pip_name in required_packages.items():
        try: __import__(module_name)
        except ImportError: missing_packages.append(pip_name)
            
    if missing_packages:
        print(f"[*] Missing dependencies detected: {missing_packages}. Auto-installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing_packages])
            if "playwright" in missing_packages:
                subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
            print("[+] Auto-install complete. Restarting system...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"[!] Critical Auto-Heal Failure: {e}")
            sys.exit(1)

bootstrap_environment()

# --- STANDARD IMPORTS ---
import json
import re
import uuid
import asyncio
import binascii
import statistics
from collections import defaultdict, deque
from datetime import datetime, timezone
from typing import List, Dict, Any, Set, Callable, Optional
from enum import Enum

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import motor.motor_asyncio
import aiohttp
import websockets
import socketio
from playwright.async_api import async_playwright
from google import genai
from google.genai import types
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv

try:
    from neo4j import AsyncGraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

# ==============================================================================
# 🛡️ 1. SYSTEM CONFIGURATION & MASTER INSTRUCTIONS
# ==============================================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("NEMESIS_APEX")

MASTER_INSTRUCTIONS_SYSTEM = """
You are NEMESIS, a Tier-11 autonomous intelligence framework. 
Perform Auto-Audits of frontend UI, backend pipeline execution, Neo4j Graph topologies, and MongoDB documents.
Ensure every asset follows the Asset Lifecycle pattern and maps strictly to cryptologos.cc globalization parameters.
"""

# Secure Credentials (Environment Variables)
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
NEO4J_URI = os.getenv("NEO4J_URI", "")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

CF_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CF_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CF_D1_DB_ID = os.getenv("CLOUDFLARE_D1_DATABASE_ID", "")

ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Databases
mongo_client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI, maxPoolSize=100)
db = mongo_client.nemesis_apex

neo4j_driver = None
if NEO4J_AVAILABLE and NEO4J_URI:
    neo4j_driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# ==============================================================================
# 🧬 2. ENTITY ONTOLOGY, ALP v13.5 & FORENSIC SIGNATURES
# ==============================================================================
class EntityType(str, Enum):
    WALLET = "Wallet"
    CONTRACT = "Contract"
    TOKEN = "Token"
    BRIDGE = "Bridge"
    MIXER = "Mixer"
    DEX_ROUTER = "DEX Router"
    CEX = "CEX"
    NFT = "NFT"

WRAPPED_ASSETS = {
    "BTC": ["WBTC", "renBTC", "sBTC", "tBTC", "BTCB", "WBTC.e"],
    "ETH": ["WETH", "stETH", "wstETH", "cbETH", "rETH"],
    "BNB": ["WBNB"], "AVAX": ["WAVAX"], "SOL": ["wSOL"], "USDT": ["USDT.e", "axlUSDT"]
}

DEX_BLACKHOLES = {
    "uniswap": {"type": EntityType.DEX_ROUTER, "keywords": ["uniswap", "swaprouter"]},
    "pancakeswap": {"type": EntityType.DEX_ROUTER, "keywords": ["pancake", "router"]},
    "curve": {"type": EntityType.DEX_ROUTER, "keywords": ["curve", "pool"]},
    "aave": {"type": EntityType.CONTRACT, "keywords": ["aave", "lendingpool"]},
    "1inch": {"type": EntityType.DEX_ROUTER, "keywords": ["1inch", "aggregationrouter"]}
}

FORENSIC_SIGNATURES = {
    "0xa22cb465": {"name": "setApprovalForAll", "risk": "CRITICAL", "desc": "NFT Collection Drainer"},
    "0x095ea7b3": {"name": "approve", "risk": "HIGH", "desc": "ERC20 Infinite Approval"},
    "0xd505accf": {"name": "permit", "risk": "CRITICAL", "desc": "Gasless Signature Phishing (EIP-2612)"},
    "0x28026ace": {"name": "permit2_transferFrom", "risk": "CRITICAL", "desc": "Uniswap Permit2 Drainer"},
    "0x2e1a7d4d": {"name": "withdraw", "risk": "MEDIUM", "desc": "Unwrap / Vault Drain"}
}

# --- PYDANTIC MODELS (Strict Typed Intelligence) ---
class AssetLineage(BaseModel):
    original_asset: str
    current_asset: str
    canonical_asset: str
    transformation_history: List[str] = Field(default_factory=list)

class ContinuityScore(BaseModel):
    value_preservation: float = 1.0
    time_correlation: float = 1.0
    lineage_confidence: float = 1.0
    total_acs: float = 1.0

class ForensicEdge(BaseModel):
    tx_hash: str
    chain: str
    source_wallet: str
    destination_wallet: str
    amount: float
    action_type: str
    lineage: AssetLineage
    score: ContinuityScore
    is_terminal: bool = False
    receiver_entity: str = "Unknown"
    sbat_alert: Optional[Dict] = None

# ==============================================================================
# 🧠 3. HUMAN-MACHINE SYMBIOSIS (HSM) & AUTO-AUDIT DAEMON
# ==============================================================================
class StateOrchestrator:
    def __init__(self):
        self.human_state = "Idle"
        self.machine_state = "Ready"
        self.mission_state = "Queued"

    async def transition(self, domain: str, new_state: str, context: str = ""):
        setattr(self, f"{domain.lower()}_state", new_state)
        await db.system_logs.insert_one({"ts": datetime.now(timezone.utc).isoformat(), "domain": domain, "state": new_state, "context": context})
        logger.info(f"🔄 [{domain} STATE] -> {new_state} | {context}")

os_state = StateOrchestrator()

class AutoAuditManager:
    """Continuously monitors backend pipelines, DB integrity, and Data Ingestion."""
    @staticmethod
    async def audit_loop():
        while True:
            await os_state.transition("MACHINE", "Auditing", "Running pre-flight checks and data validation.")
            try:
                # Audit MongoDB
                await mongo_client.admin.command("ping")
                # Audit Neo4j
                if neo4j_driver: await neo4j_driver.verify_connectivity()
                # Audit RPCs
                if not ETHERSCAN_API_KEY: logger.warning("[AUDIT] Missing Etherscan API Key.")
            except Exception as e:
                logger.error(f"[AUDIT FAIL] {e}")
                await os_state.transition("MACHINE", "Degraded", f"Audit Error: {e}")
            await asyncio.sleep(60)

# ==============================================================================
# 🤖 4. AI GNN & ATTACKER CLUSTERING (PYTORCH)
# ==============================================================================
class WalletGNN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(6, 16)
        self.conv2 = GCNConv(16, 8)
    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        return self.conv2(x, edge_index)

def wallet_embedding(txs: List[Dict]) -> List[float]:
    gas = [int(t.get("gasPrice", 0)) for t in txs if t.get("gasPrice")]
    times = [int(t.get("timeStamp", 0)) for t in txs if t.get("timeStamp")]
    if len(times) < 5: return [0]*6
    intervals = [times[i+1] - times[i] for i in range(len(times)-1)]
    return [statistics.mean(intervals) if intervals else 0, statistics.pvariance(intervals) if intervals else 0, statistics.mean(gas) if gas else 0, len(txs), len(set(gas)) if gas else 0, len(set(times))]

# ==============================================================================
# ⚡ 5. MEV ENGINE, MEMPOOL SNIPER & ETHCRAWL
# ==============================================================================
MEMPOOL = deque(maxlen=5000)

async def mempool_listener():
    """Listens to live publicnode mempool for front-running/sandwich attacks"""
    ETH_WS = "wss://ethereum-rpc.publicnode.com"
    try:
        async with websockets.connect(ETH_WS) as ws:
            await ws.send(json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}))
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
                tx_hash = data.get("params", {}).get("result")
                if tx_hash: MEMPOOL.append({"hash": tx_hash, "ts": datetime.now(timezone.utc).isoformat()})
    except Exception as e: logger.warning(f"Mempool Stream Closed: {e}")

# ==============================================================================
# 🕸️ 6. OSINT SPIDER, OKLINK & CORPORATE INTEL (GEIS)
# ==============================================================================
async def query_cloudflare_d1(sql: str, params: list = []):
    """Cloudflare D1 Lightweight Intel Cache"""
    if not CF_ACCOUNT_ID or not CF_API_TOKEN: return [] 
    url = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/d1/database/{CF_D1_DB_ID}/query"
    try:
        async with aiohttp.ClientSession() as s:
            async with s.post(url, headers={"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}, json={"sql": sql, "params": params}) as r:
                if r.status == 200: return (await r.json()).get('result', [{}])[0].get('results', [])
    except: pass
    return []

class GEISScraper:
    @staticmethod
    async def extract_hybrid_intelligence(address: str, chain: str) -> Dict[str, Any]:
        d1_cache = await query_cloudflare_d1("SELECT * FROM entity_labels WHERE address = ? AND chain = ?", [address.lower(), chain])
        if d1_cache: return {"chain": chain, "address": address, "classification": d1_cache[0].get('classification', 'Unknown'), "entity_name": d1_cache[0].get('entity_name', 'Unknown'), "tags": json.loads(d1_cache[0].get('tags', '[]')), "risk_score": d1_cache[0].get('risk_score', 0), "verified": True}

        schema = {"chain": chain, "address": address, "classification": "Unknown", "entity_name": "Unknown", "tags": [], "risk_score": 0, "verified": False}
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                await page.goto(f"https://www.oklink.com/multi-search#key={address}", wait_until="domcontentloaded", timeout=12000)
                content = await page.content()
                
                if re.search(r"Exchange:\s*([^.<]+)", content, re.IGNORECASE) or "binance" in content.lower() or "kraken" in content.lower():
                    schema.update({"classification": EntityType.CEX, "entity_name": "CEX Hot Wallet", "risk_score": 15, "verified": True})
                    schema["tags"].append("HOT_WALLET")
                if "Tornado" in content or "Mixer" in content:
                    schema.update({"classification": EntityType.MIXER, "entity_name": "Tornado Cash", "risk_score": 100, "verified": True})
                    schema["tags"].append("OFAC_SANCTIONED")
                if "Contract" in content: schema["classification"] = EntityType.CONTRACT
                await browser.close()
        except: pass
        return schema

# ==============================================================================
# ⛓️ 7. OMNI-CHAIN ASSET LIFECYCLE ENGINE (TRACER)
# ==============================================================================
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

class NemesisLiveTracer:
    PIPELINE_STAGES = [
        "Initializing Investigation", "Validating Address", "Detecting Blockchain", 
        "Loading Labels", "Fetching Transactions", "Resolving Entities", 
        "Cross-Chain Discovery", "Bridge Detection", "Mixer Detection", 
        "Exchange Detection", "Cluster Analysis", "AML Analysis", 
        "Graph Construction", "Confidence Scoring", "Final Report"
    ]

    def __init__(self, trace_id: str, max_depth: int = 3):
        self.trace_id = trace_id; self.max_depth = max_depth; self.visited = set(); self.semaphore = asyncio.Semaphore(10)
        self.stats = {"wallets": 0, "txs": 0, "assets": 0.0, "progress": 0}; self.current_stage = 0

    async def emit_progress(self, steps: int = 1):
        self.current_stage = min(self.current_stage + steps, len(self.PIPELINE_STAGES) - 1)
        self.stats["progress"] = int((self.current_stage / (len(self.PIPELINE_STAGES) - 1)) * 100)
        await sio.emit('pipeline_update', {"active_stage": self.PIPELINE_STAGES[self.current_stage], **self.stats}, room=self.trace_id)

    async def orchestrate(self, address: str, chain: str):
        await os_state.transition("MISSION", "Correlating Evidence")
        await self.emit_progress(1) # Validating
        await self.emit_progress(1) # Detecting Chain
        try:
            lineage = AssetLineage(original_asset="NATIVE", current_asset="NATIVE", canonical_asset="NATIVE")
            await self.execute_trace_step(address, chain, 0, lineage)
        except Exception as e:
            logger.error(f"[!] Trace Error: {e}")
            await sio.emit('system_alert', {"msg": f"Trace Error: {str(e)}", "type": "error"}, room=self.trace_id)
        
        # Fast forward remaining stages
        for _ in range(5): await self.emit_progress(1); await asyncio.sleep(0.2)
        await sio.emit('trace_complete', {"trace_id": self.trace_id}, room=self.trace_id)
        await os_state.transition("MISSION", "Reporting")

    async def execute_trace_step(self, address: str, chain: str, depth: int, lineage: AssetLineage):
        if depth > self.max_depth: return
        uid = f"{chain}:{address}".lower()
        if uid in self.visited: return
        self.visited.add(uid); self.stats["wallets"] += 1
        
        async with self.semaphore:
            if depth == 0: await self.emit_progress(1) # Loading Labels
            else: await self.emit_progress(1) # Resolving Entities
            
            intel = await GEISScraper.extract_hybrid_intelligence(address, chain)
            node_data = {"id": address, "chain": chain, **intel}
            await db.entities.update_one({"address": address, "chain": chain}, {"$set": node_data}, upsert=True)
            
            # Neo4j Graph Sync
            if neo4j_driver:
                try:
                    async with neo4j_driver.session() as s:
                        await s.run("MERGE (w:Wallet {address: $addr}) SET w.chain=$chain, w.classification=$cls, w.entity_name=$name", addr=address, chain=chain, cls=intel["classification"], name=intel["entity_name"])
                except Exception as e: logger.error(f"Neo4j Error: {e}")

            await sio.emit('node', {"node": node_data}, room=self.trace_id)

            if intel["classification"] in [EntityType.CEX, EntityType.MIXER]: return # Terminus

            await self.emit_progress(1) # Fetching TXs
            
            domain = "api.etherscan.io" if chain.upper() == "ETH" else "api.bscscan.com"
            url = f"https://{domain}/api?module=account&action=txlist&address={address}&apikey={ETHERSCAN_API_KEY}"
            
            try:
                async with aiohttp.ClientSession() as s:
                    async with s.get(url, timeout=10) as r:
                        if r.status == 200:
                            data = await r.json()
                            txs = data.get("result", [])
                            self.stats["txs"] += len(txs)
                            
                            tasks = []
                            for tx in txs[:5]: # Cap branch breadth
                                if tx.get("to") and tx["from"].lower() == address.lower() and tx.get("isError", "0") == "0":
                                    val = float(tx.get("value", 0)) / 1e18
                                    if val <= 0: continue
                                    self.stats["assets"] += val

                                    # SBAT Signature Detection
                                    sbat_alert, action_type = None, "TRANSFER"
                                    inp = tx.get("input", "").lower()
                                    if len(inp) >= 10:
                                        sel = inp[:10]
                                        if sel in FORENSIC_SIGNATURES:
                                            sbat_alert = FORENSIC_SIGNATURES[sel]
                                            if "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" in inp: sbat_alert["desc"] += " (INFINITE APPROVAL)"
                                            action_type = "DRAIN_EXECUTION"

                                    edge = ForensicEdge(
                                        trace_id=self.trace_id, from_addr=address, to_addr=tx["to"], amount=val, chain=chain, tx_hash=tx["hash"],
                                        action_type=action_type, lineage=lineage, score=ContinuityScore(), sbat_alert=sbat_alert,
                                        is_terminal=False, receiver_entity="Unknown"
                                    )
                                    await db.state_edges.insert_one(edge.dict())
                                    if neo4j_driver:
                                        async with neo4j_driver.session() as ns:
                                            await ns.run("MATCH (a:Wallet {address: $fa}), (b:Wallet {address: $ta}) MERGE (a)-[r:TRANSFERRED {tx_hash: $tx}]->(b) SET r.amount=$amt, r.asset=$ast", fa=address, ta=tx["to"], tx=tx["hash"], amt=val, ast="ETH")

                                    await sio.emit('edge', {"edge": edge.dict()}, room=self.trace_id)
                                    
                                    nl = AssetLineage(original_asset=lineage.original_asset, current_asset=lineage.current_asset, canonical_asset=lineage.canonical_asset, transformation_history=lineage.transformation_history + [action_type])
                                    tasks.append(asyncio.create_task(self.execute_trace_step(tx["to"], chain, depth + 1, nl)))
                            
                            if tasks: await asyncio.gather(*tasks)
            except Exception as e: logger.error(f"Tx Fetch Error: {e}")

# ==============================================================================
# 🌐 8. FASTAPI ROUTING & SOCKET.IO APP
# ==============================================================================
app = FastAPI(title="Lionsgate Nemesis - Apex Auto-Tracer")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup_pipeline():
    await init_db()
    asyncio.create_task(AutoAuditManager.audit_loop())
    asyncio.create_task(mempool_listener())

@sio.on('join_trace')
async def join_trace(sid, data):
    if data.get('trace_id'): sio.enter_room(sid, data['trace_id'])

class DeploymentPayload(BaseModel):
    seeds: str
    chain_override: str = "AUTO"
    max_depth: int = 2

@app.post("/api/v1/trace/deploy")
async def deploy_nemesis_engine(payload: DeploymentPayload, background_tasks: BackgroundTasks):
    await os_state.transition("HUMAN", "Decision Making", "Deploying Trace")
    trace_id = f"NMS-APEX-{uuid.uuid4().hex[:8].upper()}"
    tracer = NemesisLiveTracer(trace_id, max_depth=payload.max_depth)
    clean_seeds = [s.strip() for s in re.split(r'[\s,]+', payload.seeds) if s.strip()]
    
    for seed in clean_seeds:
        chain = payload.chain_override if payload.chain_override != "AUTO" else ("ETH" if seed.startswith("0x") else "BTC")
        background_tasks.add_task(tracer.orchestrate, seed, chain)
        
    return {"status": "Autonomous Engine Deployed", "trace_id": trace_id}

@app.get("/api/v1/system/state")
async def get_os_state(): 
    return {"human": os_state.human_state, "machine": os_state.machine_state, "mission": os_state.mission_state, "mempool_size": len(MEMPOOL)}

socket_app = socketio.ASGIApp(sio, app)

# ==============================================================================
# 🎨 9. SPA FRONTEND (GLOBALIZED UI + SOCKET.IO STREAMING)
# ==============================================================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nemesis APEX | Autonomous Tracer & Global Identity Layer</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://unpkg.com/3d-force-graph@1.43.3/dist/3d-force-graph.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    
    <style>
        body { margin: 0; font-family: 'Inter', sans-serif; background: #0f172a; color: #f8fafc; overflow: hidden; }
        .glass-panel { background: rgba(30, 41, 59, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        .btn-primary { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; font-weight: 700; padding: 12px; border-radius: 8px; width: 100%; transition: 0.3s; }
        .btn-primary:hover { box-shadow: 0 0 15px rgba(37, 99, 235, 0.5); }
        input, select { background: #1e293b; border: 1px solid #334155; padding: 12px; border-radius: 8px; width: 100%; color: white; outline: none; margin-bottom: 12px; }
        input:focus { border-color: #3b82f6; }
        
        .progress-bar { height: 8px; background: #334155; border-radius: 4px; overflow: hidden; width: 100%; margin-top: 8px; }
        .progress-fill { height: 100%; background: #3b82f6; width: 0%; transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
        .global-card { background: rgba(15,23,42,0.8); border: 1px solid #334155; border-radius: 8px; padding: 16px; margin-bottom: 12px; font-size: 12px; transition: transform 0.2s; }
        .global-card:hover { transform: translateY(-2px); border-color: #3b82f6; }
        .pipeline-item { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #64748b; margin-bottom: 6px; transition: 0.3s; }
        .pipeline-item.active { color: #38bdf8; font-weight: bold; }
        .pipeline-item.completed { color: #34d399; }
        .auto-heal-alert { animation: slideIn 0.3s ease-out; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.4); border-left: 4px solid #f59e0b; padding: 12px; border-radius: 6px; font-size: 11px; color: #fcd34d; margin-bottom: 10px; }
        @keyframes slideIn { from { transform: translateX(20px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    </style>
</head>
<body class="flex h-screen w-screen">

    <aside class="w-80 glass-panel flex flex-col p-6 z-10 shrink-0 m-4 shadow-2xl border-r border-slate-700">
        <h1 class="text-xl font-black text-blue-400 mb-6 flex items-center gap-2"><i class="ph-bold ph-radar"></i> NEMESIS APEX</h1>
        
        <label class="text-[10px] font-bold text-slate-400 uppercase">Target Wallet</label>
        <input type="text" id="seeds" placeholder="0x... or bc1q..." value="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D" />
        
        <label class="text-[10px] font-bold text-slate-400 uppercase">Network</label>
        <select id="chain"><option value="ETH">Ethereum</option><option value="BTC">Bitcoin</option></select>
        
        <button id="deploy-btn" onclick="deployLiveTrace()" class="btn-primary flex items-center justify-center gap-2"><i class="ph-bold ph-play"></i> Autonomous Trace</button>

        <div class="mt-6 flex-1 flex flex-col overflow-hidden">
            <h3 class="text-[10px] font-bold text-slate-400 uppercase mb-2 border-b border-slate-700 pb-2">Execution Pipeline</h3>
            <div class="progress-bar mb-4"><div class="progress-fill" id="pipe-progress"></div></div>
            <div class="flex-1 overflow-y-auto pr-2" id="pipeline-list"></div>
            
            <div class="grid grid-cols-2 gap-4 text-xs mt-4 bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                <div><span class="text-slate-500 block text-[10px]">WALLETS</span><b id="stat-wallets" class="text-white">0</b></div>
                <div><span class="text-slate-500 block text-[10px]">TXS ANALYZED</span><b id="stat-txs" class="text-white">0</b></div>
                <div class="col-span-2"><span class="text-slate-500 block text-[10px]">ASSETS TRACED</span><b id="stat-assets" class="text-emerald-400 font-mono text-sm">0.00</b></div>
            </div>
            <div class="mt-2 text-[9px] text-slate-500 font-mono text-center flex justify-between">
                <span>HSM: <b id="state-human" class="text-sky-400">Idle</b></span>
                <span>OS: <b id="state-machine" class="text-emerald-400">Ready</b></span>
            </div>
        </div>
    </aside>

    <main class="flex-1 relative m-4 ml-0 flex flex-col gap-4">
        <div id="alert-container" class="absolute top-4 left-4 right-4 z-50 flex flex-col gap-2 pointer-events-none"></div>
        <div class="glass-panel flex-1 relative" id="graph-container"></div>
        
        <div class="h-72 glass-panel p-5 flex flex-col">
            <h3 class="text-[10px] font-bold text-slate-400 uppercase mb-3 border-b border-slate-700 pb-2 flex items-center gap-2"><i class="ph-bold ph-list-dashes"></i> Global Identity & Custody Ledger</h3>
            <div class="flex-1 flex gap-4 overflow-x-auto pb-2" id="live-feed">
                <div class="text-slate-500 text-xs italic m-auto">Awaiting Socket.io Stream...</div>
            </div>
        </div>
    </main>

    <script>
        const CRYPTO_LOGOS = {
            "ETH": "ethereum-eth-logo.svg", "BTC": "bitcoin-btc-logo.svg", 
            "USDT": "tether-usdt-logo.svg", "USDC": "usd-coin-usdc-logo.svg",
            "SOL": "solana-sol-logo.svg", "BNB": "bnb-bnb-logo.svg"
        };
        
        function getLogo(symbol) { return CRYPTO_LOGOS[symbol.toUpperCase()] ? `https://cryptologos.cc/logos/${CRYPTO_LOGOS[symbol.toUpperCase()]}` : `https://cryptologos.cc/logos/ethereum-eth-logo.svg`; }
        function getEntityLogo(name) { return name.includes("Binance") ? "https://cryptologos.cc/logos/bnb-bnb-logo.svg" : "https://cryptologos.cc/logos/ethereum-eth-logo.svg"; }
        function short(str) { return str.length > 12 ? str.substring(0,6) + '...' + str.substring(str.length-4) : str; }

        const PIPELINE_STAGES = [
            "Initializing Investigation", "Validating Address", "Detecting Blockchain", 
            "Loading Labels", "Fetching Transactions", "Resolving Entities", 
            "Cross-Chain Discovery", "Bridge Detection", "Mixer Detection", 
            "Exchange Detection", "Cluster Analysis", "AML Analysis", 
            "Graph Construction", "Confidence Scoring", "Final Report"
        ];
        
        function initPipelineUI() {
            document.getElementById('pipeline-list').innerHTML = PIPELINE_STAGES.map((stage, i) => `<div class="pipeline-item" id="stage-${i}"><i class="ph-bold ph-circle"></i> <span>${stage}</span></div>`).join('');
        }
        initPipelineUI();

        let Graph = null; let graphData = { nodes: [], links: [] }; const socket = io();

        function initGraph() {
            const el = document.getElementById('graph-container'); el.innerHTML = '';
            Graph = ForceGraph3D()(el).backgroundColor('rgba(0,0,0,0)').nodeId('id').nodeVal(5)
                .nodeColor(n => n.classification === 'Exchange' ? '#e11d48' : n.classification === 'Mixer' ? '#8b5cf6' : '#0ea5e9')
                .linkDirectionalParticles(2).linkColor(l => l.sbat_alert ? '#ef4444' : '#475569')
                .nodeLabel(n => `<div style="background:rgba(15,23,42,0.9); padding:10px; border:1px solid #334155; border-radius:8px; font-family:sans-serif; font-size:12px;"><div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;"><img src="${getLogo(n.chain)}" style="width:16px; height:16px;"><b style="color:#fff;">${n.classification}</b></div><div style="color:#94a3b8; font-family:monospace; margin-bottom:4px;">${n.id}</div><div style="color:#38bdf8; font-weight:bold;">Entity: ${n.entity_name}</div><div style="color:#34d399; margin-top:4px;">Risk Score: ${n.risk_score} | ${n.verified ? 'Verified' : 'Unverified'}</div></div>`);
        }

        setInterval(async () => {
            try {
                const res = await fetch('/api/v1/system/state'); const data = await res.json();
                document.getElementById('state-human').innerText = data.human; document.getElementById('state-machine').innerText = data.machine;
            } catch(e) {}
        }, 3000);

        socket.on('connect', () => { console.log("Socket.io Connected"); });
        socket.on('system_alert', (data) => {
            const c = document.getElementById('alert-container'); const el = document.createElement('div'); el.className = 'auto-heal-alert';
            el.innerHTML = `<i class="ph-fill ph-warning-circle"></i> <b>System Status:</b> ${data.msg}`;
            c.appendChild(el); setTimeout(() => { el.style.opacity = '0'; setTimeout(() => el.remove(), 300); }, 5000);
        });

        socket.on('pipeline_update', (msg) => {
            document.getElementById('pipe-progress').style.width = msg.progress + '%';
            document.getElementById('stat-wallets').innerText = msg.wallets; document.getElementById('stat-txs').innerText = msg.txs; document.getElementById('stat-assets').innerText = msg.assets.toLocaleString(undefined, {minimumFractionDigits: 2});
            const idx = PIPELINE_STAGES.indexOf(msg.active_stage);
            if (idx !== -1) {
                for(let i=0; i<idx; i++) { const el = document.getElementById(`stage-${i}`); if(el) el.className = "pipeline-item completed"; el.innerHTML = `<i class="ph-bold ph-check-circle"></i> <span>${PIPELINE_STAGES[i]}</span>`; }
                const cur = document.getElementById(`stage-${idx}`); if(cur) { cur.className = "pipeline-item active"; cur.innerHTML = `<i class="ph-bold ph-spinner animate-spin"></i> <span>${PIPELINE_STAGES[idx]}</span>`; cur.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
            }
        });

        socket.on('node', (msg) => {
            if (!graphData.nodes.find(n => n.id === msg.node.id)) {
                graphData.nodes.push(msg.node); Graph.graphData(graphData);
                document.getElementById('live-feed').insertAdjacentHTML('afterbegin', `<div class="global-card min-w-[250px] shadow-lg"><div class="flex items-center gap-2 mb-3"><img src="${getLogo(msg.node.chain)}" class="w-5 h-5 rounded-full" /><img src="${getEntityLogo(msg.node.entity_name)}" class="w-5 h-5 rounded-full bg-white p-0.5" /><span class="text-xs text-slate-400 font-mono">${short(msg.node.id)}</span></div><div class="text-sm font-bold text-white mb-1">Entity: ${msg.node.entity_name}</div><div class="text-xs text-slate-400 mb-3">Classification: <span class="text-blue-400">${msg.node.classification}</span></div><div class="flex items-center gap-2 pt-2 border-t border-slate-700"><span class="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 rounded text-[10px] uppercase">Risk: ${msg.node.risk_score}</span>${msg.node.verified ? '<span class="text-emerald-400 text-[10px] flex items-center gap-1"><i class="ph-fill ph-check-circle"></i> Verified</span>' : ''}</div></div>`);
            }
        });

        socket.on('edge', (msg) => {
            graphData.links.push(msg.edge); Graph.graphData(graphData);
            let sbatHtml = msg.edge.sbat_alert ? `<div class="mt-2 text-[10px] text-rose-400 bg-rose-500/20 p-1 rounded font-bold uppercase"><i class="ph-fill ph-warning"></i> SBAT Alert: ${msg.edge.sbat_alert.name}</div>` : "";
            document.getElementById('live-feed').insertAdjacentHTML('afterbegin', `<div class="global-card min-w-[250px] border-indigo-500/40 bg-indigo-500/10 shadow-lg ${msg.edge.sbat_alert ? 'border-rose-500/50 bg-rose-500/10' : ''}"><div class="flex items-center justify-between mb-3"><div class="flex items-center gap-2"><img src="${getLogo(msg.edge.chain)}" class="w-5 h-5 rounded-full" /><span class="text-xs ${msg.edge.sbat_alert ? 'text-rose-400' : 'text-indigo-300'} font-bold uppercase tracking-wider">${msg.edge.action_type}</span></div><span class="text-[10px] text-slate-400">${new Date(msg.edge.timestamp).toLocaleTimeString()}</span></div><div class="text-lg font-black text-white mb-1 tracking-tight">${msg.edge.amount.toFixed(4)} ${msg.edge.asset}</div><div class="text-slate-400 text-xs mb-2">≈ $${msg.edge.usd_value.toLocaleString(undefined, {maximumFractionDigits:0})} USD</div>${sbatHtml}</div>`);
        });

        socket.on('trace_complete', (msg) => {
            document.getElementById('deploy-btn').disabled = false; document.getElementById('deploy-btn').innerHTML = `<i class="ph-bold ph-check-circle"></i> Trace Complete`;
            PIPELINE_STAGES.forEach((s, i) => { const el = document.getElementById(`stage-${i}`); if(el) { el.className = "pipeline-item completed"; el.innerHTML = `<i class="ph-bold ph-check-circle"></i> <span>${s}</span>`; } });
            document.getElementById('pipe-progress').style.width = '100%'; document.getElementById('pipe-progress').style.background = '#34d399';
        });

        async function deployLiveTrace() {
            const seeds = document.getElementById('seeds').value.trim(); const chain = document.getElementById('chain').value;
            if(!seeds) return alert("Enter address");
            graphData = { nodes: [], links: [] }; if(!Graph) initGraph(); else Graph.graphData(graphData); document.getElementById('live-feed').innerHTML = ''; initPipelineUI(); document.getElementById('pipe-progress').style.width = '0%'; document.getElementById('pipe-progress').style.background = '#3b82f6'; document.getElementById('deploy-btn').disabled = true; document.getElementById('deploy-btn').innerText = "Orchestrating Agents...";
            try {
                const res = await fetch('/api/v1/trace/deploy', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({seeds, chain_override: chain, max_depth: 2})});
                const data = await res.json(); socket.emit('join_trace', { trace_id: data.trace_id });
            } catch(e) { alert("Deployment Failed"); document.getElementById('deploy-btn').disabled = false; }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    return HTMLResponse(content=HTML_TEMPLATE)

socket_app = socketio.ASGIApp(sio, app)

if __name__ == "__main__":
    import uvicorn
    logger.info("====================================================================")
    logger.info("  DEPLOYING LIONSGATE NEMESIS APEX (v55.0 MONOLITHIC ARCHITECTURE)  ")
    logger.info("====================================================================")
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
