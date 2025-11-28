# MedAssist Project Structure

```
medassist/
├── app/                          # Main application package
│   ├── agents/                   # Multi-agent system
│   │   ├── triage.py            # LLM-powered triage agent
│   │   ├── medication.py        # Rule-based medication safety
│   │   ├── reminder.py          # Loop agent for monitoring
│   │   └── llm_client.py        # Gemini API wrapper
│   ├── db/                      # Database layer
│   │   ├── models.py            # SQLModel ORM definitions
│   │   └── db.py                # Database connection & sessions
│   ├── tools/                   # Agent tools system
│   │   ├── base.py              # Base tool interface
│   │   ├── medical_lookup.py    # Custom medical API tools
│   │   ├── mcp_client.py        # Model Context Protocol client
│   │   └── manager.py           # Tool coordination
│   ├── memory/                  # Sessions & memory system
│   │   ├── session.py           # InMemorySessionService
│   │   ├── memory_bank.py       # Long-term health memory
│   │   └── context_compaction.py # Context engineering
│   ├── orchestration/           # Agent coordination
│   │   └── coordinator.py       # Parallel agent execution
│   ├── observability/           # Monitoring & metrics
│   │   ├── metrics.py           # Performance metrics
│   │   └── tracing.py           # Distributed tracing
│   ├── evaluation/              # Agent evaluation
│   │   └── evaluator.py         # Systematic testing framework
│   ├── protocols/               # Communication protocols
│   │   └── a2a.py               # Agent-to-Agent protocol
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration management
│   ├── schemas.py               # Pydantic models
│   ├── prompts.py               # LLM prompt templates
│   └── utils.py                 # Utility functions
├── tests/                       # Test suite
│   ├── test_triage.py          # Triage agent tests
│   ├── test_medication.py      # Medication agent tests
│   └── test_reminder.py        # Reminder agent tests
├── deployment/                  # Deployment configuration
│   ├── Dockerfile              # Container definition
│   └── docker-compose.yml      # Multi-service orchestration
├── docs/                       # Documentation
│   ├── README.md               # Main documentation
│   ├── HACKATHON.md           # Hackathon compliance
│   └── PROJECT_STRUCTURE.md   # This file
├── scripts/                    # Utility scripts
│   ├── run_server.py          # Development server
│   ├── comprehensive_test.py  # Full system test
│   ├── test_api.py           # API functionality test
│   └── check_models.py       # Gemini model checker
├── frontend/                   # Test interface
│   └── test.html              # Interactive test page
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup
└── LICENSE                    # MIT License
```

## Key Components

### **Multi-Agent System**
- **TriageAgent**: LLM-powered symptom analysis with safety overrides
- **MedicationSafetyAgent**: Rule-based drug interaction checking
- **ReminderLoopAgent**: Background health monitoring
- **AgentCoordinator**: Parallel execution and cross-agent insights

### **Tools & Integration**
- **MCP Client**: Model Context Protocol for external data
- **Medical Lookup**: Custom medical database integration
- **Google Search**: Built-in search capabilities
- **Tool Manager**: Centralized tool coordination

### **Memory & Sessions**
- **Session Service**: Conversation state management
- **Memory Bank**: Long-term health history analysis
- **Context Compaction**: Intelligent conversation length management

### **Observability**
- **Distributed Tracing**: Operation tracking across agents
- **Metrics Collection**: Performance and usage analytics
- **Structured Logging**: Comprehensive audit trail

### **Safety & Evaluation**
- **Red Flag Engine**: Deterministic emergency detection
- **Agent Evaluator**: Systematic performance testing
- **Safety Overrides**: Rule-based safety guarantees

### **Communication & Deployment**
- **A2A Protocol**: Agent-to-agent messaging
- **Docker Deployment**: Production-ready containerization
- **Health Monitoring**: Automated system health checks