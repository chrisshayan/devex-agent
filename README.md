# DevEx Ambient Agent: Elevating the Developer Experience

An intelligent ambient AI agent that proactively analyzes your development workflow and provides morning briefings with actionable insights and suggestions. Built with [LangGraph](https://blog.langchain.dev/introducing-ambient-agents/) following modern ambient agent patterns.

![DevEx Agent Architecture](https://img.shields.io/badge/Architecture-Ambient%20Agent-blue) ![Python](https://img.shields.io/badge/Python-3.9%2B-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green) ![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-purple)

## 🌟 What is an Ambient Agent?

Unlike traditional chat-based AI that requires you to initiate conversations, ambient agents:
- **Listen continuously** to your development environment
- **Act autonomously** on relevant events and patterns  
- **Provide proactive insights** without interrupting your flow
- **Scale your capabilities** by handling multiple tasks simultaneously

Based on [LangChain's Ambient Agent research](https://blog.langchain.dev/introducing-ambient-agents/), this agent embodies the future of developer assistance.

## 🚀 Features

### Core Capabilities
- **🌅 Morning Briefings**: Automatic analysis of overnight work with actionable insights
- **📊 Real-time Monitoring**: Passive observation of file changes, commits, and build events
- **🤖 Intelligent Analysis**: LangGraph workflows for sophisticated pattern detection
- **💡 Proactive Suggestions**: Context-aware recommendations for code quality and productivity
- **🔔 Smart Notifications**: Alert system for critical issues requiring immediate attention

### Integration Points
- **IntelliJ Plugin**: Seamless IDE integration with file change monitoring
- **Git Integration**: Automatic commit and branch analysis
- **Build System**: CI/CD pipeline event processing
- **REST API**: Flexible integration with any development tool

## 📁 Project Structure

```
devex-agent/
├── src/devex_agent/          # Core ambient agent implementation
│   ├── main.py              # FastAPI application entry point
│   ├── core/                # Ambient orchestrator and core logic
│   ├── workflows/           # LangGraph workflow definitions
│   ├── api/                 # REST API models and endpoints
│   └── config/              # Configuration and settings
├── intellij-plugin/         # IntelliJ IDEA plugin (Kotlin)
├── tests/                   # Comprehensive test suite
│   ├── test_e2e_file_changes.py    # End-to-end tests
│   └── manual_test_runner.py       # Manual testing script
├── pyproject.toml          # Python project configuration
└── README.md              # You are here!
```

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.9+** with pip
- **OpenAI API Key** (for LLM analysis)
- **Java 17+** (for IntelliJ plugin development, optional)
- **IntelliJ IDEA** (for plugin usage)

### 1. Quick Setup

```bash
# Clone or navigate to your project directory
cd devex-agent

# Install the ambient agent
pip install -e .

# Copy environment template and configure
cp env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Configure Environment

Edit `.env` file:
```bash
# Required: OpenAI API Key for LLM analysis
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Customize agent behavior
HOST=localhost
PORT=8000
DEBUG=true
LLM_MODEL=gpt-3.5-turbo
LLM_TEMPERATURE=0.1
```

### 3. Start the Ambient Agent

```bash
# Start the ambient agent core
python -m devex_agent.main
```

You should see:
```
🚀 Starting DevEx Ambient Agent...
✅ Ambient Agent initialized and monitoring
INFO:     Uvicorn running on http://localhost:8000
```

## 🎯 Usage

### Basic Workflow

The DevEx Ambient Agent follows a simple workflow:

1. **Start the Agent**: Run the ambient agent in the background
2. **Develop Normally**: Code, commit, build - the agent observes passively
3. **Get Morning Brief**: Receive intelligent insights about your recent work
4. **Act on Suggestions**: Follow actionable recommendations to improve your workflow

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/events/ingest` | POST | Send development events to the agent |
| `/brief/morning/{developer_id}` | GET | Get morning brief for developer |
| `/status/{developer_id}` | GET | Check agent status |

### Example: Send a File Change Event

```bash
curl -X POST "http://localhost:8000/events/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "file_changed",
    "source": "intellij",
    "developer_id": "your_dev_id",
    "project_path": "/path/to/project",
    "file_path": "/path/to/file.py",
    "description": "Refactored authentication logic",
    "metadata": {
      "lines_added": 15,
      "lines_deleted": 8,
      "language": "python"
    }
  }'
```

### Example: Get Morning Brief

```bash
curl "http://localhost:8000/brief/morning/your_dev_id"
```

Sample response:
```json
{
  "developer_id": "your_dev_id",
  "generated_at": "2025-01-24T09:00:00Z",
  "status": "success",
  "summary": "Yesterday you made significant progress on authentication refactoring...",
  "activity_overview": {
    "files_changed": 12,
    "commits": 5,
    "build_time": "8.3s"
  },
  "critical_items": [
    {
      "type": "test_failure",
      "title": "3 unit tests failing in auth module",
      "priority": "high"
    }
  ],
  "suggestions": [
    {
      "title": "Add error handling to login function",
      "description": "Consider adding try-catch blocks...",
      "priority": "medium"
    }
  ]
}
```

## 🧪 Testing

### Automated Tests

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install -e .[dev]

# Run all tests
python -m pytest tests/ -v

# Run specific end-to-end tests
python -m pytest tests/test_e2e_file_changes.py -v
```

### Manual End-to-End Testing

For a comprehensive manual test:

```bash
# 1. Start the ambient agent
python -m devex_agent.main

# 2. In another terminal, run the test script
python tests/manual_test_runner.py
```

This will:
- ✅ Create a temporary test project
- ✅ Simulate realistic development events
- ✅ Test morning brief generation
- ✅ Verify all API endpoints
- ✅ Test error scenarios

### Quick API Test

```bash
# Test basic connectivity
curl http://localhost:8000/

# Should return: {"message": "DevEx Ambient Agent is running", "status": "active"}
```

## 🔌 IntelliJ Plugin (Optional)

### Building the Plugin

```bash
cd intellij-plugin
./gradlew buildPlugin
```

### Installing the Plugin

1. Build the plugin (see above)
2. In IntelliJ: `File` → `Settings` → `Plugins` → `⚙️` → `Install Plugin from Disk`
3. Select the built plugin file from `intellij-plugin/build/distributions/`
4. Restart IntelliJ

### Plugin Features

- **Automatic Event Detection**: Monitors file changes, builds, and git operations
- **Background Communication**: Sends events to ambient agent automatically  
- **Non-intrusive Operation**: Works silently without interrupting your development
- **Tool Window**: View agent status and morning briefs directly in IDE

## 🎨 Architecture

The DevEx Ambient Agent follows a modern ambient agent architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   IntelliJ      │    │   Ambient Agent  │    │   LangGraph     │
│   Plugin        │───▶│   Core (FastAPI) │───▶│   Workflows     │
│                 │    │                  │    │                 │
│ • File Monitor  │    │ • Event Ingestion│    │ • Morning Brief │
│ • Git Hooks     │    │ • State Management│    │ • Analysis      │
│ • Build Events  │    │ • API Endpoints  │    │ • Suggestions   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Key Components

1. **Ambient Orchestrator**: Central coordinator managing agent state and workflows
2. **LangGraph Workflows**: Sophisticated analysis pipelines for morning briefings
3. **Event Processing**: Real-time handling of development events
4. **IntelliJ Integration**: Seamless IDE monitoring and event detection

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | **Required**: OpenAI API key for LLM analysis |
| `HOST` | localhost | Agent API host |
| `PORT` | 8000 | Agent API port |
| `DEBUG` | true | Enable debug logging |
| `LLM_MODEL` | gpt-3.5-turbo | OpenAI model for analysis |
| `LLM_TEMPERATURE` | 0.1 | LLM temperature for consistency |
| `AMBIENT_CHECK_INTERVAL` | 300 | Ambient monitoring interval (seconds) |

### Advanced Configuration

For production deployment, customize:
- Database connections
- Vector store settings  
- Authentication tokens
- CORS origins
- Logging levels

See `src/devex_agent/config/settings.py` for all options.

## 🚦 Troubleshooting

### Common Issues

**❌ `pip install -e .` fails**
- Ensure you're in the root directory (where `pyproject.toml` exists)
- Check Python version: `python --version` (needs 3.9+)

**❌ Agent won't start**
- Verify OpenAI API key in `.env` file
- Check port 8000 isn't in use: `lsof -i :8000`
- Review logs for specific error messages

**❌ IntelliJ plugin not working**
- Ensure agent is running first
- Check plugin is properly installed and enabled
- Verify network connectivity to `localhost:8000`

**❌ No morning brief generated**
- Ensure events were sent to the agent first
- Check agent status: `curl http://localhost:8000/status/your_dev_id`
- Verify OpenAI API key has sufficient credits

### Debug Mode

Enable detailed logging:
```bash
# Set in .env file
DEBUG=true
LOG_LEVEL=DEBUG

# Or via environment
DEBUG=true LOG_LEVEL=DEBUG python -m devex_agent.main
```

### Getting Help

1. Check the logs for error messages
2. Run the manual test script: `python tests/manual_test_runner.py`
3. Verify your environment matches prerequisites
4. Review API endpoints with curl commands above

## 🤝 Contributing

This ambient agent represents the cutting edge of developer experience tools. Contributions are welcome!

### Development Setup

```bash
# Install development dependencies
pip install -e .[dev]

# Set up pre-commit hooks (optional)
pre-commit install

# Run tests before committing
python -m pytest tests/ -v
```

### Extension Ideas

- **VS Code Plugin**: Extend beyond IntelliJ
- **Additional LLM Providers**: Support Claude, Gemini, etc.
- **Advanced Analytics**: Deeper productivity insights
- **Team Features**: Multi-developer coordination
- **Slack Integration**: Team notifications and reports

## 📄 License

This project embodies research from LangChain's ambient agent initiatives and modern developer experience patterns.

---

## 🌅 Experience the Future of Development

The DevEx Ambient Agent represents a fundamental shift from reactive to proactive developer assistance. By continuously observing your development patterns and providing intelligent insights, it elevates your entire development experience.

**Ready to get started?**

```bash
pip install -e .
cp env.example .env
# Add your OpenAI API key to .env
python -m devex_agent.main
```

Welcome to the future of ambient developer assistance! 🚀 