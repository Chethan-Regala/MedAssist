# **MedAssist — Multi-Agent Personal Health Navigator**

*Transforming personal health support with AI-driven triage, medication safety checks, habit coaching, and explainable reports.*

---

## 🧠 **Overview**

**MedAssist** is a **multi-agent healthcare assistant** designed to provide safe, explainable, and personalized health guidance. It uses a pipeline of LLM-powered agents to:

* Triage symptoms
* Detect red flags & assess urgency
* Check medication conflicts
* Deliver simple explanations of medical info
* Track lifestyle habits over time
* Generate weekly personalized health reports
* Maintain longitudinal health memory
* Support periodic monitoring & reminders

This repository contains the **core backend MVP**, including:

* 🔹 Triage Agent (LLM + rule-based safety layer)
* 🔹 User session & symptom event storage (SQLite)
* 🔹 Clean FastAPI backend
* 🔹 Modular architecture for future agents
* 🔹 Ready for deployment via Docker / Cloud Run

---

# 🌟 **Why MedAssist?**

Healthcare is complex — symptoms are confusing, medication interactions are poorly understood, and people rarely track their own behavior over time.

MedAssist solves this by creating a **personal health navigator**, not just a chatbot.

It is built to meet competition criteria:

✔ Multi-agent
✔ Tools & API integrations
✔ Long-running operations
✔ Memory & context engineering
✔ Observability & safety design
✔ Social impact (Agents for Good)

---

# 🚀 **Key Features (MVP)**

### **1. Symptom Triage Agent**

* LLM-based reasoning + rule-based safety
* Detects red flags
* Classifies symptoms into medical categories
* Outputs structured JSON only
* Provides recommended next step (self-care / primary care / ER)

### **2. Rule-based Red Flag Engine**

* Immediate escalation for life-threatening terms
* Ensures deterministic safety behavior

### **3. Health Session Logging**

* Every triage interaction is stored securely
* Builds a longitudinal medical timeline

### **4. FastAPI Backend**

* Clean REST API
* Type-safe Pydantic schemas
* Ready for extension with additional agents

### **5. SQLite & SQLModel Database**

* Lightweight & reliable for local development
* Easy to switch to Postgres/Mongo later

---

# 🏗️ **Architecture**

```
User
  ↓
FastAPI Backend (/triage)
  ↓
Triage Agent
  ├─ Rule-based red-flag detection
  └─ LLM-based classification & reasoning
  ↓
Decision Output (JSON)
  ↓
Database (User + SymptomEvent)
  ↓
Session Manager (future)
  ↓
Multi-agent pipeline (future)
```

---

# 📁 **Repository Structure**

```
medassist/
├─ app/
│  ├─ main.py               # FastAPI entrypoint
│  ├─ agents/
│  │  ├─ triage.py          # Triage agent logic
│  │  └─ llm_client.py      # Wrapper for LLM API
│  ├─ db/
│  │  ├─ db.py              # Init engine + sessions
│  │  └─ models.py          # SQLModel ORM models
│  ├─ prompts.py            # Prompt templates
│  ├─ schemas.py            # Request/response schemas
│  └─ utils.py              # Helpers (logging, scoring, etc.)
├─ tests/
│  ├─ test_triage.py        # Basic triage tests
├─ requirements.txt
├─ Dockerfile
├─ README.md
└─ .env
```

---

# ⚙️ **Installation & Setup**

### **1. Clone**

```bash
git clone https://github.com/yourusername/medassist.git
cd medassist
```

### **2. Create virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate
```

### **3. Install dependencies**

```bash
pip install -r requirements.txt
```

### **4. Create `.env` file**

```
GEMINI_API_KEY=your-key
GEMINI_MODLE=your-modle
DATABASE_URL=sqlite:///./medassist.db
```

### **5. Run server**

```bash
uvicorn app.main:app --reload
```

---

# 🔌 **API Documentation**

## **POST /triage**

### Request:

```json
{
  "user_id": "user-123",
  "symptoms": "I have severe headache and blurry vision",
  "context": ""
}
```

### Response:

```json
{
  "category": "neurological",
  "urgency": "high",
  "red_flags": ["severe headache"],
  "recommended_action": "go_to_er",
  "reasoning": "Severe sudden headache + visual changes indicate possible neurological emergency."
}
```

---

# 🤖 **The Triage Agent (Detailed)**

### LLM Prompting

* JSON-only output
* Consistent categories
* Safety-first reasoning

### Rule Engine

* Scans for dangerous symptom phrases
* Overrides LLM when emergency keywords appear
* Guarantees deterministic escalation

### Final Output

* Category
* Urgency
* Red flags
* Recommended action
* Short explanation

This hybrid approach yields **safe, reliable, audit-friendly** medical triage.

---

# 🧩 **Extending into Full Multi-Agent MedAssist**

You can expand from the MVP into the full system:

### ✔ Medication Safety Agent

* Integrate with **RxNorm**, **OpenFDA**, **DrugBank**, or Google Search tool
* Cross-check interactions
* Output risk score + warnings

### ✔ Explanation Agent

* Convert medical jargon → simple English
* Re-explain triage decisions
* Provide lifestyle suggestions

### ✔ Lifestyle / Habit Coach

* Tracks: sleep, food, water intake, exercise
* Generates routines & reminders
* Produces weekly PDF report

### ✔ Session Manager Agent

* Maintains long-term user health memory
* Smart context compaction
* Stores symptom timeline

### ✔ Weekly Monitoring / Loops

* APScheduler or Cloud Cron
* Auto-generate reports
* Push reminders

Each agent will be added in `/app/agents/`.

---

# 🛡️ **Safety & Compliance**

MedAssist is **NOT a medical device**.
It provides **informational triage assistance**, not diagnosis.

### Safety Layers Implemented:

* Deterministic red-flag engine
* LLM response parsing + fallback
* Clear disclaimers
* Immediate ER escalation for dangerous symptoms
* Logging for decision transparency
* No hallucinated drug recommendations

### Before production:

* HIPAA compliance (if in US)
* Encrypted DB (AES/GCP/CloudSQL/KMS)
* Consent screen
* Data retention policies
* Moderate outputs for safety

---

# 📊 **Evaluation Plan**

### 1. **Unit Tests**

* Rule-based red flag checks
* JSON parsing
* DB writes/reads

### 2. **Agent Reasoning Tests**

* Synthetic symptom dataset
* Compare LLM decisions with gold-standard labels

### 3. **Safety Tests**

* Force dangerous inputs
* Ensure consistent ER escalation

### 4. **Observability**

Log:

* Prompt
* Raw LLM output
* Parsed output
* Final decision
* Reason for escalation

---

# ☁️ **Deployment: Cloud Run (Recommended)**

### Build:

```bash
docker build -t gcr.io/PROJECT_ID/medassist .
```

### Push:

```bash
gcloud auth configure-docker
docker push gcr.io/PROJECT_ID/medassist
```

### Deploy:

```bash
gcloud run deploy medassist \
  --image gcr.io/PROJECT_ID/medassist \
  --region asia-south1 \
  --platform managed \
  --allow-unauthenticated
```

# 🌈 **Future Roadmap**

* Wearable device integration (Fitbit, Apple Health)
* Full medication safety graph model
* Multilingual support
* Patient education agent
* Telemedicine handoff API

---

# ❤️ **Contributors**

**Chethan** – Creator & Engineer
Open to contributors & collaborators.

---

# 🏁 **License**

MIT License — free for personal & commercial use.

---