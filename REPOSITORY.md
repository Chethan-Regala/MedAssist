# MedAssist Repository Structure

## 📁 What's Included in GitHub

### **Core Application**
```
app/
├── agents/           # Multi-agent system
├── db/              # Database models and connections
├── tools/           # Agent tools (MCP, custom, built-in)
├── memory/          # Session management and memory bank
├── orchestration/   # Agent coordination
├── observability/   # Metrics, tracing, logging
├── evaluation/      # Agent evaluation framework
├── protocols/       # A2A communication protocol
├── main.py          # FastAPI application
├── config.py        # Configuration management
├── schemas.py       # Pydantic models
├── prompts.py       # LLM prompt templates
└── utils.py         # Utility functions
```

### **Tests**
```
tests/
├── test_triage.py      # Triage agent tests
├── test_medication.py  # Medication agent tests
└── test_reminder.py    # Reminder agent tests
```

### **Deployment**
```
├── Dockerfile              # Container definition
├── docker-compose.yml      # Multi-service orchestration
├── requirements.txt        # Python dependencies
└── setup.py                # Package setup
```

### **Vertex AI Deployment**
```
vertex-ai/
├── agent-config.yaml       # Agent configuration
├── agent-tools.json        # Tool definitions
├── cloudbuild.yaml         # Cloud Build config
├── manual-deployment-steps.md
├── get-project-id.md
└── README.md
```

### **Documentation**
```
├── README.md               # Main documentation
├── HACKATHON.md           # Hackathon compliance
├── PROJECT_STRUCTURE.md   # Architecture overview
├── REPOSITORY.md          # This file
└── LICENSE                # MIT License
```

### **Configuration Templates**
```
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
└── pytest.ini           # Test configuration
```

### **Frontend/Testing**
```
├── test.html             # Interactive test interface
└── docker-commands.bat   # Docker management
```

## 🚫 What's NOT Included (Protected by .gitignore)

- `.env` files with API keys
- Database files (`*.db`, `*.sqlite`)
- Python cache (`__pycache__/`)
- IDE settings (`.vscode/`, `.idea/`)
- Log files (`*.log`)
- Virtual environments (`venv/`, `.venv/`)
- Development test scripts
- Temporary files

## 🔒 Security Features

- **API keys protected**: Never committed to repository
- **Environment templates**: `.env.example` for setup guidance
- **Secure defaults**: All sensitive data excluded
- **Production ready**: Clean, deployable codebase

## 🚀 Quick Start for Contributors

1. **Clone repository**:
```bash
git clone YOUR_REPO_URL
cd MedAssist
```

2. **Setup environment**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Run tests**:
```bash
pytest
```

5. **Start development server**:
```bash
python run_server.py
```

## 📊 Repository Stats

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: SQLModel/SQLAlchemy
- **AI/LLM**: Google Gemini 2.5 Flash
- **Deployment**: Docker + Cloud Run
- **Testing**: Pytest
- **License**: MIT

## 🏆 Hackathon Compliance

This repository demonstrates ALL required hackathon concepts:
- ✅ Multi-agent system
- ✅ Tools integration
- ✅ Long-running operations
- ✅ Sessions & Memory
- ✅ Observability
- ✅ Agent evaluation
- ✅ A2A Protocol
- ✅ Agent deployment