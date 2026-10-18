<div align="center">

<img src="https://raw.githubusercontent.com/Khanapatro/supplyshield-ai/refs/heads/main/assests/banner.svg" width="100%" alt="SupplyShield AI"/>

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=22&duration=3000&pause=900&color=00E5FF&center=true&vCenter=true&width=900&height=50&lines=Typhoon+hits+a+Tier-1+supplier...;Traverse+the+multi-tier+graph+in+%3C+5+ms;Quantify+%2462.7M+of+revenue+at+risk;Score+alternatives+deterministically;Commit+the+decision+to+graph+memory" alt="Typing animation" />
</a>

<br/>

![FalkorDB](https://img.shields.io/badge/FalkorDB-Graph%20Engine-E4003B?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Server-7C3AED?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)

![Tests](https://img.shields.io/badge/tests-10%2F10%20passing-2ea44f?style=flat-square)
![Traversal](https://img.shields.io/badge/multi--hop%20traversal-4.99%20ms-00e5ff?style=flat-square)
![Graph](https://img.shields.io/badge/graph-44%20nodes%20%7C%2058%20edges-orange?style=flat-square)

</div>

---

## 📑 Contents

[Overview](#-overview) ·
[The Problem](#-the-problem) ·
[How It Works](#%EF%B8%8F-how-it-works-step-by-step) ·
[Architecture](#%EF%B8%8F-architecture) ·
[Graph Data Model](#%EF%B8%8F-graph-data-model) ·
[Queries](#-what-the-graph-queries-do) ·
[Scoring](#%EF%B8%8F-deterministic-scoring-engine) ·
[Action Memory](#-action-memory) ·
[MCP Tools](#-mcp-tools) ·
[Walkthrough](#-example-incident-walkthrough) ·
[Testing](#-testing) ·
[Run It](#-run-it) ·
[Impact](#-real-world-impact) ·
[FAQ](#-faq)

---

## 📌 Overview

**SupplyShield AI** is an autonomous **supply-chain incident commander**. When a supplier, factory or shipment is hit by a sudden disruption, it answers the questions an executive asks first:

- *What exactly is affected, and how much revenue is at risk?*
- *Which customer orders and product lines break first, and which are safe?*
- *Who can replace the failed supplier, and can they really do it?*
- *What did we decide last time, and why?*

It does this by modelling the entire supply chain as a **knowledge graph in FalkorDB**. Suppliers, components, products, factories, shipments, customer orders and risk events are nodes. Their real-world relationships are edges. Because the data is already connected, the agent follows those connections instead of stitching tables together.

> 💡 **The LLM orchestrates and explains. The graph and the math decide.**

| At a glance | |
| :-- | :-- |
| ⚡ **Speed** | Full multi-hop impact traversal in **4.99 ms** |
| 💰 **Exposure found** | **$62.7M** of customer revenue at risk in the seeded scenario |
| 🕸️ **Graph size** | 44 nodes and 58 edges across 8 node types |
| ⚖️ **Decisions** | Transparent weighted scoring with hard disqualification rules |
| 🧠 **Memory** | Every decision stored in the graph, readable across sessions |
| 🔌 **Integration** | 6 standard MCP tools, plus a REST API and an interactive CLI |
| ✅ **Quality** | 10 of 10 automated tests passing |

---

## ❓ The Problem

Modern manufacturing chains are deep. A single Tier-1 supplier can feed several components, which feed several products, which feed dozens of customer orders. When that supplier fails, four things go wrong at once:

| Pain point | What it looks like in practice |
| :-- | :-- |
| 🙈 **Hidden ripple effect** | Nobody knows which vehicle models or high-value orders will stall until deadlines are already at risk. |
| 🧱 **Siloed data** | Supplier details, bills of materials, factory schedules, in-transit shipments and purchase orders sit in separate ERP, CRM and logistics systems. |
| 🔀 **Multi-hop blindspots** | A question like *"If Apex Semiconductors goes offline, which plant shuts down first, and which delivery deadlines are breached?"* needs 5–6 joins across large tables. It takes minutes or days, not seconds. |
| 😰 **Panic-driven decisions** | Procurement teams make emergency calls and may pick a replacement that is technically incompatible, not automotive-qualified, or too small to supply a full production batch. |

SupplyShield AI removes all four: one connected model, instant multi-hop answers, and replacement decisions that are checked against hard engineering rules before anything is committed.

---

## ⚙️ How It Works (Step by Step)

| Step | Stage | What happens |
| :-: | :-- | :-- |
| 🚨 **1** | **Ingest** | A disruption is reported, for example a typhoon that takes a Tier-1 supplier offline or a canal that congests a shipping lane. The agent identifies the affected supplier or shipment. |
| 🕸️ **2** | **Traverse** | Starting at the disrupted supplier, the agent walks **Supplier → Component → Product ← CustomerOrder** through the graph. Every part, product and order that depends on the failed supplier is found in one pass, ordered by how soon each order is due. |
| 💰 **3** | **Quantify** | The agent adds up the revenue of the affected orders, counts how many are high or critical priority, and separates out product lines that do **not** depend on the failed supplier, so the team does not panic over the wrong things. |
| 🔎 **4** | **Discover** | It queries the graph for alternative suppliers that can make the affected component, excluding the supplier that is down. It reads each candidate's capacity, lead time, risk rating and verified compatibility. |
| ⚖️ **5** | **Evaluate** | Each candidate goes through hard disqualification rules first, then through a weighted score. Rejected candidates keep a clear reason. Viable candidates are ranked. |
| ✅ **6** | **Act** | The best option is committed as a **RecoveryAction** node in FalkorDB, linked to both the replaced supplier and the new supplier, with the justification, score and timestamp. |
| 🧠 **7** | **Remember** | Because the decision lives in the graph, any engineer, executive or agent in a later session can look up what was decided, by whom, when and why. |

---

## 🏗️ Architecture

<div align="center">
  <img src="https://raw.githubusercontent.com/Khanapatro/supplyshield-ai/refs/heads/main/assests/architecture.svg" width="100%" alt="SupplyShield AI system architecture diagram"/>
</div>

### Layer by layer

| Layer | Component | What it does |
| :-- | :-- | :-- |
| **1 · Clients** | Incident Commander CLI, MCP clients, Swagger UI | The ways people and agents reach the system. Engineers use the CLI, LLM clients such as Cursor or Claude Desktop use MCP, and developers explore the API in Swagger. |
| **2 · Interface** | `agent_cli.py`, `app/mcp_server.py`, `app/main.py` | Three front doors to the same logic. The CLI runs the guided incident flow, the MCP server speaks JSON-RPC over stdio, and FastAPI serves REST endpoints with auto-generated docs. |
| **3 · Agent tools** | 6 graph-backed tools | Each tool wraps one capability: overview, impact analysis, alternative discovery, recovery recommendation, action execution and decision history. All interfaces call the same tools, so behaviour is identical everywhere. |
| **4 · Reasoning** | Scoring engine + Cypher query layer | The scoring engine applies hard constraints and the weighted formula. The query layer runs the multi-hop traversals, candidate lookups and write-backs. No model guesses here. |
| **5 · Data** | FalkorDB + FalkorDB Browser | FalkorDB holds the `supplyshield` graph in memory on port 6379. The Browser on port 3000 lets anyone see the same graph visually. |

### Path of one request

1. A client sends a request, for example *analyze the disruption at supplier X*.
2. The interface layer (CLI, MCP server or FastAPI) hands it to the matching agent tool.
3. The tool runs a Cypher query against FalkorDB and gets back connected results.
4. If alternatives are involved, the scoring engine filters and ranks them.
5. If the user approves, the execute tool writes a RecoveryAction back into the graph.
6. The response returns with the evidence path and score breakdown, so the answer can be explained.

### Design principles

- 🎯 **Graph as source of truth.** Facts come from the graph, never from model memory.
- 🔢 **Math over guesses.** Candidate ranking is a fixed formula with fixed rules, so the same input gives the same output.
- 🔍 **Explain everything.** Every result carries its evidence path, and every rejection carries its reason.
- 🔌 **One logic, many doors.** CLI, REST and MCP all share the same tools.
- 🧠 **State lives in the graph.** Nothing is lost when a process ends.

---

## 🕸️ Graph Data Model

<div align="center">
  <img src="https://raw.githubusercontent.com/Khanapatro/supplyshield-ai/refs/heads/main/assests/graph-model.svg" width="100%" alt="SupplyShield AI graph data model diagram"/>
</div>

### Node types

| Node | Count | What it represents | Key properties |
| :-- | :-: | :-- | :-- |
| 🏭 **Supplier** | 6 | Disrupted primaries, verified alternatives and disqualified candidates | id, name, capacity, lead time (days), risk score |
| 🔩 **Component** | 7 | Critical MCUs, battery-management ASICs, LiDAR sensors, transceivers | id, name |
| 🏗️ **Factory** | 3 | Assembly facilities in Munich, Austin and Yokohama | name, location link |
| 🚗 **Product** | 5 | CyberDrive EV Sedan, AeroTruck Commercial EV, RoboTaxi Shuttle, Energy Wall | name |
| 📦 **CustomerOrder** | 9 | High-priority fleet delivery contracts worth over **$62M** | order number, customer name, revenue, days until due |
| 🚢 **Shipment** | 4 | Air and maritime transit cargo batches | supplier and component links |
| ⚡ **RiskEvent** | 2 | Super Typhoon Gaemi (Critical), Canal Shipping Congestion (Medium) | severity, affected entities |
| 📍 **Location** | 8 | Regional technology and manufacturing hubs | country or region |

### Relationships

| Relationship | Meaning | Why it matters |
| :-- | :-- | :-- |
| ⚡ RiskEvent **AFFECTS** Supplier / Shipment | The disruption's entry point | Starts every impact analysis |
| 🚢 Shipment **FROM_SUPPLIER** Supplier | Where cargo originates | Shows cargo stuck in transit |
| 🚢 Shipment **CARRIES** Component | What the cargo contains | Links logistics to parts |
| 🏭 Supplier **SUPPLIES** Component | Who provides which part | First hop of the blast radius |
| 🔩 Component **USED_IN** Product | Bill-of-materials link | Second hop: parts to products |
| 🏗️ Factory **PRODUCES** Product | Which plant builds what | Shows which assembly line stops first |
| 📦 CustomerOrder **ORDERS** Product | Orders waiting on a product | Third hop: products to revenue |
| 🏭 Supplier **ALTERNATIVE_TO** Supplier | A verified replacement, with compatibility score and verification flag | Feeds candidate discovery |
| 📍 Supplier / Factory **LOCATED_IN** Location | Where things are | Regional exposure |
| ✅ RecoveryAction **REPLACES** / **CONTRACTS_TO** Supplier | The recorded decision | The agent's memory |

---

## Screenshots

<img width="1917" height="901" alt="Screenshot 2026-10-18 170430" src="https://github.com/user-attachments/assets/b96e349c-e0bd-4c3a-958c-4ff99d86e3a3" />


## 🔍 What the Graph Queries Do

Three core queries power the agent. In plain terms:

| Query | Question it answers | How it works |
| :-- | :-- | :-- |
| **1 · Downstream impact traversal** | *If this supplier fails, what breaks?* | Starts at the supplier and follows SUPPLIES, USED_IN and ORDERS edges to every affected component, product and customer order. Results include supplier, component, product, order number, customer and revenue, sorted so the **soonest-due orders come first**. |
| **2 · Alternative supplier discovery** | *Who else could make this part?* | Looks at every supplier except the disrupted one. It reads each one's ALTERNATIVE_TO link (compatibility score, verified flag) and the components it can supply, then returns capacity, lead time and risk. |
| **3 · Action execution and memory** | *Record what we decided.* | Finds the disrupted and replacement suppliers, creates a RecoveryAction node with type, status, component, justification, score, agent name and timestamp, and links it to both suppliers. |

**Why this is fast:** FalkorDB stores relationships as direct pointers (index-free adjacency). Following an edge is a pointer hop, not a table join, so the whole traversal finishes in **4.99 ms**.

---

## ⚖️ Deterministic Scoring Engine

No hallucinated inventory. No invented specs. Every candidate goes through the same two stages.

### Stage 1 · Hard constraints (instant disqualification)

| Rule | Why it disqualifies |
| :-- | :-- |
| ❌ Compatibility **below 0.80** | The part is non-automotive grade or has an incompatible pinout. |
| ❌ Available capacity **below 2,000 units** | The supplier cannot fulfil a minimum production batch. |

A disqualified supplier is never ranked. It is reported with its rejection reason.

### Stage 2 · Weighted score

> **Score = 0.40 × Compatibility + 0.30 × Capacity + 0.20 × Lead Time + 0.10 × (1 − Risk)**

| Factor | Weight | Meaning |
| :-- | :-: | :-- |
| 🔧 **Compatibility** | **40%** | Verified pin-for-pin and firmware compatibility. Weighted highest because a part that does not fit is useless. |
| 🏭 **Capacity** | **30%** | Normalized available monthly units. Can they supply the volume? |
| ⏱️ **Lead Time** | **20%** | Turnaround speed factor. Faster delivery scores higher. |
| 🛡️ **Risk** | **10%** | Inverted historical risk rating. Lower risk scores higher. |

### Illustrative example

*These numbers are made up to show the mechanics. They are not the seeded data.*

| Candidate | Compatibility | Capacity | Outcome |
| :-- | :-: | :-: | :-- |
| Supplier A | 0.95 | 5,000 units | ✅ Viable. Score = 0.40×0.95 + 0.30×0.80 + 0.20×0.70 + 0.10×0.80 = **0.84** |
| Supplier B | 0.72 | 6,000 units | ❌ Disqualified: compatibility below 0.80 |
| Supplier C | 0.90 | 1,500 units | ❌ Disqualified: capacity below 2,000 units |

**Why not let the LLM pick?** In automotive, aerospace and medical industries, a hallucinated spec or inventory number can mean a recall. A fixed formula is reproducible, auditable and cannot be talked into a bad choice.

---

## 🧠 Action Memory

When the agent executes a recovery, it writes a **RecoveryAction** node into the graph:

| Field | Purpose |
| :-- | :-- |
| Action type | The kind of action, for example rerouting supply |
| Status | Whether it was executed |
| Component | Which part was being replaced |
| Justification | Why this supplier was chosen |
| Decision score | The weighted score behind the choice |
| Agent name | Who made the decision |
| Timestamp | When it was made |

The node is linked to the **disrupted supplier** (REPLACES) and the **replacement supplier** (CONTRACTS_TO). This gives you:

- 📜 **Auditability.** Anyone can reconstruct what was decided and why.
- 🔁 **Continuity across sessions.** A new agent or engineer picks up exactly where the last one stopped.
- 🕸️ **Connected decisions.** A decision is not a log line in a file. It sits in the same graph as the suppliers, parts and orders it affects, so you can query it alongside them.

---

## 🔌 MCP Tools

The server uses standard JSON-RPC over `stdio`, so any MCP-compliant client can discover and call these tools without custom integration.

| # | Tool | What it does |
| :-: | :-- | :-- |
| 1 | `get_supply_chain_overview` | Returns high-level graph topology counts, a quick health check of what is loaded. |
| 2 | `analyze_disruption` | Runs the multi-hop blast-radius calculation: affected components, products, orders and revenue at risk. |
| 3 | `find_compatible_alternatives` | Finds and evaluates replacement suppliers with the hard constraints and weighted score. |
| 4 | `recommend_recovery_plan` | Combines impact and alternatives into one advisory recommendation. It advises but does not change anything. |
| 5 | `execute_recovery_action` | Commits the chosen recovery as a RecoveryAction node in the graph. |
| 6 | `get_agent_decision_history` | Reads past recovery decisions from graph memory across sessions. |

Tools 1–4 and 6 only **read**. Only tool 5 **writes**, so the one state-changing step is explicit and easy to control.

---

## 🎬 Example Incident Walkthrough

**Scenario:** Super Typhoon Gaemi, a critical risk event, takes a primary semiconductor supplier offline.

1. 🚨 **Alert.** The incident is raised: *"Apex Semiconductors is offline."*
2. 🕸️ **Impact.** In about 5 ms the agent traces the supplier's components to the products that use them and the orders waiting on those products. Result: **$62.7M** of customer revenue at risk, with the soonest-due orders listed first.
3. 🧭 **Scope.** Product lines that do not depend on the failed supplier are flagged as unaffected, so teams focus on the real problem.
4. 🔎 **Candidates.** The agent pulls alternative suppliers from the graph with their capacity, lead time, risk and compatibility.
5. ⚖️ **Ruling.** Under-qualified or undersized suppliers are disqualified with reasons. The rest are scored and ranked.
6. ✅ **Decision.** On approval, the best option is recorded as a RecoveryAction linking the failed and replacement suppliers.
7. 🧠 **Audit.** Later, anyone can call the decision-history tool and see what was chosen and why.

---

## 🧪 Testing

**10 of 10 automated tests pass in about 1.8 seconds.** They cover:

| Area | What is verified |
| :-- | :-- |
| 🌱 **Seeding** | The graph loads with the expected 44 nodes and 58 edges. |
| ♻️ **Idempotency** | Seeding repeatedly never creates duplicates. |
| 🕸️ **Multi-hop traversals** | Impact analysis returns the correct components, products and orders. |
| ⚖️ **Deterministic scoring** | Hard constraints reject the right suppliers and rankings are stable. |
| 🧠 **Action memory** | Recovery actions are written and can be read back. |

---

## 🚀 Run It

**Needs:** Docker with Docker Compose, and Python 3.11+ (or `uv`).

| # | Step | Command | Expected Result |
| :-: | :-- | :-- | :-- |
| 1 | Start graph and browser | `docker compose up -d` | Containers up on `:6379` and `:3000` |
| 2 | Seed the graph | `uv run python -m app.graph.seed` | 44 nodes, 58 edges in ~200 ms |
| 3 | Run the tests | `uv run pytest` | 10/10 passed in ~1.8 s |
| 4 | Launch the agent CLI | `uv run python agent_cli.py` | Full multi-hop response and action |
| 5 | Start the API | `uv run uvicorn app.main:app --reload` | Swagger UI at `http://127.0.0.1:8000/docs` |
| 6 | Start the MCP server | `uv run python -m app.mcp_server` | Tools available to MCP clients over stdio |
| 7 | Explore visually | Open `http://localhost:3000` | Interactive network graph |

Steps 2 to 6 run from the `backend` folder. In FalkorDB Browser, connect to host `falkordb`, port `6379`, and select the `supplyshield` graph.

### 🔭 Key files

| Path | Role |
| :-- | :-- |
| `docker-compose.yml` | Starts FalkorDB and FalkorDB Browser |
| `backend/app/graph/seed.py` | Builds the 44-node, 58-edge knowledge graph |
| `backend/app/mcp_server.py` | MCP server exposing the 6 tools |
| `backend/app/main.py` | FastAPI application |
| `backend/agent_cli.py` | Interactive incident commander |

---

## 💼 Real-World Impact

| Stakeholder | Value Delivered |
| :-- | :-- |
| 👔 **Chief Supply Chain Officer** | Instant, live visibility into the dollar revenue at risk during geopolitical or climate crises. |
| 🛒 **Procurement and Sourcing Managers** | Automated discovery of verified, pin-compatible alternative vendors with lead-time estimates. |
| 🏭 **Plant Operations Managers** | Immediate identification of which assembly lines need rerouted components before work halts. |
| 🤝 **Customer Success and Sales** | Proactive notification of high-priority accounts with realistic delivery timelines. |

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
| :-- | :-- | :-- |
| 🕸️ Graph engine | **FalkorDB** (in-memory, Cypher) | Ultra-low-latency multi-hop traversal |
| 🔍 Graph UI | FalkorDB Browser | Visual explainability for stakeholders |
| ⚙️ Backend | Python 3.11+, FastAPI, Pydantic Settings, Uvicorn | Typed, fast, auto-documented API |
| 🤖 Agent layer | MCP server and interactive CLI | Works with any MCP-compliant client |
| 📦 Packaging | `uv` | Fast, reproducible Python environments |
| 🧪 Testing | `pytest` | Seeding, traversal, scoring and memory tests |
| 🐳 Infra | Docker Compose | One command to start the graph |

---

## ❔ FAQ

<details>
<summary><b>Does the LLM choose the replacement supplier?</b></summary>

<br/>

No. The ranking comes from the deterministic scoring engine and the hard constraints. The LLM orchestrates the tools and explains the result in plain language.

</details>

<details>
<summary><b>Can it recommend a supplier that isn't compatible?</b></summary>

<br/>

No. Anything below 0.80 compatibility or 2,000 units of capacity is disqualified before scoring, and the reason is reported.

</details>

<details>
<summary><b>What happens if I restart everything?</b></summary>

<br/>

Decisions are stored as RecoveryAction nodes in the graph, so they remain available to later sessions. Re-seeding is idempotent and does not create duplicates.

</details>

<details>
<summary><b>Why a graph instead of SQL?</b></summary>

<br/>

Tracing supplier to customer order in SQL needs 5–6 joins that slow down as data grows. In FalkorDB the same path is a chain of direct pointers, giving a 4.99 ms traversal, and the result can be seen visually in FalkorDB Browser.

</details>

<details>
<summary><b>Can I connect my own AI client?</b></summary>

<br/>

Yes. Any MCP-compliant client can launch the stdio server and call the 6 tools.

</details>



<div align="center">

### 👨‍💻 Built by [Khana Patro (Bablu)](https://github.com/Khanapatro)

⭐ **If SupplyShield AI helped or inspired you, give it a star!** ⭐

</div>
