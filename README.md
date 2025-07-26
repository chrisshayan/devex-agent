# DevEx Ambient Agent with Knowledge Graph

<div align="center">

**🚀 Elevating Developer Experience through Intelligent AI and Knowledge-Driven Code Evaluation**

![DevEx Agent Architecture](https://img.shields.io/badge/Architecture-Ambient%20Agent-blue)
[![LangChain](https://img.shields.io/badge/LangChain-Latest-purple.svg)](https://langchain.com)
![LangGraph](https://img.shields.io/badge/LangGraph-Enabled-purple)
[![Neo4J](https://img.shields.io/badge/Neo4j-008CC1?logo=neo4j&logoColor=white)](#)

An intelligent ambient agent that proactively analyzes code and provides morning briefings with actionable insights, enhanced with a sophisticated Knowledge Graph system for golden source reference and code evaluation.

[🚀 Quick Start](#-quick-start) •
[📖 Documentation](#-documentation) •
[🎯 Features](#-features) •
[🏗️ Architecture](#%EF%B8%8F-architecture) •
[🤝 Contributing](#-contributing)

</div>

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#%EF%B8%8F-architecture)
- [🔧 Technology Stack](#-technology-stack)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Installation](#%EF%B8%8F-installation)
- [📚 Knowledge Graph Setup](#-knowledge-graph-setup)
- [🧪 Enhanced Analysis Setup](#-enhanced-analysis-setup)
- [🎯 Usage Examples](#-usage-examples)
- [📖 API Reference](#-api-reference)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [🔧 Configuration](#-configuration)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [🔮 Roadmap](#-roadmap)
- [📄 License](#-license)
- [🆘 Support](#-support)

---

## ✨ Features

### 🌟 Core Ambient Agent

- **🌅 Morning Brief Generation**: Intelligent daily summaries using LangGraph workflows
- **🔬 Enhanced Code Analysis**: Real-world security and quality analysis with professional tools
- **📊 Pattern Detection**: Advanced AI-powered pattern recognition and anomaly detection
- **🔄 Event-Driven Architecture**: Seamless integration with IDEs and development tools
- **⚡ Real-time Processing**: Ambient event processing with intelligent prioritization

### 🧠 Knowledge Graph System

- **📚 Golden Source Management**: Register GitHub repos, Confluence pages, DeepWiki content, and text files
- **🔍 Semantic Search**: Vector-based search across all knowledge sources using ChromaDB
- **🎯 Contextual Code Evaluation**: Compare new code against established patterns and best practices
- **🔗 Relationship Mapping**: Understand dependencies, similarities, and conflicts between code patterns
- **⚡ Real-time Context**: Receive relevant knowledge precisely when and where you need it
- **🤖 Intelligent Recommendations**: Get suggestions based on proven patterns from golden sources

### 🛡️ Advanced Code Analysis

- **🔐 Security Analysis**: Bandit, Safety, Semgrep for comprehensive security scanning
- **📏 Quality Metrics**: Pylint, Flake8, MyPy for code quality and style analysis
- **📈 Complexity Analysis**: Radon for cyclomatic complexity measurement
- **🧹 Dead Code Detection**: Vulture for unused code identification
- **📄 File-Level Details**: Specific file paths, line numbers, and issue descriptions

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Developer Interface"
        IDE[IntelliJ Plugin]
        API[REST API]
        CLI[CLI Interface]
    end

    subgraph "Knowledge Graph Core"
        KGS[Knowledge Graph Service]
        ISE[Ingestion & Search Engine]
        REL[Relationship Engine]
        EMB[Embedding Service]
    end

    subgraph "Source Connectors"
        GHC[GitHub Connector]
        CONF[Confluence Connector]
        DWC[DeepWiki Connector]
        FC[File Connector]
        MCP[MCP Adapters]
    end

    subgraph "Storage Layer"
        VDB[(Vector Database<br/>ChromaDB)]
        GDB[(Graph Database<br/>Neo4j)]
        RDB[(Relational Database<br/>PostgreSQL)]
        CACHE[(Redis Cache)]
    end

    subgraph "AI & Analytics"
        LLM[LLM Service<br/>OpenAI/Claude]
        ANA[Code Analyzer]
        PAT[Pattern Engine]
        SIM[Similarity Engine]
    end

    subgraph "Integration Layer"
        AMB[Ambient Orchestrator]
        WF[LangGraph Workflows]
        EVT[Event Bus]
    end

    IDE --> API
    API --> KGS
    KGS --> ISE
    KGS --> REL
    KGS --> EMB

    ISE --> GHC
    ISE --> CONF
    ISE --> DWC
    ISE --> FC
    ISE --> MCP

    KGS --> VDB
    KGS --> GDB
    KGS --> RDB
    KGS --> CACHE

    KGS --> LLM
    KGS --> ANA
    KGS --> PAT
    KGS --> SIM

    KGS --> AMB
    AMB --> WF
    WF --> EVT
```

---

## 🔧 Technology Stack

### Backend & AI
- **Python 3.9+** with FastAPI for high-performance APIs
- **uv** for blazing-fast dependency management and virtual environments
- **LangChain & LangGraph** for AI workflows and agentic patterns
- **OpenAI GPT-4** / **Claude** for LLM capabilities
- **ChromaDB / Qdrant** for vector storage and semantic search
- **Neo4j** for graph relationships and knowledge mapping
- **PostgreSQL** for structured data and metadata

### Analysis Tools
- **Bandit** for Python security analysis
- **Safety** for dependency vulnerability checking
- **Semgrep** for multi-language security patterns
- **Pylint, Flake8, MyPy** for comprehensive code analysis
- **Radon** for complexity analysis
- **Vulture** for dead code detection

### Integration & Infrastructure
- **Model Context Protocol (MCP)** for extensible connectors
- **Docker** for containerization
- **Redis** for caching and session management
- **IntelliJ Platform SDK** for IDE integration

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Node.js 16+** (for IntelliJ plugin development)
- **Docker** (recommended for database services)
- **OpenAI API key** (optional, for enhanced LLM features)

### 30-Second Setup

```bash
# 1. Clone and enter directory
git clone https://github.com/your-org/devex-agent.git
cd devex-agent

# 2. Install dependencies with uv
uv sync

# 3. Set API key (optional)
export OPENAI_API_KEY="your-api-key"

# 4. Start the agent
uv run python -m devex_agent.main
```

### Register Your First Golden Source

```bash
curl -X POST http://localhost:8000/api/v1/knowledge-graph/sources \
  -H "Content-Type: application/json" \
  -d '{
    "type": "github",
    "config": {
      "name": "Company Standards",
      "repository": "your-org/coding-standards",
      "branch": "main"
    },
    "priority": "high"
  }'
```

### Get Your Morning Brief

```bash
curl http://localhost:8000/brief/morning/your-dev-id@company.com
```

---

## ⚙️ Installation

### Option 1: Full Installation with Docker

```bash
# Clone the repository
git clone https://github.com/your-org/devex-agent.git
cd devex-agent

# Start databases with Docker Compose
docker-compose up -d postgres neo4j redis

# Install all dependencies with uv
uv sync

# Start the agent
uv run python -m devex_agent.main
```

### Option 2: Minimal Installation

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install core dependencies
uv sync

# Start with basic configuration (uses SQLite and mock graph DB)
uv run python -m devex_agent.main
```

### Option 3: Development Installation

```bash
# Install all dependencies including development tools
uv sync --dev

# Install pre-commit hooks (if using)
uv run pre-commit install

# Run tests
uv run pytest tests/
```

---

## 📚 Knowledge Graph Setup

### Supported Golden Source Types

| Source Type | Description | Use Cases |
|-------------|-------------|-----------|
| **GitHub** | Repositories, issues, PRs, wikis | Code standards, examples, documentation |
| **Confluence** | Pages, spaces, attachments | Architecture decisions, processes |
| **DeepWiki** | Wiki pages and content | Technical knowledge bases |
| **Local Files** | Text, markdown, code files | Team-specific standards |
| **MCP Connectors** | Custom sources via MCP | Extensible integrations |

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Core Agent Configuration
OPENAI_API_KEY=your_openai_api_key_here
HOST=localhost
PORT=8000
DEBUG=true

# Knowledge Graph Configuration
KG_VECTOR_STORE_PATH=./data/vector_store
KG_GRAPH_DATABASE_URL=bolt://localhost:7687
KG_RELATIONAL_DATABASE_URL=postgresql://user:pass@localhost:5432/devex

# Source Connector Tokens
GITHUB_ACCESS_TOKEN=your_github_token
CONFLUENCE_USERNAME=your_confluence_username
CONFLUENCE_API_TOKEN=your_confluence_api_token
DEEPWIKI_API_KEY=your_deepwiki_api_key
```

### Golden Sources Configuration

Create `config/golden-sources.yaml` (see [config/golden-sources-example.yaml](config/golden-sources-example.yaml)):

```yaml
golden_sources:
  - id: "company-backend-patterns"
    type: "github"
    config:
      name: "Company Backend Standards"
      repository: "your-company/backend-standards"
      branch: "main"
      include_patterns: ["src/**/*.py", "docs/**/*.md"]
      exclude_patterns: ["tests/**/*"]
    priority: "high"
    auto_sync: true
    sync_interval: "6h"
    enabled: true

  - id: "architecture-decisions"
    type: "confluence"
    config:
      name: "Architecture Decision Records"
      base_url: "https://yourcompany.atlassian.net"
      space_key: "ARCH"
      page_filter: "label = 'architecture-decision'"
      username: "${CONFLUENCE_USERNAME}"
      api_token: "${CONFLUENCE_API_TOKEN}"
    priority: "high"
    auto_sync: true
    sync_interval: "1d"
    enabled: true
```

---

## 🧪 Enhanced Analysis Setup

### Install Analysis Tools

All analysis tools are already included in the uv dependencies. Simply run:

```bash
# Install all dependencies including analysis tools
uv sync

# Optional: Semgrep (requires separate installation)
# See: https://semgrep.dev/docs/getting-started/
```

### Test Enhanced Analysis

```bash
# Create sample files with intentional issues
python demo_enhanced_analysis.py --create-samples

# Run analysis demo
python demo_enhanced_analysis.py
```

### Expected Enhanced Output

**Before:** `"Found 28 security issues"`

**After:**
```json
{
  "critical_items": [
    {
      "type": "security",
      "title": "Security concerns detected",
      "count": 4,
      "files": [
        {
          "file_path": "src/auth/service.py",
          "line_number": 45,
          "description": "Hardcoded password in dictionary",
          "severity": "high",
          "rule_id": "B105",
          "tool": "bandit"
        }
      ]
    }
  ]
}
```

---

## 🎯 Usage Examples

### Enhanced Morning Brief with Knowledge Graph

```json
{
  "developer_id": "alice@company.com",
  "generated_at": "2024-01-15T08:00:00Z",
  "summary": "Good morning! Your recent auth service changes align well with company patterns.",
  "golden_source_evaluation": {
    "alignment_score": 0.87,
    "pattern_matches": [
      {
        "pattern": "JWT Authentication Pattern",
        "source": "company/backend-standards",
        "confidence": 0.92,
        "reference_file": "src/auth/jwt_service.py"
      }
    ],
    "recommendations": [
      {
        "type": "enhancement",
        "description": "Consider adding rate limiting as shown in golden source",
        "reference": "company/backend-standards/src/auth/rate_limiter.py"
      }
    ]
  },
  "critical_items": [
    {
      "type": "security",
      "title": "Security concerns detected",
      "files": [
        {
          "file_path": "src/config.py",
          "line_number": 12,
          "description": "Hardcoded password detected",
          "severity": "high",
          "tool": "bandit"
        }
      ]
    }
  ]
}
```

### Contextual Code Evaluation

```bash
# Evaluate code against golden sources
curl -X POST http://localhost:8000/api/v1/knowledge-graph/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "developer_id": "alice@company.com",
    "code_content": "def authenticate_user(token):\n    return validate_jwt(token)",
    "file_path": "src/auth/service.py",
    "language": "python"
  }'
```

### Semantic Knowledge Search

```bash
# Search across all golden sources
curl -X POST http://localhost:8000/api/v1/knowledge-graph/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "JWT authentication best practices",
    "developer_id": "alice@company.com",
    "current_file": "src/auth/jwt_service.py",
    "language": "python",
    "max_results": 5
  }'
```

### IntelliJ Plugin Integration

```kotlin
// Auto-trigger knowledge graph suggestions
class CodeAssistantAction : AnAction() {
    override fun actionPerformed(event: AnActionEvent) {
        val context = DevelopmentContext(
            currentFile = event.getData(CommonDataKeys.PSI_FILE)?.name,
            selectedCode = event.getData(CommonDataKeys.EDITOR)?.selectionModel?.selectedText,
            language = "python"
        )
        
        val suggestions = knowledgeGraphService.getContextualSuggestions(context)
        showSuggestionsPopup(suggestions)
    }
}
```

---

## 📖 API Reference

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/events/ingest` | Ingest development events |
| `GET` | `/brief/morning/{developer_id}` | Generate morning brief |
| `GET` | `/status/{developer_id}` | Get agent status |

### Knowledge Graph Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/knowledge-graph/sources` | Register golden source |
| `GET` | `/api/v1/knowledge-graph/sources` | List all sources |
| `GET` | `/api/v1/knowledge-graph/sources/{id}` | Get specific source |
| `PUT` | `/api/v1/knowledge-graph/sources/{id}` | Update source |
| `DELETE` | `/api/v1/knowledge-graph/sources/{id}` | Remove source |
| `POST` | `/api/v1/knowledge-graph/sources/{id}/ingest` | Trigger ingestion |
| `GET` | `/api/v1/knowledge-graph/sources/{id}/health` | Check source health |
| `POST` | `/api/v1/knowledge-graph/search` | Search knowledge |
| `GET` | `/api/v1/knowledge-graph/context/{developer_id}` | Get contextual knowledge |
| `POST` | `/api/v1/knowledge-graph/evaluate` | Evaluate code |
| `POST` | `/api/v1/knowledge-graph/sync-all` | Sync all sources |

### Example API Usage

```python
import requests

# Register a GitHub source
response = requests.post(
    "http://localhost:8000/api/v1/knowledge-graph/sources",
    json={
        "type": "github",
        "config": {
            "name": "Security Patterns",
            "repository": "company/security-patterns",
            "branch": "main"
        },
        "priority": "high"
    }
)

# Search for patterns
search_response = requests.post(
    "http://localhost:8000/api/v1/knowledge-graph/search",
    json={
        "query": "authentication patterns",
        "developer_id": "alice@company.com",
        "max_results": 10
    }
)
```

---

## 🧪 Testing

### Run Tests

```bash
# Run all tests
uv run pytest tests/

# Run specific test categories
uv run pytest tests/unit/                    # Unit tests
uv run pytest tests/integration/             # Integration tests
uv run pytest tests/knowledge_graph/         # Knowledge graph tests

# Run with coverage
uv run pytest --cov=src tests/

# Run enhanced analysis tests
uv run pytest tests/workflows/test_enhanced_analyzer.py
```

### Test Knowledge Graph Features

```bash
# Test vector store
uv run pytest tests/knowledge_graph/test_vector_store.py

# Test golden source registration
uv run pytest tests/knowledge_graph/test_source_management.py

# Test semantic search
uv run pytest tests/knowledge_graph/test_search_engine.py
```

---

## 🚀 Deployment

### Docker Deployment

```bash
# Build and deploy all services
docker-compose -f docker-compose.prod.yml up -d

# Or deploy individual components
docker build -t devex-agent .
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e GITHUB_ACCESS_TOKEN=your_token \
  devex-agent
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get pods -l app=devex-agent

# View logs
kubectl logs -f deployment/devex-agent
```

### Production Configuration

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  devex-agent:
    image: devex-agent:latest
    environment:
      - DEBUG=false
      - HOST=0.0.0.0
      - PORT=8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - neo4j
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: devex_kg
      POSTGRES_USER: devex
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  neo4j:
    image: neo4j:5.0
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_dbms_memory_heap_max__size: 2G
    volumes:
      - neo4j_data:/data
```

---

## 🔧 Configuration

### Golden Source Configuration Examples

#### GitHub Source
```yaml
- id: "backend-standards"
  type: "github"
  config:
    name: "Backend Development Standards"
    repository: "company/backend-standards"
    branch: "main"
    include_patterns: ["src/**/*.py", "docs/**/*.md"]
    exclude_patterns: ["tests/**/*", "*.pyc"]
    access_token: "${GITHUB_ACCESS_TOKEN}"
    include_issues: true
    include_prs: true
    include_wiki: true
  priority: "high"
  auto_sync: true
  sync_interval: "6h"
```

#### Confluence Source
```yaml
- id: "architecture-docs"
  type: "confluence"
  config:
    name: "Architecture Documentation"
    base_url: "https://company.atlassian.net"
    space_key: "ARCH"
    page_filter: "type = page AND space = ARCH"
    username: "${CONFLUENCE_USERNAME}"
    api_token: "${CONFLUENCE_API_TOKEN}"
    include_attachments: true
    include_comments: false
  priority: "medium"
  auto_sync: true
  sync_interval: "1d"
```

### Advanced Performance Settings

```yaml
# config/advanced-settings.yaml
performance:
  max_concurrent_syncs: 5
  chunk_size: 1000
  chunk_overlap: 200
  max_file_size_mb: 50
  batch_size: 100
  vector_search_timeout: 30

embedding:
  model: "sentence-transformers/all-mpnet-base-v2"
  dimension: 768
  batch_size: 32

cache:
  ttl_seconds: 3600
  max_entries: 10000
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. ChromaDB Installation Problems

```bash
# Clear ChromaDB data and reinstall
rm -rf ./data/vector_store
pip install chromadb --no-cache-dir

# On macOS with M1/M2
pip install chromadb --no-binary :all:
```

#### 2. GitHub API Rate Limiting

```bash
# Check rate limit status
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/rate_limit

# Solution: Use a higher-tier token or reduce sync frequency
```

#### 3. Analysis Tools Not Found

```bash
# Verify tool installation
uv run bandit --version
uv run pylint --version
uv run flake8 --version

# Reinstall all tools
uv sync --dev
```

#### 4. Vector Store Initialization Errors

```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Clear and reinitialize
rm -rf ./data/vector_store
python -m devex_agent.main
```

### Debug Mode

```bash
# Enable comprehensive debugging
export DEBUG=true
export LOG_LEVEL=DEBUG
export KG_DEBUG=true

# Start with verbose logging
python -m devex_agent.main --verbose
```

### Health Check Commands

```bash
# System health
curl http://localhost:8000/

# Knowledge graph status
curl http://localhost:8000/status/your-dev-id

# Vector store statistics
curl http://localhost:8000/api/v1/knowledge-graph/analytics

# Source health check
curl http://localhost:8000/api/v1/knowledge-graph/sources/source-id/health
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

1. **Fork the repository**
   ```bash
   git fork https://github.com/your-org/devex-agent.git
   cd devex-agent
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Set up development environment**
   ```bash
   uv sync --dev
   uv run pre-commit install
   ```

4. **Make changes and test**
   ```bash
   uv run pytest tests/
   uv run flake8 src/
   uv run mypy src/
   ```

5. **Submit a pull request**

### Code Style

- Follow PEP 8 for Python code
- Use type hints throughout
- Write comprehensive tests
- Document new features
- Keep commits atomic and well-described

### Testing Guidelines

- Write unit tests for all new functionality
- Add integration tests for API endpoints
- Include knowledge graph tests for KG features
- Ensure minimum 80% code coverage

---

## 🔮 Roadmap

### Current Focus (Q1 2024)
- ✅ Knowledge Graph Architecture Design
- ✅ Core Knowledge Graph Service Implementation
- 🔄 GitHub and Confluence Connectors
- 🔄 Enhanced Morning Brief with Golden Source Integration

### Near Term (Q2 2024)
- 🔄 Advanced Pattern Recognition
- 📋 Real-time Code Evaluation
- 📋 IntelliJ Plugin Knowledge Graph Integration
- 📋 Performance Optimization

### Future Vision (2024+)
- 📋 Multi-language Support Extension
- 📋 Advanced AI Code Generation
- 📋 Team Collaboration Features
- 📋 Enterprise Security Enhancements
- 📋 VSCode Plugin
- 📋 Slack/Teams Integration

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

<div align="center">

### Need Help?

| Resource | Description | Link |
|----------|-------------|------|
| 📚 **Documentation** | Comprehensive guides and API docs | [docs/](docs/) |
| 🐛 **Bug Reports** | Report issues and bugs | [GitHub Issues](https://github.com/your-org/devex-agent/issues) |
| 💬 **Discussions** | Community discussions and Q&A | [GitHub Discussions](https://github.com/your-org/devex-agent/discussions) |
| 📧 **Contact** | Direct support from DevEx team | devex@company.com |
| 💡 **Feature Requests** | Suggest new features | [GitHub Issues](https://github.com/your-org/devex-agent/issues/new?template=feature_request.md) |

</div>

### Frequently Asked Questions

**Q: How do I add a custom knowledge source?**
A: Use the MCP connector system. See [MCP Configuration Guide](docs/mcp-connectors.md) for details.

**Q: Can I use this without OpenAI API?**
A: Yes! The system works with basic analysis. OpenAI enhances pattern detection and insights.

**Q: How much storage does the Knowledge Graph need?**
A: Depends on sources. Typical setup: ~100MB for vector store, ~50MB for graph data per 1000 documents.

**Q: Is this secure for enterprise use?**
A: Yes. All data stays in your infrastructure. Supports enterprise authentication and audit logging.

---

<div align="center">

**Built with ❤️ by the DevEx Team**

*Empowering developers with intelligent, ambient AI and knowledge-driven insights.*

⭐ **Star this repo** if you find it useful! ⭐

</div> 