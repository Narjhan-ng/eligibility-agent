# 🏥 Insurance Eligibility Agent

AI-powered agent for checking insurance eligibility across multiple Italian providers using LangChain and Claude.

## 🎯 Overview

This project demonstrates a **production-ready AI agent** that:
- ✅ Checks insurance eligibility with 4 major Italian providers (Generali, UnipolSai, Allianz, AXA)
- ✅ Calculates risk profiles and premium estimates
- ✅ Loads provider rules dynamically from JSON files
- ✅ Orchestrates multiple tools autonomously to answer complex queries

**Key Learning**: This is a **GenAI Engineering** project focused on agent orchestration, not machine learning.

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
- **JSON** - Dynamic provider rule storage
- **FastAPI** (planned) - REST API

## 📁 Project Structure

```
eligibility-agent/
├── app/
│   ├── agent.py              # Main agent orchestration
│   ├── tools.py              # 7 LangChain tools
│   └── provider_loader.py    # Dynamic JSON rule loading
├── data/
│   └── providers/            # Provider rules (JSON)
│       ├── generali.json
│       ├── unipolsai.json
│       ├── allianz.json
│       └── axa.json
├── tests/
│   ├── test_tools.py         # Unit tests for tools
│   ├── test_provider_loader.py
│   ├── test_dynamic_tools.py
│   └── test_agent.py         # Agent integration tests
├── .env                      # API keys (not in git)
├── requirements.txt
└── README.md
```

## 🚀 Setup

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

### 3. Test Tools (No API Key Required)

```bash
# Test individual tools
python test_tools.py

# Test provider loader
python test_provider_loader.py

# Test dynamic tools
python test_dynamic_tools.py
```

### 4. Test Agent (Requires API Key)

```bash
python test_agent.py
```

## 💡 Usage Examples

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

```bash
# Test all components
python test_tools.py              # Test individual tools
python test_provider_loader.py    # Test JSON loading
python test_dynamic_tools.py      # Test dynamic features
python test_agent.py              # Test full agent (requires API key)
```

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

- [ ] FastAPI REST API
- [ ] Conversation memory (multi-turn dialogues)
- [ ] Database integration (PostgreSQL)
- [ ] Provider API integration (real-time rules)
- [ ] Multi-language support
- [ ] PDF document generation (policy quotes)
- [ ] Authentication & authorization
- [ ] Deployment (Docker + Railway/Render)

## 📝 License

MIT

## 👤 Author

**Nicola Gnasso**
- Learning project for AI Engineering portfolio
- Part of 6-8 week intensive AI Engineer roadmap
- Goal: €45-55k AI Engineer position

---

**Built with**: LangChain, Claude, Python 3.11
**Learning Focus**: Agent orchestration, production patterns, tool design
