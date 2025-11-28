# 🚀 MedAssist - Quick Start Guide

## 30-Second Setup

1. **Get API Key**: Obtain Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **Clone & Run**:
```bash
git clone <repository-url>
cd MedAssist
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
docker-compose up --build
```

3. **Test**: Open http://localhost:8000/docs

## Quick Test Commands

**Test Triage Agent**:
```bash
curl -X POST "http://localhost:8000/triage" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "symptoms": "headache and fever"}'
```

**Test All Systems**:
```bash
curl -X POST "http://localhost:8000/test"
```

**View Metrics**:
```bash
curl "http://localhost:8000/metrics"
```

## What You Get

- ✅ **Multi-Agent System**: LLM + Parallel + Loop agents
- ✅ **Tools Integration**: MCP, Google Search, Custom tools
- ✅ **Memory & Sessions**: Persistent health history
- ✅ **Observability**: Metrics, tracing, logging
- ✅ **A2A Communication**: Agent-to-agent messaging
- ✅ **Production Ready**: Docker deployment

## Need Help?

- **Full Documentation**: [README.md](./README.md)
- **Hackathon Evaluation**: [HACKATHON_EVALUATION.md](./HACKATHON_EVALUATION.md)
- **API Docs**: http://localhost:8000/docs (after startup)

---

**Ready to explore healthcare AI! 🏥**