# SupplyShield AI — 3-Minute Demo Video Script (Hackathon Submission)

This script gives you the exact talking points and actions for recording your 3-minute hackathon demo video.

---

## ⏱️ Video Breakdown

| Timestamp | Section | Visual Screen |
| :--- | :--- | :--- |
| **0:00 – 0:35** | **The Problem & FalkorDB Solution** | FalkorDB Browser UI with all connected nodes |
| **0:35 – 1:20** | **Multi-Hop Traversal (Disruption Analysis)** | Terminal running Cypher Query / Agent CLI |
| **1:20 – 2:05** | **Deterministic Scoring & Alternative Selection** | Terminal / Swagger API docs showing scoring matrix |
| **2:05 – 2:40** | **Action Execution & Graph Memory** | FalkorDB Browser showing `(:RecoveryAction)` node |
| **2:40 – 3:00** | **Conclusion & Hackathon Track Alignment** | Architecture diagram in README |

---

## 🎙️ Step-by-Step Script

### Part 1: Introduction (0:00 - 0:35)
> *"Hello judges! Welcome to **SupplyShield AI**, an autonomous, graph-powered supply chain recovery agent built for the FalkorDB Hackathon under **Track 01: Agents That Act on Connected Data**.*
> 
> *In global manufacturing, when a Tier-1 supplier goes down—say from a typhoon or factory fire—companies face a catastrophic ripple effect. Answering 'Which car models will stop, which customer orders are delayed, and who can replace them?' usually takes days of SQL queries and panic.*
> 
> *Relational databases struggle with deep multi-hop joins. That’s why we chose **FalkorDB**, an ultra-low latency in-memory graph database, as the primary relationship and reasoning engine."*

---

### Part 2: Live Multi-Hop Graph Reasoning (0:35 - 1:20)
> *(Action: Show the FalkorDB Browser or run `agent_cli.py`)*
> 
> *"Let's trigger a real-world crisis scenario: A Category-5 Typhoon strikes Taiwan, shutting down our primary microcontroller supplier, **Apex Semiconductors (`SUP-001`)**.*
> 
> *Instead of relying on guesswork, our AI agent queries FalkorDB with a multi-hop traversal:*
> `(:Supplier)-[:SUPPLIES]->(:Component)-[:USED_IN]->(:Product)<-[:ORDERS]-(:CustomerOrder)`
> 
> *In just **4.9 milliseconds**, FalkorDB identifies:*
> - *1 critical component halted (`CMP-101`).*
> - *3 vehicle lines stalled: the CyberDrive Sedan, AeroTruck, and RoboTaxi Shuttle.*
> - *7 high-priority customer orders across Europe and North America totaling **$62.7 Million in at-risk revenue**.*
> - *And equally important: it proves that our energy wall products are completely unaffected!*
> 
> *Every single conclusion is backed by traceable graph paths."*

---

### Part 3: Alternative Discovery & Deterministic Scoring (1:20 - 2:05)
> *(Action: Point to the Candidate Evaluation Matrix in `agent_cli.py`)*
> 
> *"Next, the agent discovers recovery alternatives. In mission-critical supply chains, an LLM cannot hallucinate fake suppliers or ignore engineering standards.*
> 
> *SupplyShield uses a deterministic scoring formula weighted on:*
> - *Component Compatibility (40%)*
> - *Manufacturing Capacity (30%)*
> - *Lead Time (20%)*
> - *Supplier Risk (10%)*
> 
> *Notice how hard constraints immediately disqualify invalid options:*
> - *Vanguard Legacy Chips is **DISQUALIFIED** because its chip lacks automotive AEC-Q100 qualification and its capacity is below minimum batch size.*
> - *EuroSilicon Systems is feasible as a backup option.*
> - *And **Nexus Microelectronics (`SUP-002`)** ranks #1 with a score of **88.8/100**, offering a verified drop-in replacement with a 10-day lead time."*

---

### Part 4: Graph Action & Cross-Session Memory (2:05 - 2:40)
> *(Action: Show the Step 4 terminal output or query `MATCH (act:RecoveryAction) RETURN act` in FalkorDB Browser)*
> 
> *"A true agent doesn't just analyze—it acts. Based on what the graph revealed, the agent executes the recovery decision and writes a `(:RecoveryAction)` node directly into FalkorDB graph memory.*
> 
> *This node links the disrupted supplier, the replacement supplier, the timestamp, and the exact mathematical justification. If another agent or user logs in tomorrow, FalkorDB remembers this decision across sessions!"*

---

### Part 5: Conclusion (2:40 - 3:00)
> *"SupplyShield AI demonstrates the true power of FalkorDB: ultra-fast traversal, transparent evidence-backed AI reasoning, and persistent graph memory.*
> 
> *The entire system runs locally via Docker Compose, features automated pytest coverage, and exposes tools via both FastAPI and the Model Context Protocol (MCP).*
> 
> *Thank you for watching, and we hope you enjoy SupplyShield AI!"*
