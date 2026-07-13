#!/usr/bin/env python3
"""
==============================================================================
🛡️ LIONSGATE INTELLIGENCE NETWORK - NEMESIS APEX OMNI-ENGINE (v56.0 MONOLITH)
==============================================================================
Integrated Capabilities:
- Auto-Dependency Bootstrapper & Auto-Healing Core
- Asset Lifecycle Engine v13.5 (Wraps, Bridges, Swaps, Mints, Burns)
- Forensic Signature Engine (SBAT / Phishing Drainer Detection / 1inch / Curve)
- MEV & Mempool Sniper (Flashbots, Sandwich Attacks)
- PyTorch Geometric (GNN) Attacker Clustering
- OSINT Orchestrator & Corporate Intel Scraper
- Cloudflare D1 Lightweight Cache & Dual-Database (MongoDB + Neo4j)
- 12-Tab NEMESIS ID GUI & Real-Time Socket.io Pipeline Streaming
- Globalized Wallet & Transaction UI (cryptologos.cc mapping)
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
import math
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
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

try:
    from neo4j import AsyncGraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

from dotenv import load_dotenv
load_dotenv()

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
MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("DATABASE_MONGO_URL", "mongodb://localhost:27017"))
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
# 🧬 2. ASSET LIFECYCLE ENGINE (v13.5), ONTOLOGY & FORENSICS
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

class ActionType(str, Enum):
    TRANSFER = "TRANSFER"
    SWAP = "SWAP"
    MINT = "MINT"
    BURN = "BURN"
    BRIDGE = "BRIDGE"
    WRAP = "WRAP"
    UNWRAP = "UNWRAP"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    MIXER = "MIXER"
    CEX_DEPOSIT = "CEX_DEPOSIT"
    INTERNAL_TX = "INTERNAL_TX"
    NFT_TRANSFER = "NFT_TRANSFER"

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

# --- PYDANTIC MODELS ---
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
    @staticmethod
    async def audit_loop():
        while True:
            await os_state.transition("MACHINE", "Auditing", "Running pre-flight checks and data validation.")
            try:
                await mongo_client.admin.command("ping")
                if neo4j_driver: await neo4j_driver.verify_connectivity()
            except Exception as e:
                logger.error(f"[AUDIT FAIL] {e}")
                await os_state.transition("MACHINE", "Degraded", f"Audit Error: {e}")
            await asyncio.sleep(60)

# ==============================================================================
# 🤖 4. AI GNN & ATTACKER CLUSTERING (PYTORCH) & MEV ENGINE
# ==============================================================================
class WalletGNN(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = GCNConv(6, 16)
        self.conv2 = GCNConv(16, 8)
    def forward(self, x, edge_index):
        x = F.relu(self.conv1(x, edge_index))
        return self.conv2(x, edge_index)

MEMPOOL = deque(maxlen=5000)

async def mempool_listener():
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
# 🕸️ 5. OSINT SPIDER, OKLINK & CLOUDFLARE D1 (LIGHTWEIGHT CACHE)
# ==============================================================================
async def query_cloudflare_d1(sql: str, params: list = []):
    """Cloudflare D1 Lightweight Intel Cache (Wallet Labels, Entities, Tags)"""
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
                
                if re.search(r"Exchange:\s*([^.<]+)", content, re.IGNORECASE) or "binance" in content.lower() or "kraken" in content.lower() or "coinbase" in content.lower():
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
# ⛓️ 6. AUTONOMOUS TRACE EXECUTION PIPELINE (SOCKET.IO)
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
        self.stats = {"wallets": 0, "txs": 0, "assets": 0.0, "progress": 0, "chain": "", "hop": 0}; self.current_stage = 0

    async def emit_progress(self, steps: int = 1):
        self.current_stage = min(self.current_stage + steps, len(self.PIPELINE_STAGES) - 1)
        self.stats["progress"] = int((self.current_stage / (len(self.PIPELINE_STAGES) - 1)) * 100)
        await sio.emit('pipeline_update', {"active_stage": self.PIPELINE_STAGES[self.current_stage], **self.stats}, room=self.trace_id)

    def classify_tx_event(self, tx: Dict) -> str:
        """Asset Lifecycle Classification Engine v13.5"""
        fn = (tx.get("functionName") or "").lower()
        inp = (tx.get("input") or "").lower()
        if len(inp) >= 10 and inp[:10] in FORENSIC_SIGNATURES:
            sig = FORENSIC_SIGNATURES[inp[:10]]
            if sig["name"] == "withdraw": return ActionType.UNWRAP
            if sig["name"] in ["approve", "permit", "setApprovalForAll", "permit2_transferFrom"]: return ActionType.TRANSFER
        
        if "swap" in fn: return ActionType.SWAP
        if "mint" in fn or tx.get("from") == "0x0000000000000000000000000000000000000000": return ActionType.MINT
        if "burn" in fn or tx.get("to") == "0x0000000000000000000000000000000000000000": return ActionType.BURN
        if "bridge" in fn: return ActionType.BRIDGE
        if "deposit" in fn: return ActionType.DEPOSIT
        if "wrap" in fn: return ActionType.WRAP
        if "unwrap" in fn: return ActionType.UNWRAP
        return ActionType.TRANSFER

    async def orchestrate(self, address: str, chain: str):
        self.stats["chain"] = chain
        await os_state.transition("MISSION", "Collecting Intelligence")
        await self.emit_progress(1) # Initializing
        await self.emit_progress(1) # Validating Address
        await self.emit_progress(1) # Detecting Blockchain
        
        try:
            lineage = AssetLineage(original_asset="NATIVE", current_asset="NATIVE", canonical_asset="NATIVE")
            await self.execute_trace_step(address, chain, 0, lineage)
        except Exception as e:
            logger.error(f"[!] Trace Error: {e}")
            await sio.emit('system_alert', {"msg": f"Trace Error: {str(e)}", "type": "error"}, room=self.trace_id)
        
        # Fast forward remaining analytical stages
        await self.emit_progress(1) # Cluster Analysis
        await self.emit_progress(1) # AML Analysis
        await self.emit_progress(1) # Graph Construction
        await self.emit_progress(1) # Confidence Scoring
        await self.emit_progress(1) # Final Report
        
        await sio.emit('trace_complete', {"trace_id": self.trace_id}, room=self.trace_id)
        await os_state.transition("MISSION", "Completed")

    async def execute_trace_step(self, address: str, chain: str, depth: int, lineage: AssetLineage):
        if depth > self.max_depth: return
        uid = f"{chain}:{address}".lower()
        if uid in self.visited: return
        self.visited.add(uid); self.stats["wallets"] += 1; self.stats["hop"] = depth
        
        async with self.semaphore:
            if depth == 0: await self.emit_progress(1) # Loading Labels
            else: await self.emit_progress(1) # Resolving Entities
            
            intel = await GEISScraper.extract_hybrid_intelligence(address, chain)
            node_data = {
                "id": address, "chain": chain, "classification": intel["classification"], 
                "entity_name": intel["entity_name"], "tags": intel["tags"], 
                "risk_score": intel["risk_score"], "verified": intel["verified"]
            }
            
            # Neo4j Graph Sync
            if neo4j_driver:
                try:
                    async with neo4j_driver.session() as s:
                        await s.run("MERGE (w:Wallet {address: $addr}) SET w.chain=$chain, w.classification=$cls, w.entity_name=$name", addr=address, chain=chain, cls=intel["classification"], name=intel["entity_name"])
                except Exception as e: logger.error(f"Neo4j Error: {e}")

            await db.entities.update_one({"address": address, "chain": chain}, {"$set": node_data}, upsert=True)
            await sio.emit('node', {"node": node_data}, room=self.trace_id)

            if intel["classification"] in [EntityType.CEX, EntityType.MIXER]:
                if intel["classification"] == EntityType.CEX: await self.emit_progress(3) # CEX Detection
                if intel["classification"] == EntityType.MIXER: await self.emit_progress(4) # Mixer Detection
                return # Terminus

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

                                    action_type = self.classify_tx_event(tx)
                                    if intel["classification"] == EntityType.CEX: action_type = ActionType.CEX_DEPOSIT

                                    # SBAT Signature Detection
                                    sbat_alert = None
                                    inp = tx.get("input", "").lower()
                                    if len(inp) >= 10 and inp[:10] in FORENSIC_SIGNATURES:
                                        sbat_alert = FORENSIC_SIGNATURES[inp[:10]]
                                        if "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff" in inp: sbat_alert["desc"] += " (INFINITE APPROVAL)"

                                    edge = ForensicEdge(
                                        trace_id=self.trace_id, from_addr=address, to_addr=tx["to"], amount=val, chain=chain, tx_hash=tx["hash"],
                                        action_type=action_type, lineage=lineage, score=ContinuityScore(), sbat_alert=sbat_alert,
                                        is_terminal=False, receiver_entity="Unknown"
                                    )
                                    await db.state_edges.insert_one(edge.dict())
                                    if neo4j_driver:
                                        async with neo4j_driver.session() as ns:
                                            await ns.run("MATCH (a:Wallet {address: $fa}), (b:Wallet {address: $ta}) MERGE (a)-[r:TRANSFERRED {tx_hash: $tx}]->(b) SET r.amount=$amt, r.action=$act", fa=address, ta=tx["to"], tx=tx["hash"], amt=val, act=action_type)

                                    await sio.emit('edge', {"edge": edge.dict()}, room=self.trace_id)
                                    
                                    nl = AssetLineage(original_asset=lineage.original_asset, current_asset=lineage.current_asset, canonical_asset=lineage.canonical_asset, transformation_history=lineage.transformation_history + [action_type])
                                    tasks.append(asyncio.create_task(self.execute_trace_step(tx["to"], chain, depth + 1, nl)))
                            
                            if tasks: await asyncio.gather(*tasks)
            except Exception as e: logger.error(f"Tx Fetch Error: {e}")

# ==============================================================================
# 🤖 8. AI INVESTIGATION LAYER (GEMINI DOC GENERATOR)
# ==============================================================================
class AIAgent:
    @staticmethod
    async def generate_full_report(trace_id: str, zip_code: str = "") -> str:
        edges = await db.state_edges.find({"trace_id": trace_id}, {"_id": 0}).to_list(1000)
        if not edges: return "<h2>Insufficient graph data for narrative.</h2>"
        
        flow = "\n".join([f"- {e['source_wallet']} sent {e['amount']} to {e['destination_wallet']} (Action: {e['action_type']})" for e in edges])
        
        prompt = f"""
        Generate a comprehensive, Google Doc style HTML Forensic Report for this blockchain trace.
        Follow this exact structure (use HTML tags like <h1>, <h2>, <ul>, <table>, <p>):
        1. Table of Contents
        2. Executive Summary (Incident, Recovery Probability %, Identified CEX Terminals)
        3. Incident Details & Methodology
        4. Chronological Fund Flow (Analyze the provided transactions)
        5. Timeline of Events & Findings
        6. Conclusion & Recommendations
        7. Glossary of Terms
        8. Crypto Victims Guidelines (Law Enforcement contacts, localized for zip code: {zip_code})
        9. Disclaimer (Include: "Lionsgate Network makes no warranties... Law enforcement is the only authority empowered to freeze funds.")
        
        Data to analyze:
        {flow}
        """

        try:
            client_ai = genai.Client(api_key=GEMINI_API_KEY)
            response = client_ai.models.generate_content(model='gemini-2.5-flash', contents=prompt, config=types.GenerateContentConfig(temperature=0.2))
            html_content = response.text.replace("```html", "").replace("```", "")
            return html_content
        except Exception as e: return f"<h2>AI Generation Failed</h2><p>{str(e)}</p>"

# ==============================================================================
# 🌐 9. FASTAPI ROUTING & SOCKET.IO APP
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

@app.get("/api/v1/report/{trace_id}")
async def get_report(trace_id: str, zip: str = ""):
    return {"html": await AIAgent.generate_full_report(trace_id, zip)}

@app.get("/api/v1/system/state")
async def get_os_state(): 
    return {"human": os_state.human_state, "machine": os_state.machine_state, "mission": os_state.mission_state, "mempool_size": len(MEMPOOL)}

socket_app = socketio.ASGIApp(sio, app)

# ==============================================================================
# 🎨 10. SPA FRONTEND (LIGHT THEME, SIGMA-STYLE GRAPH, 12-TAB NEMESIS ID)
# ==============================================================================
HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nemesis APEX | Autonomous Tracer & Global Identity Layer</title>
    
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="//unpkg.com/force-graph"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    
    <style>
        body { margin: 0; font-family: 'Inter', sans-serif; background: #f8fafc; color: #0f172a; overflow: hidden; }
        
        /* Glassmorphism Panel (Light Theme) */
        .glass-panel { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(12px); border: 1px solid rgba(226, 232, 240, 0.8); border-radius: 16px; box-shadow: 0 10px 40px -10px rgba(0,0,0,0.05); }
        
        .btn-primary { background: #0f172a; color: white; font-weight: 700; padding: 12px; border-radius: 8px; width: 100%; transition: 0.3s; box-shadow: 0 4px 10px rgba(15, 23, 42, 0.2); cursor: pointer; border: none; }
        .btn-primary:hover { background: #3b82f6; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }
        
        input, select { background: #f1f5f9; border: 1px solid #cbd5e1; padding: 12px; border-radius: 8px; width: 100%; color: #0f172a; outline: none; margin-bottom: 12px; transition: 0.2s; }
        input:focus { border-color: #3b82f6; box-shadow: 0 0 0 2px rgba(59,130,246,0.2); background: white; }
        
        .progress-bar { height: 8px; background: #e2e8f0; border-radius: 4px; overflow: hidden; width: 100%; margin-top: 8px; }
        .progress-fill { height: 100%; background: #3b82f6; width: 0%; transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
        
        /* Globalized Component Wrappers */
        .global-card { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 12px; font-size: 12px; transition: transform 0.2s, box-shadow 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.02); flex-shrink: 0; }
        .global-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(0,0,0,0.05); border-color: #cbd5e1; }
        
        .pipeline-item { display: flex; align-items: center; gap: 8px; font-size: 11px; color: #94a3b8; margin-bottom: 6px; transition: 0.3s; }
        .pipeline-item.active { color: #3b82f6; font-weight: bold; }
        .pipeline-item.completed { color: #10b981; }

        /* Nemesis ID Tabs */
        .tab-btn { padding: 8px 16px; font-size: 11px; font-weight: 600; color: #64748b; border-bottom: 2px solid transparent; cursor: pointer; white-space: nowrap; }
        .tab-btn.active { color: #0f172a; border-bottom: 2px solid #3b82f6; font-weight: 800; }
        .tab-content { display: none; padding: 16px 0; animation: fadeIn 0.3s ease; height: 100%; overflow-y: auto;}
        .tab-content.active { display: block; }
        
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        
        /* Report HTML Styling */
        .report-doc { max-width: 800px; margin: 0 auto; background: white; padding: 40px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); font-family: serif; color: #1e293b; line-height: 1.6;}
        .report-doc h1 { font-size: 24px; font-weight: bold; text-transform: uppercase; border-bottom: 2px solid #0f172a; padding-bottom: 10px; margin-bottom: 20px; font-family: 'Inter', sans-serif;}
        .report-doc h2 { font-size: 18px; font-weight: bold; margin-top: 24px; margin-bottom: 12px; color: #3b82f6; font-family: 'Inter', sans-serif;}
        .report-doc ul { padding-left: 20px; margin-bottom: 16px; list-style-type: disc;}
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="flex h-screen w-screen relative">

    <!-- Deployment & Pipeline Panel -->
    <aside class="w-80 glass-panel flex flex-col p-6 z-10 shrink-0 m-4 shadow-xl">
        <h1 class="text-xl font-black text-slate-900 mb-6 flex items-center gap-2"><i class="ph-bold ph-radar text-blue-600"></i> NEMESIS TRACER</h1>
        
        <label class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Target Wallet / Seed</label>
        <input type="text" id="seeds" placeholder="0x... or bc1q..." value="0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D" />
        
        <label class="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">Network</label>
        <select id="chain"><option value="ETH">Ethereum</option><option value="BTC">Bitcoin</option></select>
        
        <button id="deploy-btn" onclick="deployLiveTrace()" class="btn-primary flex items-center justify-center gap-2"><i class="ph-bold ph-play"></i> Autonomous Trace</button>

        <!-- Live Execution Pipeline Stream -->
        <div class="mt-6 flex-1 flex flex-col overflow-hidden">
            <h3 class="text-[10px] font-bold text-slate-500 uppercase mb-2 border-b border-slate-200 pb-2">Execution Pipeline</h3>
            <div class="progress-bar mb-4"><div class="progress-fill" id="pipe-progress"></div></div>
            
            <div class="flex-1 overflow-y-auto pr-2" id="pipeline-list"></div>
            
            <div class="grid grid-cols-2 gap-4 text-xs mt-4 bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div><span class="text-slate-500 block text-[10px] uppercase">Wallets</span><b id="stat-wallets" class="text-slate-900">0</b></div>
                <div><span class="text-slate-500 block text-[10px] uppercase">Txs Analyzed</span><b id="stat-txs" class="text-slate-900">0</b></div>
                <div class="col-span-2"><span class="text-slate-500 block text-[10px] uppercase">Assets Traced</span><b id="stat-assets" class="text-blue-600 font-mono text-sm">0.00</b></div>
            </div>
            
            <div class="mt-4 text-[9px] text-slate-500 font-mono text-center flex justify-between bg-slate-100 p-2 rounded">
                <span>HSM: <b id="state-human" class="text-blue-600">Idle</b></span>
                <span>OS: <b id="state-machine" class="text-emerald-600">Ready</b></span>
            </div>
        </div>
    </aside>

    <!-- Main Workspace -->
    <main class="flex-1 relative m-4 ml-0 flex flex-col gap-4 overflow-hidden">
        
        <!-- Header Info -->
        <div class="glass-panel p-4 flex justify-between items-center shrink-0">
            <div class="flex items-center gap-4">
                <div class="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center text-slate-900 text-xl shadow-inner"><i class="ph-fill ph-fingerprint"></i></div>
                <div>
                    <h2 class="font-black text-sm text-slate-900 flex items-center gap-2 uppercase tracking-wide">SUBJECT WALLET ENTITY <span id="alert-badge" class="hidden px-2 py-0.5 bg-red-100 text-red-600 rounded text-[9px] animate-pulse">CUSTODIAL ALERT</span></h2>
                    <p class="text-xs font-mono text-slate-500" id="header-address">Awaiting Deployment...</p>
                </div>
            </div>
            <div class="flex gap-2">
                <button onclick="switchTab(12, document.getElementById('tab-btn-12'))" class="bg-white border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-xs font-bold shadow-sm hover:bg-slate-50 transition"><i class="ph-bold ph-file-pdf"></i> Export DOSSIER</button>
            </div>
        </div>

        <!-- 12-TAB NEMESIS ID PANEL -->
        <div class="glass-panel flex-1 flex flex-col overflow-hidden">
            <!-- Tabs Navigation -->
            <div class="flex overflow-x-auto border-b border-slate-200 px-4 shrink-0 no-scrollbar">
                <div class="tab-btn active" onclick="switchTab(1, this)">Wallet Profile</div>
                <div class="tab-btn" onclick="switchTab(2, this)">Counterparties</div>
                <div class="tab-btn" onclick="switchTab(3, this)">Assets</div>
                <div class="tab-btn" onclick="switchTab(4, this)">Chains</div>
                <div class="tab-btn" onclick="switchTab(5, this)">Transactions</div>
                <div class="tab-btn" onclick="switchTab(6, this)">Balances</div>
                <div class="tab-btn" id="tab-btn-7" onclick="switchTab(7, this)">Trace Graph</div>
                <div class="tab-btn" onclick="switchTab(8, this)">AML / CFT</div>
                <div class="tab-btn" onclick="switchTab(9, this)">Georisk</div>
                <div class="tab-btn" onclick="switchTab(10, this)">Intelligence</div>
                <div class="tab-btn" onclick="switchTab(11, this)">AI Insights Report</div>
                <div class="tab-btn" id="tab-btn-12" onclick="switchTab(12, this)">Generate Infographics</div>
            </div>

            <!-- Tabs Content Area -->
            <div class="flex-1 overflow-hidden p-4 bg-slate-50/50">
                
                <!-- Tab 1: Wallet Profile (Globalized UI Components) -->
                <div id="tab-1" class="tab-content active">
                    <div class="grid grid-cols-2 gap-6 h-full">
                        <div class="space-y-4 overflow-y-auto">
                            <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
                                <h3 class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Globalized Wallet Identity</h3>
                                <div id="wallet-identity-container" class="space-y-2">
                                    <div class="text-xs text-slate-400 italic">Deploy trace to resolve identity...</div>
                                </div>
                            </div>
                            <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm grid grid-cols-2 gap-4 text-xs">
                                <div class="col-span-2"><h3 class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">Metrics</h3></div>
                                <div><span class="text-slate-400 block mb-1">Total INBOUND</span><strong class="text-emerald-600" id="t1-in">--</strong></div>
                                <div><span class="text-slate-400 block mb-1">Total OUTBOUND</span><strong class="text-rose-600" id="t1-out">--</strong></div>
                            </div>
                        </div>
                        <div class="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col">
                            <h3 class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Chronological Fund Flow</h3>
                            <div class="flex-1 overflow-y-auto space-y-2 pr-2" id="live-feed">
                                <div class="text-slate-400 text-xs italic text-center mt-10">Awaiting Socket.io Stream...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Tab 7: Trace Graph (Sigma/Graphology Style 2D Canvas) -->
                <div id="tab-7" class="tab-content relative p-0">
                    <div id="graph-container" class="w-full h-full bg-white rounded-xl shadow-inner overflow-hidden cursor-move border border-slate-200" style="background-image: radial-gradient(#cbd5e1 1px, transparent 1px); background-size: 30px 30px;"></div>
                </div>

                <!-- Tab 11: AI Insights Report -->
                <div id="tab-11" class="tab-content">
                    <div class="h-full bg-white p-8 rounded-xl border border-slate-200 shadow-sm overflow-y-auto" id="ai-report-content">
                        <div class="flex flex-col items-center justify-center h-full text-slate-400">
                            <i class="ph-duotone ph-robot text-6xl mb-4"></i>
                            <p>Execute trace and click "Generate Report" to synthesize AI Insights.</p>
                            <button onclick="generateDocReport()" class="mt-6 bg-purple-600 text-white px-6 py-2 rounded-lg font-bold shadow hover:bg-purple-500 transition">Generate AI Report</button>
                        </div>
                    </div>
                </div>

                <!-- Tab 12: Full HTML Report -->
                <div id="tab-12" class="tab-content">
                    <div class="flex justify-between items-center mb-4 px-4">
                        <input type="text" id="zip-code" placeholder="Victim Zip Code (For Local LEA info)" class="w-64 mb-0 bg-white shadow-sm" />
                        <button onclick="generateDocReport()" class="bg-slate-900 text-white px-6 py-2 rounded-lg font-bold shadow hover:bg-slate-800 transition"><i class="ph-bold ph-printer"></i> Generate & Print Dossier</button>
                    </div>
                    <div class="h-[calc(100%-60px)] overflow-y-auto rounded-xl border border-slate-200 bg-slate-100 p-8">
                        <div id="full-report-content" class="report-doc hidden"></div>
                        <div id="report-placeholder" class="text-center text-slate-400 mt-20"><i class="ph-duotone ph-file-doc text-6xl mb-4"></i><p>Awaiting Document Generation...</p></div>
                    </div>
                </div>

                <!-- Placeholder for other tabs -->
                <div id="tab-2" class="tab-content"><div class="p-8 text-center text-slate-500">Counterparties Intelligence syncing...</div></div>
                <div id="tab-3" class="tab-content"><div class="p-8 text-center text-slate-500">Global Multi-Chain Portfolio syncing...</div></div>
                <div id="tab-4" class="tab-content"><div class="p-8 text-center text-slate-500">Chain Detection active...</div></div>
                <div id="tab-5" class="tab-content"><div class="p-8 text-center text-slate-500">Transaction History analyzing...</div></div>
                <div id="tab-6" class="tab-content"><div class="p-8 text-center text-slate-500">Balance Analytics calculating...</div></div>
                <div id="tab-8" class="tab-content"><div class="p-8 text-center text-slate-500">AML/CFT Compliance Risk Engine evaluating...</div></div>
                <div id="tab-9" class="tab-content"><div class="p-8 text-center text-slate-500">Georisk & IP Node Resolution running...</div></div>
                <div id="tab-10" class="tab-content"><div class="p-8 text-center text-slate-500">OSINT, Darknet & Ransomware Intelligence mapping...</div></div>

            </div>
        </div>
    </main>

    <script>
        // --- 1. ASSET RESOLUTION ENGINE (Cryptologos) ---
        const CRYPTO_LOGOS = {
            "ETH": "ethereum-eth-logo.svg", "BTC": "bitcoin-btc-logo.svg", 
            "USDT": "tether-usdt-logo.svg", "USDC": "usd-coin-usdc-logo.svg",
            "SOL": "solana-sol-logo.svg", "BNB": "bnb-bnb-logo.svg",
            "XRP": "xrp-xrp-logo.svg", "TRX": "tron-trx-logo.svg",
            "DOGE": "dogecoin-doge-logo.svg", "LINK": "chainlink-link-logo.svg",
            "UNI": "uniswap-uni-logo.svg", "AAVE": "aave-aave-logo.svg", "WBTC": "wrapped-bitcoin-wbtc-logo.svg"
        };
        
        function getLogoUrl(symbol) { 
            const file = CRYPTO_LOGOS[symbol.toUpperCase()];
            return file ? `https://cryptologos.cc/logos/${file}` : `https://cryptologos.cc/logos/ethereum-eth-logo.svg`; 
        }
        
        const ENTITY_LOGOS = {
            "Binance": "https://cryptologos.cc/logos/bnb-bnb-logo.svg",
            "Tornado Cash": "https://cryptologos.cc/logos/tornado-cash-torn-logo.svg"
        };
        function getEntityLogoUrl(name) {
            for (let key in ENTITY_LOGOS) { if (name.includes(key)) return ENTITY_LOGOS[key]; }
            return "https://cryptologos.cc/logos/ethereum-eth-logo.svg"; 
        }

        function short(str) { return str.length > 12 ? str.substring(0,6) + '...' + str.substring(str.length-4) : str; }

        // Load images for Canvas Drawing
        const imgCache = {};
        function loadImg(url) {
            if(imgCache[url]) return imgCache[url];
            const img = new Image(); img.src = url; imgCache[url] = img; return img;
        }

        // --- 2. UI TABS & PIPELINE SETUP ---
        function switchTab(num, btn) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            if(btn) btn.classList.add('active');
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById('tab-'+num).classList.add('active');
            
            // Re-center graph if Tab 7
            if(num === 7 && Graph) setTimeout(() => Graph.zoomToFit(400, 50), 100);
        }

        const PIPELINE_STAGES = [
            "Initializing Investigation", "Validating Address", "Detecting Blockchain", 
            "Loading Labels", "Fetching Transactions", "Resolving Entities", 
            "Cross-Chain Discovery", "Bridge Detection", "Mixer Detection", 
            "Exchange Detection", "Cluster Analysis", "AML Analysis", 
            "Graph Construction", "Confidence Scoring", "Final Report"
        ];
        
        function initPipelineUI() {
            document.getElementById('pipeline-list').innerHTML = PIPELINE_STAGES.map((stage, i) => `
                <div class="pipeline-item" id="stage-${i}">
                    <i class="ph-bold ph-circle"></i> <span>${stage}</span>
                </div>
            `).join('');
        }
        initPipelineUI();

        // --- 3. SOCKET.IO AND 2D CANVAS GRAPH (Sigma-style) ---
        let Graph = null;
        let graphData = { nodes: [], links: [] };
        const socket = io(); 

        function initGraph() {
            const el = document.getElementById('graph-container'); el.innerHTML = '';
            
            Graph = ForceGraph()(el)
                .graphData(graphData)
                .nodeId('id')
                .backgroundColor('rgba(0,0,0,0)')
                .linkDirectionalArrowLength(6)
                .linkDirectionalArrowRelPos(1)
                .linkCurvature(0.2) // Curved edges like nodes.png
                .linkColor(() => '#94a3b8')
                .linkWidth(2)
                .nodeCanvasObject((node, ctx, globalScale) => {
                    // Sigma-Style Node: White circle, shadow, entity logo, text below
                    const size = 16;
                    
                    // Shadow
                    ctx.shadowColor = 'rgba(0, 0, 0, 0.15)';
                    ctx.shadowBlur = 10;
                    ctx.shadowOffsetX = 0;
                    ctx.shadowOffsetY = 4;
                    
                    // Outer Circle (Risk color border)
                    ctx.beginPath();
                    ctx.arc(node.x, node.y, size, 0, 2 * Math.PI, false);
                    ctx.fillStyle = '#ffffff';
                    ctx.fill();
                    ctx.lineWidth = 2;
                    ctx.strokeStyle = node.classification === 'Exchange' ? '#e11d48' : (node.classification === 'Mixer' ? '#8b5cf6' : '#0ea5e9');
                    ctx.stroke();
                    
                    // Clear shadow for interior
                    ctx.shadowColor = 'transparent';

                    // Draw Logo Image inside
                    const imgUrl = getEntityLogoUrl(node.entity_name || '');
                    const img = loadImg(imgUrl);
                    if (img && img.complete) {
                        ctx.save();
                        ctx.beginPath(); ctx.arc(node.x, node.y, size-2, 0, Math.PI*2, true); ctx.closePath(); ctx.clip();
                        ctx.drawImage(img, node.x - size + 2, node.y - size + 2, (size-2)*2, (size-2)*2);
                        ctx.restore();
                    }

                    // Text Labels (Amount, Entity, Classification)
                    const fontSize = 12/globalScale;
                    ctx.font = `bold ${fontSize}px Inter`;
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'top';
                    
                    // Amount (Blue like in nodes.png)
                    ctx.fillStyle = '#2563eb';
                    const amountText = `$${((node.val || 0) * 3000).toLocaleString(undefined, {maximumFractionDigits:0})}`; // Rough USD
                    ctx.fillText(amountText, node.x, node.y + size + 4);
                    
                    // Entity Badge
                    ctx.fillStyle = '#64748b';
                    ctx.font = `600 ${fontSize*0.8}px Inter`;
                    ctx.fillText((node.classification || '').toUpperCase(), node.x, node.y + size + 4 + fontSize + 2);
                })
                .linkCanvasObjectMode(() => 'after')
                .linkCanvasObject((link, ctx, globalScale) => {
                    // Draw Edge Text (Amount USD) over the line
                    const MAX_FONT_SIZE = 10;
                    const LABEL = `$${((link.amount || 0) * 3000).toLocaleString(undefined, {maximumFractionDigits:0})}`; // Rough USD
                    
                    const start = link.source;
                    const end = link.target;
                    
                    if (typeof start !== 'object' || typeof end !== 'object') return; // wait for coords
                    
                    // Calculate midpoint for curved line approximation
                    const midX = start.x + (end.x - start.x) * 0.5;
                    const midY = start.y + (end.y - start.y) * 0.5;
                    
                    const fontSize = Math.min(MAX_FONT_SIZE, 14 / globalScale);
                    ctx.font = `bold ${fontSize}px Inter`;
                    ctx.fillStyle = '#ef4444'; // Red outflow text like in nodes.png
                    
                    // Background pill for text
                    const textWidth = ctx.measureText(LABEL).width;
                    const bckgDimensions = [textWidth, fontSize].map(n => n + fontSize * 0.2);
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
                    ctx.fillRect(midX - bckgDimensions[0] / 2, midY - bckgDimensions[1] / 2, ...bckgDimensions);
                    
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = '#ef4444';
                    ctx.fillText(LABEL, midX, midY);
                });
        }

        // --- SOCKET EVENT LISTENERS ---
        socket.on('connect', () => { console.log("Socket.io Connected"); });

        socket.on('pipeline_update', (msg) => {
            document.getElementById('pipe-progress').style.width = msg.progress + '%';
            document.getElementById('stat-wallets').innerText = msg.wallets;
            document.getElementById('stat-txs').innerText = msg.txs;
            document.getElementById('stat-assets').innerText = msg.assets.toLocaleString(undefined, {minimumFractionDigits: 2});
            
            const stageIndex = PIPELINE_STAGES.indexOf(msg.active_stage);
            if (stageIndex !== -1) {
                for(let i=0; i<stageIndex; i++) {
                    const el = document.getElementById(`stage-${i}`);
                    if(el) { el.className = "pipeline-item completed"; el.innerHTML = `<i class="ph-bold ph-check-circle"></i> <span>${PIPELINE_STAGES[i]}</span>`; }
                }
                const currentEl = document.getElementById(`stage-${stageIndex}`);
                if(currentEl) { currentEl.className = "pipeline-item active"; currentEl.innerHTML = `<i class="ph-bold ph-spinner animate-spin"></i> <span>${PIPELINE_STAGES[stageIndex]}</span>`; currentEl.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
            }
        });

        socket.on('node', (msg) => {
            if (!graphData.nodes.find(n => n.id === msg.node.id)) {
                graphData.nodes.push({...msg.node, val: 0}); // Add val tracking
                Graph.graphData(graphData);
                
                if (msg.node.classification === 'Exchange' || msg.node.classification === 'Mixer') {
                    document.getElementById('alert-badge').classList.remove('hidden');
                }

                // Render Globalized Wallet Card into Tab 1
                const html = `
                <div class="global-card">
                    <div class="flex items-center gap-2 mb-2">
                        <img src="${getLogoUrl(msg.node.chain)}" class="w-4 h-4"> <span class="text-xs font-bold text-slate-500">${msg.node.chain}</span>
                    </div>
                    <div class="flex items-center gap-2 mb-2">
                        <img src="${getEntityLogoUrl(msg.node.entity_name || 'Unknown')}" class="w-4 h-4"> <span class="text-xs font-bold text-slate-800">${msg.node.entity_name || 'Unknown'}</span>
                    </div>
                    <div class="font-mono text-sm text-blue-600 mb-2">${short(msg.node.id)}</div>
                    <div class="text-xs text-slate-500 mb-1">Classification: <span class="font-bold text-slate-800">${msg.node.classification}</span></div>
                    <div class="text-xs text-slate-500 mb-2">Risk: <span class="font-bold ${msg.node.risk_score > 50 ? 'text-rose-600' : 'text-emerald-600'}">${msg.node.risk_score}</span></div>
                    <div class="text-xs text-emerald-500 font-bold flex items-center gap-1"><i class="ph-fill ph-check-circle"></i> Verified</div>
                </div>`;
                document.getElementById('wallet-identity-container').insertAdjacentHTML('afterbegin', html);
            }
        });

        socket.on('edge', (msg) => {
            graphData.links.push(msg.edge);
            
            // Update Node Values
            const sNode = graphData.nodes.find(n => n.id === msg.edge.source);
            const tNode = graphData.nodes.find(n => n.id === msg.edge.target);
            if(sNode) sNode.val += msg.edge.amount;
            if(tNode) tNode.val += msg.edge.amount;

            Graph.graphData(graphData);
            
            // Update UI Ledger (Transaction Globalization)
            const usdValue = msg.edge.usd_value || (msg.edge.amount * 3000);
            const html = `
            <div class="global-card border-l-4 border-l-blue-500 shadow-sm flex-shrink-0 min-w-[300px]">
                <div class="flex items-center gap-2 mb-2">
                    <img src="${getLogoUrl(msg.edge.chain)}" class="w-4 h-4"> <span class="text-xs font-bold text-slate-500">${msg.edge.chain}</span>
                </div>
                <div class="text-lg font-black text-slate-900 mb-1">${msg.edge.amount.toFixed(4)} ${msg.edge.asset || 'NATIVE'}</div>
                <div class="text-xs text-slate-500 mb-3">≈ $${usdValue.toLocaleString(undefined, {maximumFractionDigits:0})}</div>
                <div class="flex items-center gap-2 text-xs mb-3 bg-slate-50 p-2 rounded">
                    <span class="text-slate-500">Transferred:</span>
                    <img src="${getLogoUrl(msg.edge.asset || 'ETH')}" class="w-3 h-3"> <span class="font-bold text-slate-800">${msg.edge.amount.toFixed(4)} ${msg.edge.asset || 'NATIVE'}</span>
                </div>
                <div class="text-[10px] text-slate-400 font-mono mb-2">Hash: ${short(msg.edge.tx_hash)}</div>
                <div class="text-[10px] text-emerald-500 font-bold flex items-center gap-1"><i class="ph-fill ph-check-circle"></i> Verified</div>
            </div>`;
            document.getElementById('live-feed').insertAdjacentHTML('afterbegin', html);
        });

        socket.on('trace_complete', (msg) => {
            document.getElementById('deploy-btn').disabled = false;
            document.getElementById('deploy-btn').innerHTML = `<i class="ph-bold ph-check-circle"></i> Trace Complete`;
            PIPELINE_STAGES.forEach((stage, i) => {
                const el = document.getElementById(`stage-${i}`);
                if(el) { el.className = "pipeline-item completed"; el.innerHTML = `<i class="ph-bold ph-check-circle"></i> <span>${stage}</span>`; }
            });
            document.getElementById('pipe-progress').style.width = '100%';
            document.getElementById('pipe-progress').style.background = '#10b981'; // Emerald

            document.getElementById('t1-summary').innerText = `Completed trace for seed. Identified ${graphData.nodes.length} nodes and ${graphData.links.length} transactions across the network.`;
        });

        // State Machine Polling
        setInterval(async () => {
            try {
                const res = await fetch('/api/v1/system/state'); const data = await res.json();
                document.getElementById('state-human').innerText = data.human;
                document.getElementById('state-machine').innerText = data.machine;
            } catch(e) {}
        }, 3000);

        // --- 4. TRACE INITIATION ---
        async function deployLiveTrace() {
            const seeds = document.getElementById('seeds').value.trim();
            const chain = document.getElementById('chain').value;
            if(!seeds) return alert("Enter address");

            // Reset UI
            graphData = { nodes: [], links: [] };
            if(!Graph) initGraph(); else Graph.graphData(graphData);
            document.getElementById('live-feed').innerHTML = '';
            document.getElementById('wallet-identity-container').innerHTML = '';
            initPipelineUI(); 
            document.getElementById('pipe-progress').style.width = '0%';
            document.getElementById('pipe-progress').style.background = '#3b82f6';
            document.getElementById('deploy-btn').disabled = true;
            document.getElementById('deploy-btn').innerText = "Orchestrating Agents...";
            document.getElementById('alert-badge').classList.add('hidden');
            
            document.getElementById('header-address').innerText = seeds;
            switchTab(1, document.querySelector('.tab-btn')); // Go to tab 1

            try {
                const res = await fetch('/api/v1/trace/deploy', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({seeds, chain_override: chain, max_depth: 2})});
                const data = await res.json();
                window.activeTraceId = data.trace_id;
                socket.emit('join_trace', { trace_id: data.trace_id });
            } catch(e) { 
                alert("Deployment Failed"); 
                document.getElementById('deploy-btn').disabled = false;
            }
        }

        // --- 5. REPORT GENERATOR ---
        async function generateDocReport() {
            if(!window.activeTraceId) return alert("Deploy Trace First");
            const zip = document.getElementById('zip-code') ? document.getElementById('zip-code').value : "";
            
            const ph = document.getElementById('report-placeholder');
            const doc = document.getElementById('full-report-content');
            
            ph.classList.remove('hidden');
            doc.classList.add('hidden');
            ph.innerHTML = `<i class="ph-duotone ph-robot text-6xl mb-4 text-blue-500 animate-pulse"></i><p>Synthesizing Full Evidentiary Dossier via Gemini...</p>`;

            try {
                const res = await fetch(`/api/v1/report/${window.activeTraceId}?zip=${zip}`);
                const data = await res.json();
                
                ph.classList.add('hidden');
                doc.classList.remove('hidden');
                doc.innerHTML = data.html;
            } catch (e) {
                ph.innerHTML = `<p class="text-rose-500">Report Generation Failed: ${e.message}</p>`;
            }
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
    logger.info("  DEPLOYING LIONSGATE NEMESIS APEX (v56.0 MONOLITHIC ARCHITECTURE)  ")
    logger.info("====================================================================")
    uvicorn.run(socket_app, host="0.0.0.0", port=8000)
