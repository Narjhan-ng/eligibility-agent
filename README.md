# 🏥 Insurance Eligibility Agent

AI-powered agent for checking insurance eligibility across multiple Italian providers using LangChain and Claude.

## 🎯 Overview

This project demonstrates a **production-ready AI agent** that:
- ✅ Checks insurance eligibility with 4 major Italian providers (Generali, UnipolSai, Allianz, AXA)
- ✅ Calculates risk profiles and premium estimates
- ✅ Loads provider rules dynamically from JSON files
- ✅ Orchestrates multiple tools autonomously to answer complex queries

**Key Learning**: This is a **GenAI Engineering** project focused on agent orchestration, not machine learning.

### 🆕 NEW: Conversation Memory

Supports **multi-turn dialogues** with conversation memory!

- 💬 **Session-based conversations** - Agent remembers context across messages
- 💾 **PostgreSQL persistence** - Conversations saved and resumable
- 🔄 **Chat history loading** - Return to previous conversations
- 🎨 **Modern chat UI** - Clean, responsive interface at `/chat`

**Example multi-turn conversation:**
```
User: "I'm 35 years old, can I get life insurance?"
Agent: [checks eligibility, finds options]

User: "What about health insurance?"
Agent: "Since you're 35 years old (from our conversation), let me check..."
         ↑ Agent remembers age from previous message!
```

## 🏗️ Architecture

```
User Question
    ↓
LangChain Agent (Claude 3.5 Sonnet)
    ↓
Decision: Which tools to call?
    ↓
Tools Execution:
  - calculate_age
  - assess_risk_category
  - check_provider_eligibility (×4 providers)
  - estimate_premium
  - list_available_providers
  - get_provider_details
  - update_provider_rules
    ↓
Agent synthesizes results
    ↓
Natural language response
```

## 🛠️ Tech Stack

- **Python 3.11**
- **LangChain** 0.3.27 - Agent orchestration
- **Anthropic Claude 3.5 Sonnet** - LLM reasoning
- **FastAPI** - REST API with interactive frontend
- **PostgreSQL** 🆕 - Conversation memory persistence
- **Docker & Docker Compose** 🆕 - Containerized deployment
- **JSON** - Dynamic provider rule storage

## 📁 Project Structure

```
eligibility-agent/
├── app/
│   ├── main.py               # FastAPI REST API + HTML frontend
│   ├── agent.py              # Agent orchestration with session support
│   ├── tools.py              # 7 LangChain tools
│   ├── provider_loader.py    # Dynamic JSON rule loading
│   └── session_manager.py    # 🆕 Conversation memory management
├── database/
│   ├── schema.sql            # 🆕 PostgreSQL schema for conversations
│   └── README.md             # 🆕 Database setup guide
├── static/
│   └── chat.html             # 🆕 Chat interface with memory
├── data/
│   └── providers/            # Provider rules (JSON)
│       ├── generali.json
│       ├── unipolsai.json
│       ├── allianz.json
│       └── axa.json
├── tests/
│   ├── test_api.py           # API integration tests (13 tests)
│   ├── test_tools.py         # Unit tests for tools
│   ├── test_provider_loader.py
│   ├── test_dynamic_tools.py
│   └── test_agent.py         # Agent integration tests
├── Dockerfile                # 🆕 Multi-stage Docker build
├── docker-compose.yml        # 🆕 App + PostgreSQL orchestration
├── .dockerignore             # 🆕 Docker build exclusions
├── docker-run.sh             # 🆕 Helper script for Docker
├── DOCKER.md                 # 🆕 Docker deployment guide
├── .env                      # API keys + Database URL (not in git)
├── requirements.txt
└── README.md
```

## 🐳 Quick Start with Docker (Recommended)

The fastest way to run the application:

```bash
# 1. Create environment file
cp .env.docker.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Start with helper script
./docker-run.sh start

# OR use docker-compose directly
docker-compose up -d
```

**Access the application:**
- Web Interface: http://localhost:8000
- Chat Interface: http://localhost:8000/chat
- API Documentation: http://localhost:8000/docs

**View logs:** `./docker-run.sh logs`

See [DOCKER.md](DOCKER.md) for detailed Docker documentation.

---

## 🚀 Manual Setup (Alternative)

### 1. Clone & Install

```bash
cd eligibility-agent
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Key

Get your Anthropic API key from: https://console.anthropic.com/

Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key:
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
```

### 3. Setup Database (Optional - for conversation memory)

**Required for chat interface with memory:**

```bash
# Install PostgreSQL (if not already installed)
# macOS:
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# Create database
psql postgres
CREATE DATABASE eligibility_agent;
\q

# Apply schema
psql eligibility_agent < database/schema.sql

# Add DATABASE_URL to .env
echo "DATABASE_URL=postgresql://postgres:postgres@localhost:5432/eligibility_agent" >> .env
```

**See [database/README.md](database/README.md) for detailed setup instructions.**

**Note**: Without database, you can still use the original interface at `/` (stateless queries).

### 4. Test Tools (No API Key Required)

```bash
# Test individual tools
python test_tools.py

# Test provider loader
python test_provider_loader.py

# Test dynamic tools
python test_dynamic_tools.py
```

### 4. Run FastAPI Server

```bash
# Start the development server
uvicorn app.main:app --reload --port 8000

# Open browser at: http://localhost:8000
# API docs at: http://localhost:8000/docs
```

### 5. Run Tests

```bash
# Run all API tests (mocked, no API key needed)
pytest tests/test_api.py -v

# Run agent tests (requires API key)
python test_agent.py
```

## 💡 Usage Examples

### Web Interface (Easiest)

1. Start server: `uvicorn app.main:app --reload`
2. Choose your interface:
   - **Original Interface**: http://localhost:8000 (stateless queries)
   - **🆕 Chat Interface**: http://localhost:8000/chat (with conversation memory)

<img src="https://via.placeholder.com/800x400/667eea/ffffff?text=Interactive+Web+Interface" alt="Web Interface" width="100%"/>

#### Original Interface (`/`)
*Features*:
- ✅ Structured form for customer profiles
- ✅ Natural language query interface
- ✅ Real-time eligibility checking
- ✅ Beautiful, responsive design

#### 🆕 Chat Interface (`/chat`)
*Features*:
- 💬 Multi-turn conversations with memory
- 🔄 Continue previous conversations
- 📜 Load conversation history
- 🎨 Modern chat UI (message bubbles)
- 💾 Sessions persisted in database

### REST API Examples

#### Check Eligibility (Structured)

```bash
curl -X POST http://localhost:8000/api/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "birth_date": "1985-05-15",
    "health_conditions": ["diabetes"],
    "occupation": "software engineer",
    "insurance_type": "life"
  }'
```

**Response:**
```json
{
  "success": true,
  "analysis": "Based on the customer profile (40 years old, software engineer, with diabetes), here's the eligibility analysis:\n\n✓ Generali: Eligible - Premium €75/month\n✓ AXA: Eligible - Premium €80/month\n✗ UnipolSai: Not eligible (health conditions)\n..."
}
```

#### Natural Language Query

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Can a 35-year-old teacher get auto insurance? Compare all providers."
  }'
```

**Response:**
```json
{
  "success": true,
  "answer": "Yes, a 35-year-old teacher can get auto insurance from all 4 providers. Here's the comparison:\n\n1. Generali: €45/month (low risk)\n2. AXA: €50/month\n3. UnipolSai: €48/month\n4. Allianz: €47/month\n\nBest option: Generali at €45/month"
}
```

#### List Available Providers

```bash
curl http://localhost:8000/api/providers
```

**Response:**
```json
{
  "providers": [
    {
      "code": "generali",
      "name": "Generali",
      "country": "IT",
      "products": ["life", "auto", "home", "health"]
    },
    ...
  ],
  "total": 4
}
```

#### 🆕 Session-based Query (with conversation memory)

**First message (creates session):**
```bash
curl -X POST http://localhost:8000/api/v2/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "I am 35 years old, can I get life insurance?"
  }'
```

**Response:**
```json
{
  "answer": "Yes! At 35 years old, you're eligible for life insurance...",
  "session_key": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "abc123",
  "message_count": 2,
  "is_new_session": true
}
```

**Follow-up message (agent remembers context!):**
```bash
curl -X POST http://localhost:8000/api/v2/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What about health insurance?",
    "session_key": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Response:**
```json
{
  "answer": "Since you're 35 years old (from our previous conversation), let me check health insurance eligibility...",
  "session_key": "550e8400-e29b-41d4-a716-446655440000",
  "session_id": "abc123",
  "message_count": 4,
  "is_new_session": false
}
```

#### 🆕 Load Conversation History

```bash
curl http://localhost:8000/api/v2/conversation/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "session_id": "abc123",
  "messages": [
    {
      "role": "user",
      "content": "I am 35 years old, can I get life insurance?",
      "created_at": "2024-10-16T21:00:00"
    },
    {
      "role": "assistant",
      "content": "Yes! At 35 years old...",
      "created_at": "2024-10-16T21:00:05"
    },
    ...
  ],
  "session_info": {
    "message_count": 4,
    "status": "active"
  }
}
```

#### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_ready": true,
  "message": "Agent is ready"
}
```

### Python API

```python
from app.agent import create_agent

# Create agent
agent = create_agent(verbose=True)

# Ask a question
response = agent.query("""
Can a 35-year-old software engineer get life insurance?
Compare all providers and estimate costs.
""")

print(response)
```

### Structured API

```python
from app.agent import EligibilityAgent

agent = EligibilityAgent()

# Structured input
result = agent.check_eligibility({
    'birth_date': '1990-05-15',
    'health_conditions': [],
    'occupation': 'software engineer',
    'insurance_type': 'life'
})

print(result['output'])
```

## 🧰 Available Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `calculate_age` | Convert birth date to age | `1990-01-01` → 35 |
| `assess_risk_category` | Evaluate customer risk | `{age: 35, occupation: "office"}` → "low" |
| `estimate_premium` | Calculate monthly premium | `("life", 35, "low")` → €50 |
| `check_provider_eligibility` | Check provider rules | `("generali", "life", 35, "low")` → eligible |
| `list_available_providers` | Get all providers | → `["generali", "axa", ...]` |
| `get_provider_details` | Get provider info | `"generali"` → full details |
| `update_provider_rules` | Update rules (admin) | Change age limits, premiums, etc. |

## 📊 Provider Rules (Dynamic JSON)

Provider rules are stored in `data/providers/*.json`:

```json
{
  "provider_name": "Generali",
  "provider_code": "generali",
  "country": "IT",
  "products": {
    "life": {
      "age_min": 18,
      "age_max": 70,
      "max_risk": "high",
      "base_premium": 50.0
    }
  }
}
```

**Benefits**:
- ✅ Update rules without code changes
- ✅ Add new providers by adding JSON files
- ✅ Version control for rule changes
- ✅ Business users can update rules

## 🧪 Testing

**Test Coverage**: 13/13 API integration tests passing ✅

```bash
# API integration tests (mocked, no API key required)
pytest tests/test_api.py -v
# Tests: health check, providers, eligibility, queries, error handling, CORS

# Unit tests (no API key required)
python test_tools.py              # Test individual tools
python test_provider_loader.py    # Test JSON loading
python test_dynamic_tools.py      # Test dynamic features

# E2E tests (requires API key)
python test_agent.py              # Test full agent with real LLM calls
```

**What's tested:**
- ✅ FastAPI endpoints (POST/GET)
- ✅ Request validation (Pydantic models)
- ✅ Error handling (4xx, 5xx)
- ✅ Tool execution (calculate_age, assess_risk, etc.)
- ✅ Provider data loading (JSON)
- ✅ Agent orchestration (LangChain + Claude)

## 🎓 Learning Outcomes

This project demonstrates:

1. **LangChain Agent Patterns**
   - Tool creation with `@tool` decorator
   - Agent orchestration with `create_tool_calling_agent`
   - ReAct pattern (Reasoning + Acting)

2. **Production Architecture**
   - Separation of concerns (tools, agent, data)
   - Dynamic configuration (JSON rules)
   - Error handling and validation
   - Comprehensive testing

3. **GenAI Engineering Skills**
   - Prompt engineering (system prompts)
   - Tool design (when to use tools vs. LLM knowledge)
   - Agent debugging (verbose mode)
   - Cost optimization (temperature=0, structured inputs)

## 🚧 Future Enhancements

- [x] FastAPI REST API ✅
- [x] Interactive HTML frontend ✅
- [x] Comprehensive testing suite ✅
- [ ] Conversation memory (multi-turn dialogues)
- [ ] Database integration (PostgreSQL)
- [ ] Provider API integration (real-time rules)
- [ ] Multi-language support
- [ ] PDF document generation (policy quotes)
- [ ] Authentication & authorization
- [ ] Deployment (Docker + Railway/Render)

## 📝 License

MIT

---

**Built with**: Python 3.11 • LangChain 0.3.27 • Claude 3.5 Sonnet • FastAPI • PostgreSQL 15 • Docker
