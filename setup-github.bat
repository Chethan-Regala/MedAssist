@echo off
echo ========================================
echo MedAssist GitHub Repository Setup
echo ========================================

REM Check if git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/windows
    pause
    exit /b 1
)

echo ✓ Git found

REM Initialize repository if not already done
if not exist .git (
    echo Initializing Git repository...
    git init
    git branch -M main
) else (
    echo ✓ Git repository already initialized
)

REM Add all files (respecting .gitignore)
echo Adding files to repository...
git add .

REM Create initial commit
echo Creating initial commit...
git commit -m "🏥 Initial commit: MedAssist Multi-Agent Healthcare AI System

✨ Features:
- Multi-agent system (Triage + Medication + Reminder agents)
- LLM-powered symptom analysis with Gemini 2.5 Flash
- Rule-based medication safety checking
- Background health monitoring with APScheduler
- Session management and long-term memory
- Tool integration (MCP + Custom + Built-in tools)
- Comprehensive observability (logging, tracing, metrics)
- Agent evaluation framework
- A2A protocol for agent communication
- Docker deployment ready
- Vertex AI deployment configurations

🏆 Hackathon Requirements:
✅ Multi-agent system
✅ Tools integration  
✅ Long-running operations
✅ Sessions & Memory
✅ Observability
✅ Agent evaluation
✅ A2A Protocol
✅ Agent deployment

🚀 Ready for production deployment!"

echo.
echo ========================================
echo Repository prepared for GitHub!
echo ========================================
echo.
echo Next steps:
echo 1. Create repository on GitHub.com
echo 2. Copy the repository URL
echo 3. Run: git remote add origin YOUR_REPO_URL
echo 4. Run: git push -u origin main
echo.
echo Repository contains:
echo - Complete MedAssist source code
echo - Docker deployment configuration
echo - Vertex AI deployment files
echo - Comprehensive documentation
echo - Test files and examples
echo ========================================
pause