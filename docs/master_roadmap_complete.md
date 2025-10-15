# 📘 Master Document: AI Engineer Roadmap Completa

**Versione**: 1.0  
**Data**: Ottobre 2025  
**Studente**: Nicola Gnasso  
**Obiettivo**: AI Engineer €45-55k in 6-8 settimane  
**Progetto Core**: Insurance Comparison CRM

---

## 👤 PROFILO STUDENTE

### Background
- **Nome**: Nicola Gnasso
- **Esperienza**: 17 anni IT/Infrastructure
- **Educazione**: Laurea Magistrale Ingegneria Informatica
- **Skills attuali**: PHP, SQL, Bash, C/C++, Linux, Git, Docker basics
- **Esperienza BI**: Data Warehousing, SQL avanzato
- **Current RAL**: €30k
- **Target RAL**: €45-55k (+50-80%)
- **Location**: Aversa (CE), Italia

### Progetti Esistenti
- **Webapp Telco completa** (produzione, non pubblicabile)
- **n8n workflows** su GitHub
- **Sviluppo con Claude Code** (orchestrator + debugger)

### Gap da Colmare
- ❌ Portfolio pubblico progetti AI
- ❌ LangChain/LangGraph formalizzazione
- ❌ Visibilità LinkedIn/community
- ❌ Esperienza "AI Engineer" formale

---

## 🎯 OBIETTIVO FINALE

### Target Position
**AI Engineer** (non MLOps - no esperienza infra production richiesta)

### Salari Mercato Italia 2025
- Entry AI Engineer: €35-45k
- Mid AI Engineer: €45-60k
- Senior AI Engineer: €60-80k+

### Timeline
**6-8 settimane intensive** = 150-200h totali

### Success Criteria
- 7-8 progetti portfolio pubblico
- 1 showcase production-level
- 30+ applications inviate
- 5+ interview rounds
- 1+ job offer target

---

## 🏗️ PROGETTO CENTRALE: INSURANCE CRM

### Concept
Clone webapp Telco esistente → Insurance domain
Dimostra: domain adaptation, LangChain integration, production architecture

### Architecture Originale (Telco)

**Database Structure**:
- `crm` (primary): leads, offers, contracts, commissions, users
- `coverage` (secondary): provider coverage data (TIM, OpenFiber, Fastweb, NHM)

**Core Modules** (15 totali):
1. Leads - Customer lifecycle management
2. Coverage - Network availability checking
3. Offers - Dynamic quote generation
4. Contracts - PDF document generation
5. Commissions - Multi-tier compensation
6. Web & Hosting - Additional services
7. Inventory - Device management
8. Dashboard - Role-based analytics
9. Reports - Business intelligence
10. Documents - File management
11. Actions - Task automation
12. Products - Catalog management
13. Validation - Data quality
14. Auth - Security & access
15. Search - Global search

**Tech Stack**:
- PHP 8.0 + custom MVC framework
- MySQL dual database
- mPDF for documents
- Repository pattern
- CSRF protection
- Role-based access (Admin/Manager/Agent/Partner)

### Domain Mapping: Telco → Insurance

| Telco Concept | Insurance Equivalent |
|---------------|---------------------|
| **Lead telecomunicazioni** | Insurance prospect (individual/family/business) |
| **Coverage check (4 providers)** | Policy eligibility check (Generali/UnipolSai/Allianz/AXA) |
| **Tecnologie (FTTH/FTTC/ADSL)** | Insurance types (Life/Auto/Home/Health) |
| **Offerta internet + devices** | Policy quote with coverage options |
| **Contratto telecomunicazioni** | Insurance policy agreement |
| **Commissione agente/manager/partner** | Broker/manager/affiliate commission |
| **Web & Hosting services** | Financial advisory services |
| **Inventory dispositivi** | Policy catalog management |
| **Coverage database** | Eligibility rules database |

### Insurance CRM - Database Schema

```sql
-- =======================
-- PROSPECTS (ex Leads)
-- =======================
CREATE TABLE prospects (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type ENUM('individual', 'family', 'business') NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birth_date DATE,
    email VARCHAR(255),
    phone VARCHAR(20),
    tax_code VARCHAR(20),
    status ENUM('new', 'contacted', 'quoted', 'policy_signed', 'declined') DEFAULT 'new',
    risk_category ENUM('low', 'medium', 'high'),
    assigned_broker INT,
    created_by INT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (assigned_broker) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id),
    
    INDEX idx_prospects_status (status),
    INDEX idx_prospects_broker (assigned_broker)
);

-- =======================
-- ELIGIBILITY CACHE (ex Coverage)
-- =======================
CREATE TABLE eligibility_cache (
    id INT PRIMARY KEY AUTO_INCREMENT,
    provider ENUM('generali', 'unipolsai', 'allianz', 'axa') NOT NULL,
    insurance_type ENUM('life', 'auto', 'home', 'health') NOT NULL,
    age_min INT,
    age_max INT,
    risk_category VARCHAR(20),
    is_eligible BOOLEAN DEFAULT TRUE,
    base_premium DECIMAL(10,2),
    coverage_max DECIMAL(10,2),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_eligibility_provider (provider, insurance_type),
    INDEX idx_eligibility_age (age_min, age_max)
);

-- =======================
-- QUOTES (ex Offers)
-- =======================
CREATE TABLE quotes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prospect_id INT NOT NULL,
    provider VARCHAR(50) NOT NULL,
    insurance_type VARCHAR(50) NOT NULL,
    monthly_premium DECIMAL(10,2) NOT NULL,
    annual_premium DECIMAL(10,2) NOT NULL,
    coverage_amount DECIMAL(10,2) NOT NULL,
    deductible DECIMAL(10,2),
    status ENUM('draft', 'sent', 'accepted', 'rejected', 'expired') DEFAULT 'draft',
    valid_until DATE,
    items JSON COMMENT 'Coverage details and add-ons',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP NULL,
    
    FOREIGN KEY (prospect_id) REFERENCES prospects(id) ON DELETE CASCADE,
    
    INDEX idx_quotes_prospect (prospect_id),
    INDEX idx_quotes_status (status)
);

-- =======================
-- POLICIES (ex Contracts)
-- =======================
CREATE TABLE policies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    quote_id INT NOT NULL,
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
    pdf_path VARCHAR(255),
    signed_at TIMESTAMP,
    renewal_date DATE,
    
    FOREIGN KEY (quote_id) REFERENCES quotes(id),
    
    INDEX idx_policies_number (policy_number),
    INDEX idx_policies_renewal (renewal_date)
);

-- =======================
-- COMMISSIONS
-- =======================
CREATE TABLE commissions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    prospect_id INT NOT NULL,
    broker_id INT NOT NULL,
    manager_id INT,
    affiliate_id INT,
    commission_type ENUM('initial', 'renewal_year1', 'renewal_recurring', 'referral') NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    percentage DECIMAL(5,2) NOT NULL,
    base_amount DECIMAL(10,2) NOT NULL,
    status ENUM('pending', 'approved', 'paid') DEFAULT 'pending',
    period_year INT,
    period_month INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    paid_at TIMESTAMP NULL,
    
    FOREIGN KEY (prospect_id) REFERENCES prospects(id),
    FOREIGN KEY (broker_id) REFERENCES users(id),
    FOREIGN KEY (manager_id) REFERENCES users(id),
    FOREIGN KEY (affiliate_id) REFERENCES users(id),
    
    INDEX idx_commissions_broker (broker_id, period_year, period_month),
    INDEX idx_commissions_prospect (prospect_id)
);

-- =======================
-- ADVISORY SERVICES (ex Web & Hosting)
-- =======================
CREATE TABLE advisory_offers (
    id VARCHAR(20) PRIMARY KEY,
    prospect_id INT NOT NULL,
    service_type ENUM('financial_planning', 'investment', 'retirement', 'estate_planning') NOT NULL,
    status ENUM('draft', 'sent', 'accepted', 'closed') DEFAULT 'draft',
    total_amount DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (prospect_id) REFERENCES prospects(id) ON DELETE CASCADE
);

-- =======================
-- USERS (unchanged structure)
-- =======================
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'head_of_sales', 'manager', 'broker', 'affiliate') NOT NULL,
    supervisor_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (supervisor_id) REFERENCES users(id)
);
```

### Insurance CRM - API Endpoints

```
# Prospects Management
GET    /api/prospects              # List all prospects
GET    /api/prospects/:id          # Get prospect details
POST   /api/prospects              # Create new prospect
PUT    /api/prospects/:id          # Update prospect
DELETE /api/prospects/:id          # Delete prospect
PUT    /api/prospects/:id/status   # Update status

# Eligibility Checking
POST   /api/eligibility/check      # Check eligibility (all providers)
GET    /api/eligibility/providers  # List providers
POST   /api/eligibility/calculate  # Calculate premium estimate

# Quote Generation
POST   /api/quotes/generate        # Generate multi-provider quotes
GET    /api/quotes/:id             # Get quote details
POST   /api/quotes/:id/accept      # Accept quote
POST   /api/quotes/:id/send        # Send quote via email

# Policy Management
POST   /api/policies/generate      # Generate policy from quote
GET    /api/policies/:id           # Get policy details
GET    /api/policies/:id/pdf       # Download policy PDF

# Commissions
GET    /api/commissions/dashboard  # Commission dashboard
POST   /api/commissions/calculate  # Calculate commissions
GET    /api/commissions/report     # Generate report

# Advisory Services
POST   /api/advisory/create        # Create advisory offer
GET    /api/advisory/:id           # Get advisory details
```

---

## 📅 ROADMAP DETTAGLIATA 6-8 SETTIMANE

---

## 🗓️ SETTIMANA 1: Foundation & Quick Wins

### Obiettivi Week 1
- GitHub portfolio live
- 2 progetti pubblici funzionanti
- LinkedIn attivo
- LangChain basics

### Daily Routine
- **Mattina (1h)**: Learning LangChain docs
- **Pranzo (30m)**: LinkedIn + community
- **Sera (1h)**: Coding + documentation

---

### 📅 GIORNO 1: Setup & Networking

#### Mattina (1h): GitHub Setup

**Task 1: Create Repository**
```bash
# Create main portfolio repo
mkdir ai-engineering-portfolio
cd ai-engineering-portfolio
git init

# Create structure
mkdir -p projects/{policy-rag,eligibility-agent,insurance-crm}
mkdir -p docs
touch README.md

# Initial commit
git add .
git commit -m "Initial commit: AI Engineering Portfolio"
```

**Task 2: Professional README**
```markdown
# AI Engineering Portfolio

## About Me
AI Engineer specializing in LLM orchestration and multi-agent systems.
Background: 17 years IT infrastructure, transitioning to AI Engineering.

## Tech Stack
- **AI/ML**: LangChain, LangGraph, Claude API
- **Backend**: Python, FastAPI, PHP
- **Database**: MySQL, ChromaDB
- **Tools**: Git, Docker, n8n

## Projects

### 1. Insurance Policy RAG System
Q&A system over insurance policy documents using RAG.
[View Project →](./projects/policy-rag)

### 2. Eligibility Checker Agent
Multi-tool agent for insurance eligibility verification.
[View Project →](./projects/eligibility-agent)

### 3. Insurance Comparison CRM (In Development)
Full-stack insurance CRM with multi-agent orchestration.
[View Project →](./projects/insurance-crm)

## Contact
- LinkedIn: [Your Profile]
- Email: nicola.gnasso@gmail.com
- Location: Aversa, Italy
```

**Task 3: GitHub Profile Optimization**
- Add profile photo
- Bio: "AI Engineer | LLM Orchestration & Multi-Agent Systems | 17y IT Background"
- Pin portfolio repo
- Enable GitHub Pages (optional)

#### Pausa Pranzo (30m): LinkedIn Optimization

**Profile Updates**:
- **Headline**: "AI Engineer | LLM Orchestration & Multi-Agent Systems"
- **About** (draft):
```
AI Engineer specializing in LLM orchestration, RAG systems, and multi-agent workflows.

17 years IT infrastructure background, now focused on building production-ready AI applications with LangChain and Claude API.

Currently building: Insurance Comparison CRM with multi-agent orchestration

Tech stack: Python, LangChain, LangGraph, FastAPI, Claude API
```

**Post #1**:
```
🚀 Starting my AI Engineering portfolio in public

After 17 years in IT infrastructure, I'm transitioning to AI Engineering.

Over the next 6 weeks, I'll build and share:
• RAG systems with LangChain
• Multi-agent workflows
• Production-ready AI applications

First project: Insurance Policy Q&A with RAG

Follow along as I document the journey!

#AIEngineering #LangChain #BuildInPublic
```

#### Sera (1h): Community Setup

**Discord Servers to Join**:
1. LangChain Official
2. n8n Community
3. LocalLLaMA
4. AI Engineers

**Reddit Communities**:
- r/LangChain
- r/LocalLLaMA
- r/MachineLearning
- r/artificial

**First Actions**:
- Introduce yourself in #introductions
- Read pinned messages
- Bookmark useful resources
- Follow 20 AI engineers on LinkedIn (Italian market)

---

### 📅 GIORNO 2: Progetto 1 Setup - Insurance Policy RAG

#### Mattina (1h): Architecture & Setup

**Project Structure**:
```
projects/policy-rag/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── app/
│   ├── main.py
│   ├── services/
│   │   ├── document_processor.py
│   │   └── rag_service.py
│   └── api/
│       └── routes.py
├── data/
│   └── policies/  # PDF files
├── static/
│   ├── css/
│   └── js/
└── templates/
    └── index.html
```

**Requirements Installation**:
```bash
cd projects/policy-rag

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install fastapi uvicorn anthropic langchain langchain-anthropic \
    langchain-community chromadb pypdf python-multipart python-dotenv
```

**requirements.txt**:
```
fastapi==0.104.1
uvicorn==0.24.0
anthropic==0.7.8
langchain==0.1.0
langchain-anthropic==0.1.1
langchain-community==0.0.10
chromadb==0.4.18
pypdf==3.17.1
python-multipart==0.0.6
python-dotenv==1.0.0
```

**.env.example**:
```
ANTHROPIC_API_KEY=your_api_key_here
CHROMA_PERSIST_DIR=./chroma_db
```

**README.md** (initial):
```markdown
# Insurance Policy RAG System

Q&A system for insurance policy documents using RAG (Retrieval Augmented Generation).

## Features
- Upload multiple policy PDFs
- Semantic search over policy content
- Answer questions with source citations
- Compare policies side-by-side

## Tech Stack
- FastAPI
- LangChain
- ChromaDB
- Claude 3.5 Sonnet
- PyPDF

## Setup
\`\`\`bash
pip install -r requirements.txt
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
uvicorn app.main:app --reload
\`\`\`

## Usage
1. Navigate to http://localhost:8000
2. Upload insurance policy PDFs
3. Ask questions about coverage, terms, etc.
```

#### Pausa Pranzo (30m): Learning

**LangChain Docs to Read**:
- Document Loaders: https://python.langchain.com/docs/modules/data_connection/document_loaders/
- Text Splitters: https://python.langchain.com/docs/modules/data_connection/document_transformers/
- Vector Stores: https://python.langchain.com/docs/modules/data_connection/vectorstores/
- RAG Tutorial: https://python.langchain.com/docs/tutorials/rag/

#### Sera (1h): Core Implementation

**app/services/document_processor.py**:
```python
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_anthropic import AnthropicEmbeddings
import os

class DocumentProcessor:
    def __init__(self, persist_directory="./chroma_db"):
        self.persist_directory = persist_directory
        self.embeddings = AnthropicEmbeddings(
            model="claude-3-sonnet-20240229"
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def process_pdf(self, pdf_path):
        """Load and process a PDF file"""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Split documents
        splits = self.text_splitter.split_documents(documents)
        
        return splits
    
    def add_to_vectorstore(self, documents):
        """Add documents to ChromaDB"""
        vectorstore = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
        return vectorstore
    
    def get_vectorstore(self):
        """Load existing vectorstore"""
        vectorstore = Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
        return vectorstore
```

**app/services/rag_service.py**:
```python
from langchain_anthropic import ChatAnthropic
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

class RAGService:
    def __init__(self, vectorstore):
        self.vectorstore = vectorstore
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0
        )
        
        # Custom prompt for insurance domain
        self.prompt_template = """You are an insurance policy expert. 
        Use the following policy documents to answer the question.
        If you don't know the answer, say so. Always cite the source.
        
        Context: {context}
        
        Question: {question}
        
        Answer with policy details and source citations:"""
        
        self.prompt = PromptTemplate(
            template=self.prompt_template,
            input_variables=["context", "question"]
        )
    
    def query(self, question):
        """Query the RAG system"""
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": self.prompt}
        )
        
        result = qa_chain.invoke({"query": question})
        
        return {
            "answer": result["result"],
            "sources": [
                {
                    "content": doc.page_content[:200],
                    "metadata": doc.metadata
                }
                for doc in result["source_documents"]
            ]
        }
```

---

### 📅 GIORNO 3: Progetto 1 Complete - Policy RAG

#### Mattina (1h): API Implementation

**app/main.py**:
```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
import os
import shutil

from app.services.document_processor import DocumentProcessor
from app.services.rag_service import RAGService

app = FastAPI(title="Insurance Policy RAG")

# Setup
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

doc_processor = DocumentProcessor()
rag_service = None

class QueryRequest(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_policy(file: UploadFile = File(...)):
    """Upload and process insurance policy PDF"""
    try:
        # Save file
        upload_dir = "data/policies"
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process document
        documents = doc_processor.process_pdf(file_path)
        vectorstore = doc_processor.add_to_vectorstore(documents)
        
        global rag_service
        rag_service = RAGService(vectorstore)
        
        return {
            "message": "Policy uploaded successfully",
            "filename": file.filename,
            "chunks": len(documents)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_policy(query: QueryRequest):
    """Query the policy documents"""
    if rag_service is None:
        raise HTTPException(
            status_code=400,
            detail="No policies uploaded yet"
        )
    
    try:
        result = rag_service.query(query.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

#### Pausa Pranzo (30m): Frontend Template

**templates/index.html**:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Insurance Policy RAG</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            padding: 20px;
            max-width: 1200px;
            margin: 0 auto;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; margin-bottom: 20px; }
        .upload-section, .query-section {
            margin-bottom: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 4px;
        }
        input[type="file"], input[type="text"], button {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 16px;
        }
        button {
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover { background: #0056b3; }
        .result {
            margin-top: 20px;
            padding: 20px;
            background: #e9ecef;
            border-radius: 4px;
            border-left: 4px solid #007bff;
        }
        .sources {
            margin-top: 15px;
            padding: 15px;
            background: white;
            border-radius: 4px;
        }
        .source-item {
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-left: 3px solid #28a745;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏥 Insurance Policy RAG System</h1>
        
        <div class="upload-section">
            <h2>Upload Policy Document</h2>
            <input type="file" id="policyFile" accept=".pdf">
            <button onclick="uploadPolicy()">Upload & Process</button>
            <div id="uploadStatus"></div>
        </div>
        
        <div class="query-section">
            <h2>Ask Questions</h2>
            <input type="text" id="questionInput" placeholder="What does this policy cover?">
            <button onclick="askQuestion()">Search</button>
            <div id="queryResult"></div>
        </div>
    </div>

    <script>
        async function uploadPolicy() {
            const fileInput = document.getElementById('policyFile');
            const statusDiv = document.getElementById('uploadStatus');
            
            if (!fileInput.files[0]) {
                statusDiv.innerHTML = '<p style="color: red;">Please select a file</p>';
                return;
            }
            
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);
            
            statusDiv.innerHTML = '<p>Processing...</p>';
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    statusDiv.innerHTML = `
                        <p style="color: green;">
                            ✓ ${data.message}<br>
                            Processed ${data.chunks} document chunks
                        </p>
                    `;
                } else {
                    statusDiv.innerHTML = `<p style="color: red;">Error: ${data.detail}</p>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        }
        
        async function askQuestion() {
            const question = document.getElementById('questionInput').value;
            const resultDiv = document.getElementById('queryResult');
            
            if (!question) {
                resultDiv.innerHTML = '<p style="color: red;">Please enter a question</p>';
                return;
            }
            
            resultDiv.innerHTML = '<p>Searching...</p>';
            
            try {
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    let sourcesHTML = '';
                    if (data.sources && data.sources.length > 0) {
                        sourcesHTML = '<div class="sources"><h3>Sources:</h3>';
                        data.sources.forEach((source, idx) => {
                            sourcesHTML += `
                                <div class="source-item">
                                    <strong>Source ${idx + 1}:</strong><br>
                                    ${source.content}...
                                </div>
                            `;
                        });
                        sourcesHTML += '</div>';
                    }
                    
                    resultDiv.innerHTML = `
                        <div class="result">
                            <h3>Answer:</h3>
                            <p>${data.answer}</p>
                            ${sourcesHTML}
                        </div>
                    `;
                } else {
                    resultDiv.innerHTML = `<p style="color: red;">Error: ${data.detail}</p>`;
                }
            } catch (error) {
                resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
```

#### Sera (1h): Testing & Documentation

**Test locally**:
```bash
# Run application
uvicorn app.main:app --reload

# Test in browser: http://localhost:8000
# Upload sample insurance PDF
# Ask questions like:
# - "What is the coverage limit for home insurance?"
# - "What are the exclusions?"
# - "How do I file a claim?"
```

**Update README with screenshots**:
- Take screenshots of interface
- Add to README
- Document API endpoints

**Commit**:
```bash
git add .
git commit -m "feat: complete insurance policy RAG system"
git push origin main
```

---

### 📅 GIORNO 4-5: Progetto 2 - Eligibility Checker Agent

#### Giorno 4 Mattina: Agent Architecture

**Project Setup**:
```bash
mkdir -p projects/eligibility-agent/{app,tests}
cd projects/eligibility-agent
python3 -m venv venv
source venv/bin/activate

pip install fastapi uvicorn anthropic langchain langchain-anthropic python-dotenv
```

**app/tools.py** - Define Tools:
```python
from langchain.tools import tool
from datetime import datetime
from typing import Dict, Any

@tool
def calculate_age(birth_date: str) -> int:
    """
    Calculate age from birth date.
    Args:
        birth_date: Date in format YYYY-MM-DD
    Returns:
        Age in years
    """
    birth = datetime.strptime(birth_date, "%Y-%m-%d")
    today = datetime.today()
    age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    return age

@tool
def assess_risk_category(profile: Dict[str, Any]) -> str:
    """
    Assess risk category based on customer profile.
    Args:
        profile: Dict with age, health_conditions, occupation, etc.
    Returns:
        Risk category: 'low', 'medium', or 'high'
    """
    age = profile.get('age', 0)
    health_conditions = profile.get('health_conditions', [])
    occupation = profile.get('occupation', 'office')
    
    risk_score = 0
    
    # Age factor
    if age < 25 or age > 65:
        risk_score += 2
    elif age > 50:
        risk_score += 1
    
    # Health conditions
    high_risk_conditions = ['diabetes', 'heart_disease', 'cancer_history']
    if any(cond in health_conditions for cond in high_risk_conditions):
        risk_score += 3
    elif health_conditions:
        risk_score += 1
    
    # Occupation
    high_risk_jobs = ['construction', 'mining', 'firefighter']
    if occupation.lower() in high_risk_jobs:
        risk_score += 2
    
    if risk_score >= 5:
        return 'high'
    elif risk_score >= 2:
        return 'medium'
    else:
        return 'low'

@tool
def estimate_premium(insurance_type: str, age: int, risk_category: str) -> float:
    """
    Estimate monthly insurance premium.
    Args:
        insurance_type: 'life', 'auto', 'home', or 'health'
        age: Customer age
        risk_category: 'low', 'medium', or 'high'
    Returns:
        Estimated monthly premium in euros
    """
    base_premiums = {
        'life': 50,
        'auto': 80,
        'home': 60,
        'health': 100
    }
    
    base = base_premiums.get(insurance_type, 50)
    
    # Age multiplier
    age_multiplier = 1.0
    if age < 25:
        age_multiplier = 1.5
    elif age > 50:
        age_multiplier = 1.2 + (age - 50) * 0.02
    
    # Risk multiplier
    risk_multipliers = {
        'low': 1.0,
        'medium': 1.3,
        'high': 1.8
    }
    risk_mult = risk_multipliers.get(risk_category, 1.0)
    
    premium = base * age_multiplier * risk_mult
    return round(premium, 2)

@tool
def check_provider_eligibility(
    provider: str,
    insurance_type: str,
    age: int,
    risk_category: str
) -> Dict[str, Any]:
    """
    Check eligibility with specific insurance provider.
    Args:
        provider: 'generali', 'unipolsai', 'allianz', or 'axa'
        insurance_type: 'life', 'auto', 'home', or 'health'
        age: Customer age
        risk_category: 'low', 'medium', or 'high'
    Returns:
        Eligibility result with details
    """
    # Provider rules (simplified)
    rules = {
        'generali': {
            'life': {'age_min': 18, 'age_max': 70, 'max_risk': 'high'},
            'auto': {'age_min': 18, 'age_max': 75, 'max_risk': 'high'},
            'home': {'age_min': 18, 'age_max': 80, 'max_risk': 'high'},
            'health': {'age_min': 18, 'age_max': 65, 'max_risk': 'medium'}
        },
        'unipolsai': {
            'life': {'age_min': 18, 'age_max': 65, 'max_risk': 'medium'},
            'auto': {'age_min': 21, 'age_max': 75, 'max_risk': 'high'},
            'home': {'age_min': 18, 'age_max': 80, 'max_risk': 'high'},
            'health': {'age_min': 18, 'age_max': 60, 'max_risk': 'medium'}
        },
        'allianz': {
            'life': {'age_min': 21, 'age_max': 68, 'max_risk': 'medium'},
            'auto': {'age_min': 23, 'age_max': 75, 'max_risk': 'high'},
            'home': {'age_min': 18, 'age_max': 75, 'max_risk': 'high'},
            'health': {'age_min': 21, 'age_max': 65, 'max_risk': 'medium'}
        },
        'axa': {
            'life': {'age_min': 18, 'age_max': 72, 'max_risk': 'medium'},
            'auto': {'age_min': 20, 'age_max': 75, 'max_risk': 'high'},
            'home': {'age_min': 18, 'age_max': 80, 'max_risk': 'high'},
            'health': {'age_min': 18, 'age_max': 67, 'max_risk': 'medium'}
        }
    }
    
    provider_rules = rules.get(provider, {}).get(insurance_type)
    
    if not provider_rules:
        return {
            'eligible': False,
            'reason': f'Provider {provider} does not offer {insurance_type} insurance'
        }
    
    # Check age
    if age < provider_rules['age_min'] or age > provider_rules['age_max']:
        return {
            'eligible': False,
            'reason': f'Age {age} is outside acceptable range ({provider_rules["age_min"]}-{provider_rules["age_max"]})'
        }
    
    # Check risk
    risk_levels = ['low', 'medium', 'high']
    max_risk_idx = risk_levels.index(provider_rules['max_risk'])
    current_risk_idx = risk_levels.index(risk_category)
    
    if current_risk_idx > max_risk_idx:
        return {
            'eligible': False,
            'reason': f'Risk category {risk_category} exceeds maximum accepted risk ({provider_rules["max_risk"]})'
        }
    
    return {
        'eligible': True,
        'provider': provider,
        'insurance_type': insurance_type,
        'reason': 'Customer meets all eligibility criteria'
    }
```

#### Giorno 4 Sera: Agent Implementation

**app/agent.py**:
```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.tools import (
    calculate_age,
    assess_risk_category,
    estimate_premium,
    check_provider_eligibility
)

class EligibilityAgent:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0
        )
        
        self.tools = [
            calculate_age,
            assess_risk_category,
            estimate_premium,
            check_provider_eligibility
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an insurance eligibility expert.
            
            Your role is to help customers understand their insurance eligibility
            and find the best insurance options for their needs.
            
            When a customer provides information:
            1. Calculate their age if birth date is given
            2. Assess their risk category based on profile
            3. Check eligibility with all major providers (Generali, UnipolSai, Allianz, AXA)
            4. Estimate premiums for eligible options
            5. Provide clear recommendations
            
            Always be transparent about eligibility criteria and explain why
            a customer may or may not be eligible with certain providers.
            """),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_tool_calling_agent(
            self.llm,
            self.tools,
            self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def check_eligibility(self, customer_info: dict) -> dict:
        """
        Check customer eligibility for insurance
        """
        # Format input for agent
        input_text = f"""
        Customer Profile:
        - Birth Date: {customer_info.get('birth_date', 'Not provided')}
        - Health Conditions: {customer_info.get('health_conditions', [])}
        - Occupation: {customer_info.get('occupation', 'Not specified')}
        - Insurance Type Interested: {customer_info.get('insurance_type', 'Not specified')}
        
        Please check eligibility with all major providers and provide recommendations.
        """
        
        result = self.agent_executor.invoke({
            "input": input_text
        })
        
        return {
            "output": result["output"],
            "customer_info": customer_info
        }
    
    def interactive_query(self, question: str, chat_history: list = None) -> dict:
        """
        Handle interactive questions about insurance eligibility
        """
        result = self.agent_executor.invoke({
            "input": question,
            "chat_history": chat_history or []
        })
        
        return result
```

#### Giorno 5 Mattina: API & Frontend

**app/main.py**:
```python
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.agent import EligibilityAgent

app = FastAPI(title="Insurance Eligibility Checker")

agent = EligibilityAgent()

class CustomerProfile(BaseModel):
    birth_date: str
    health_conditions: List[str] = []
    occupation: str
    insurance_type: str

class InteractiveQuery(BaseModel):
    question: str
    chat_history: Optional[List[Dict[str, str]]] = None

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Insurance Eligibility Checker</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            input, select, button {
                width: 100%;
                padding: 10px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            button {
                background: #007bff;
                color: white;
                border: none;
                cursor: pointer;
            }
            button:hover { background: #0056b3; }
            .result {
                margin-top: 20px;
                padding: 20px;
                background: #e9f5ff;
                border-radius: 4px;
                white-space: pre-wrap;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 Insurance Eligibility Checker</h1>
            
            <h2>Customer Profile</h2>
            <input type="date" id="birthDate" placeholder="Birth Date">
            <input type="text" id="healthConditions" placeholder="Health conditions (comma-separated)">
            <input type="text" id="occupation" placeholder="Occupation">
            <select id="insuranceType">
                <option value="life">Life Insurance</option>
                <option value="auto">Auto Insurance</option>
                <option value="home">Home Insurance</option>
                <option value="health">Health Insurance</option>
            </select>
            <button onclick="checkEligibility()">Check Eligibility</button>
            
            <div id="result"></div>
        </div>
        
        <script>
            async function checkEligibility() {
                const profile = {
                    birth_date: document.getElementById('birthDate').value,
                    health_conditions: document.getElementById('healthConditions').value.split(',').map(s => s.trim()).filter(s => s),
                    occupation: document.getElementById('occupation').value,
                    insurance_type: document.getElementById('insuranceType').value
                };
                
                const resultDiv = document.getElementById('result');
                resultDiv.innerHTML = '<p>Checking eligibility...</p>';
                
                try {
                    const response = await fetch('/check-eligibility', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(profile)
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        resultDiv.innerHTML = `<div class="result"><h3>Results:</h3><p>${data.output}</p></div>`;
                    } else {
                        resultDiv.innerHTML = `<p style="color: red;">Error: ${data.detail}</p>`;
                    }
                } catch (error) {
                    resultDiv.innerHTML = `<p style="color: red;">Error: ${error.message}</p>`;
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/check-eligibility")
async def check_eligibility(profile: CustomerProfile):
    """Check insurance eligibility for a customer profile"""
    try:
        result = agent.check_eligibility(profile.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def interactive_query(query: InteractiveQuery):
    """Ask questions about insurance eligibility"""
    try:
        result = agent.interactive_query(
            query.question,
            query.chat_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "ready"}
```

#### Giorno 5 Sera: Testing & Documentation

**Test Cases**:
```bash
# Run app
uvicorn app.main:app --reload

# Test scenarios:
# 1. Young person (25) with no health issues
# 2. Middle-aged (50) with diabetes
# 3. Senior (70) applying for life insurance
# 4. High-risk occupation (construction worker)
```

**README.md**:
```markdown
# Insurance Eligibility Checker Agent

Multi-tool AI agent for checking insurance eligibility across providers.

## Features
- Age calculation from birth date
- Risk assessment based on profile
- Multi-provider eligibility checking
- Premium estimation
- Interactive Q&A

## Tools
1. **calculate_age** - Age from birth date
2. **assess_risk_category** - Risk profiling
3. **estimate_premium** - Premium calculation
4. **check_provider_eligibility** - Provider-specific rules

## Providers Supported
- Generali
- UnipolSai
- Allianz
- AXA

## Tech Stack
- LangChain Agents
- Claude 3.5 Sonnet
- FastAPI
- Tool Calling Pattern

## Usage
\`\`\`bash
uvicorn app.main:app --reload
# Visit http://localhost:8000
\`\`\`
```

**Commit & Deploy**:
```bash
git add .
git commit -m "feat: multi-tool eligibility checker agent"
git push

# Deploy to Railway/Render (Week 1 optional, Week 2 mandatory)
```

---

### 📅 WEEKEND WEEK 1: Publishing & Networking

#### Sabato (3-4h): Polish Projects

**Tasks**:
- [ ] Clean code both projects
- [ ] Complete README with screenshots
- [ ] Add demo GIFs (use Peek on Linux / Kap on Mac)
- [ ] Add LICENSE files (MIT)
- [ ] Ensure all commits are clean
- [ ] Test both projects end-to-end

**Demo GIFs Creation**:
```bash
# Install Peek (Linux)
sudo apt install peek

# Install Kap (Mac)
brew install --cask kap

# Record:
# - Uploading PDF to RAG
# - Asking questions
# - Eligibility check workflow
```

#### Sabato Sera (2h): LinkedIn Content

**Post #2 - Policy RAG**:
```
🏥 Built an Insurance Policy RAG System

Upload policy PDFs, ask questions, get answers with source citations.

Tech stack:
• LangChain for document processing
• ChromaDB for vector storage
• Claude 3.5 Sonnet for generation
• FastAPI for the API

Why RAG matters in insurance:
✓ Instant policy information
✓ Accurate with citations
✓ Handles multiple documents
✓ Reduces manual research time

[Demo GIF]
[GitHub link]

#AIEngineering #LangChain #RAG #Insurance
```

**Post #3 - Eligibility Agent**:
```
🤖 Built a Multi-Tool Insurance Eligibility Agent

One agent, 4 tools, 4 providers checked automatically.

The agent:
• Calculates age & risk profile
• Checks eligibility with Generali, UnipolSai, Allianz, AXA
• Estimates premiums
• Explains reasoning

Built with LangChain's tool calling + Claude API.

Agent-based AI is perfect for insurance workflows:
complex rules, multiple data sources, clear decisions.

[Demo GIF]
[GitHub link]

#AIEngineering #LangChain #Agents #Insurance
```

#### Domenica (3-4h): Community Engagement & Week 2 Prep

**Community Actions**:
- [ ] Comment on 10 AI engineering posts
- [ ] Connect with 10 AI engineers (personalized invites)
- [ ] Share projects in Discord #showcase channels
- [ ] Answer 2-3 questions in communities (if you can)

**Week 2 Preparation**:
- [ ] Review Telco app architecture
- [ ] List all modules to port
- [ ] Create Insurance CRM project structure
- [ ] Design database schema (refine)
- [ ] Plan API endpoints
- [ ] Download insurance PDF samples for testing

---

### KPI Week 1 - CHECK ✓
- [ ] 2 progetti GitHub documentati
- [ ] 2 post LinkedIn pubblicati + engagement
- [ ] 30+ GitHub profile views
- [ ] 20+ nuove connessioni LinkedIn
- [ ] LangChain basics padroneggiati
- [ ] Community presence established

---

## 🗓️ SETTIMANA 2: Insurance CRM Foundation

### Obiettivi Week 2
- Database schema Insurance CRM
- Core API endpoints (Prospects, Eligibility)
- Repository pattern implementation
- n8n workflows documentation
- LangChain integration planning

---

### 📅 GIORNO 6: Database Setup & Repository Pattern

#### Mattina (1h): Database Implementation

**Create Database**:
```sql
-- Connect to MySQL
mysql -u root -p

-- Create databases
CREATE DATABASE insurance_crm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE eligibility_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create users
CREATE USER 'insurance_user'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON insurance_crm.* TO 'insurance_user'@'localhost';
GRANT ALL PRIVILEGES ON eligibility_data.* TO 'insurance_user'@'localhost';
FLUSH PRIVILEGES;

-- Use database
USE insurance_crm;

-- Import schema (from master document above)
-- Copy schema SQL and execute
```

**Project Structure**:
```
projects/insurance-crm/
├── app/
│   ├── Core/
│   │   ├── Database.php
│   │   ├── Auth.php
│   │   └── Session.php
│   ├── Modules/
│   │   ├── Prospects/
│   │   │   ├── ProspectsController.php
│   │   │   └── ProspectsRepository.php
│   │   ├── Eligibility/
│   │   │   ├── EligibilityController.php
│   │   │   └── EligibilityRepository.php
│   │   └── Quotes/
│   │       ├── QuotesController.php
│   │       └── QuotesRepository.php
│   └── Lib/
│       └── Validators.php
├── public/
│   ├── index.php
│   └── assets/
├── api/  # FastAPI bridge
│   ├── main.py
│   ├── services/
│   └── models/
├── config/
│   └── database.php
└── README.md
```

#### Sera (1h): Repository Implementation

**app/Modules/Prospects/ProspectsRepository.php**:
```php
<?php
namespace App\Modules\Prospects;

use App\Core\Database;
use PDO;

class ProspectsRepository {
    private $db;
    
    public function __construct() {
        $this->db = Database::getConnection('insurance_crm');
    }
    
    public function create($data) {
        $sql = "INSERT INTO prospects (
            type, first_name, last_name, birth_date, email, phone,
            tax_code, status, risk_category, assigned_broker, created_by, notes
        ) VALUES (
            :type, :first_name, :last_name, :birth_date, :email, :phone,
            :tax_code, :status, :risk_category, :assigned_broker, :created_by, :notes
        )";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute($data);
        
        return $this->db->lastInsertId();
    }
    
    public function findById($id) {
        $sql = "SELECT p.*, u.username as broker_name
                FROM prospects p
                LEFT JOIN users u ON p.assigned_broker = u.id
                WHERE p.id = :id";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute(['id' => $id]);
        
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
    
    public function findByBroker($broker_id, $filters = []) {
        $sql = "SELECT p.*, COUNT(q.id) as quote_count
                FROM prospects p
                LEFT JOIN quotes q ON p.id = q.prospect_id
                WHERE p.assigned_broker = :broker_id";
        
        $params = ['broker_id' => $broker_id];
        
        if (!empty($filters['status'])) {
            $sql .= " AND p.status = :status";
            $params['status'] = $filters['status'];
        }
        
        if (!empty($filters['date_from'])) {
            $sql .= " AND p.created_at >= :date_from";
            $params['date_from'] = $filters['date_from'];
        }
        
        $sql .= " GROUP BY p.id ORDER BY p.created_at DESC";
        
        if (!empty($filters['limit'])) {
            $sql .= " LIMIT :limit";
            $params['limit'] = (int)$filters['limit'];
        }
        
        $stmt = $this->db->prepare($sql);
        foreach ($params as $key => $value) {
            $stmt->bindValue(":$key", $value);
        }
        $stmt->execute();
        
        return $stmt->fetchAll(PDO::FETCH_ASSOC);
    }
    
    public function updateStatus($id, $status, $notes = null) {
        $sql = "UPDATE prospects 
                SET status = :status, notes = :notes, updated_at = NOW()
                WHERE id = :id";
        
        $stmt = $this->db->prepare($sql);
        return $stmt->execute([
            'id' => $id,
            'status' => $status,
            'notes' => $notes
        ]);
    }
    
    public function delete($id) {
        $sql = "DELETE FROM prospects WHERE id = :id";
        $stmt = $this->db->prepare($sql);
        return $stmt->execute(['id' => $id]);
    }
}
```

**app/Modules/Eligibility/EligibilityRepository.php**:
```php
<?php
namespace App\Modules\Eligibility;

use App\Core\Database;
use PDO;

class EligibilityRepository {
    private $db;
    
    public function __construct() {
        $this->db = Database::getConnection('eligibility_data');
    }
    
    public function checkCached($provider, $insurance_type, $age, $risk_category) {
        $sql = "SELECT * FROM eligibility_cache
                WHERE provider = :provider
                AND insurance_type = :type
                AND age_min <= :age
                AND age_max >= :age
                AND (risk_category = :risk OR risk_category IS NULL)
                AND last_updated > DATE_SUB(NOW(), INTERVAL 24 HOUR)";
        
        $stmt = $this->db->prepare($sql);
        $stmt->execute([
            'provider' => $provider,
            'type' => $insurance_type,
            'age' => $age,
            'risk' => $risk_category
        ]);
        
        return $stmt->fetch(PDO::FETCH_ASSOC);
    }
    
    public function storeResult($data) {
        $sql = "INSERT INTO eligibility_cache (
            provider, insurance_type, age_min, age_max,
            risk_category, is_eligible, base_premium, coverage_max
        ) VALUES (
            :provider, :insurance_type, :age_min, :age_max,
            :risk_category, :is_eligible, :base_premium, :coverage_max
        )";
        
        $stmt = $this->db->prepare($sql);
        return $stmt->execute($data);
    }
    
    public function getAllProviders() {
        $sql = "SELECT DISTINCT provider FROM eligibility_cache";
        $stmt = $this->db->query($sql);
        return $stmt->fetchAll(PDO::FETCH_COLUMN);
    }
}
```

---

### 📅 GIORNO 7-8: FastAPI Bridge & LangChain Integration

#### Concept: Hybrid Architecture
- PHP per CRUD tradizionale (eredità Telco app)
- FastAPI per AI features (LangChain integration)
- Chiamate REST tra PHP ↔ FastAPI

#### Giorno 7: FastAPI Bridge Setup

**api/main.py**:
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import mysql.connector
import os
from dotenv import load_dotenv

from services.eligibility_service import EligibilityService
from services.quote_generator import QuoteGenerator

load_dotenv()

app = FastAPI(title="Insurance CRM AI Bridge")

# CORS for PHP frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
eligibility_service = EligibilityService()
quote_generator = QuoteGenerator()

# Pydantic models
class ProspectProfile(BaseModel):
    birth_date: str
    health_conditions: List[str] = []
    occupation: str
    insurance_type: str

class QuoteRequest(BaseModel):
    prospect_id: int
    insurance_type: str
    providers: List[str]

@app.post("/api/ai/eligibility-check")
async def check_eligibility(profile: ProspectProfile):
    """AI-powered eligibility checking"""
    try:
        result = eligibility_service.check_multi_provider(profile.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/generate-quotes")
async def generate_quotes(request: QuoteRequest):
    """AI-powered quote generation"""
    try:
        # Get prospect from database
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM prospects WHERE id = %s",
            (request.prospect_id,)
        )
        prospect = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospect not found")
        
        # Generate quotes with AI
        quotes = quote_generator.generate_multi_provider(
            prospect,
            request.insurance_type,
            request.providers
        )
        
        return {"quotes": quotes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "insurance_user"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "insurance_crm")
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["eligibility", "quotes"]}
```

**services/eligibility_service.py**:
```python
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from datetime import datetime
from typing import Dict, List

# Import tools from Week 1 Eligibility Agent
from tools import (
    calculate_age,
    assess_risk_category,
    check_provider_eligibility,
    estimate_premium
)

class EligibilityService:
    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0
        )
        
        self.tools = [
            calculate_age,
            assess_risk_category,
            check_provider_eligibility,
            estimate_premium
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an insurance eligibility expert..."),
            ("human", "{input}"),
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.executor = AgentExecutor(agent=self.agent, tools=self.tools)
    
    def check_multi_provider(self, profile: Dict) -> Dict:
        """Check eligibility across all providers"""
        providers = ['generali', 'unipolsai', 'allianz', 'axa']
        
        # Calculate age
        birth_date = datetime.strptime(profile['birth_date'], '%Y-%m-%d')
        age = (datetime.now() - birth_date).days // 365
        
        # Assess risk
        risk = assess_risk_category.invoke(profile)
        
        results = []
        for provider in providers:
            eligibility = check_provider_eligibility.invoke({
                'provider': provider,
                'insurance_type': profile['insurance_type'],
                'age': age,
                'risk_category': risk
            })
            
            if eligibility['eligible']:
                premium = estimate_premium.invoke({
                    'insurance_type': profile['insurance_type'],
                    'age': age,
                    'risk_category': risk
                })
                eligibility['estimated_premium'] = premium
            
            results.append(eligibility)
        
        return {
            'age': age,
            'risk_category': risk,
            'providers': results
        }
```

#### Giorno 8: PHP Integration

**app/Modules/Prospects/ProspectsController.php**:
```php
<?php
namespace App\Modules\Prospects;

class ProspectsController {
    private $repository;
    private $ai_bridge_url = 'http://localhost:8001';  // FastAPI
    
    public function __construct() {
        $this->repository = new ProspectsRepository();
    }
    
    public function create() {
        // Validate input
        $data = $this->validateInput($_POST);
        
        // Create prospect
        $prospect_id = $this->repository->create($data);
        
        // Check eligibility with AI
        if (!empty($data['birth_date'])) {
            $eligibility = $this->checkEligibilityAI([
                'birth_date' => $data['birth_date'],
                'health_conditions' => $data['health_conditions'] ?? [],
                'occupation' => $data['occupation'] ?? 'office',
                'insurance_type' => $data['insurance_type'] ?? 'life'
            ]);
            
            // Update risk category
            $this->repository->updateRiskCategory(
                $prospect_id,
                $eligibility['risk_category']
            );
        }
        
        return [
            'success' => true,
            'prospect_id' => $prospect_id,
            'eligibility' => $eligibility ?? null
        ];
    }
    
    private function checkEligibilityAI($profile) {
        $url = $this->ai_bridge_url . '/api/ai/eligibility-check';
        
        $ch = curl_init($url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_POST, true);
        curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($profile));
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Content-Type: application/json'
        ]);
        
        $response = curl_exec($ch);
        $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($http_code !== 200) {
            error_log("AI Bridge error: " . $response);
            return null;
        }
        
        return json_decode($response, true);
    }
}
```

---

### 📅 GIORNO 9: n8n Workflows Documentation

#### Workflow 1: Lead Capture & Eligibility

**Concept**: Automate prospect creation from web form + eligibility check

**n8n Workflow**:
```json
{
  "nodes": [
    {
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "parameters": {
        "path": "insurance-lead",
        "responseMode": "responseNode",
        "options": {}
      }
    },
    {
      "name": "Validate Data",
      "type": "n8n-nodes-base.function",
      "parameters": {
        "functionCode": "// Validate required fields\nconst required = ['email', 'birth_date', 'insurance_type'];\nconst data = items[0].json;\n\nfor (const field of required) {\n  if (!data[field]) {\n    throw new Error(`Missing required field: ${field}`);\n  }\n}\n\nreturn items;"
      }
    },
    {
      "name": "Check Eligibility (AI)",
      "type": "n8n-nodes-base.httpRequest",
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8001/api/ai/eligibility-check",
        "options": {
          "bodyContentType": "json"
        },
        "jsonParameters": true,
        "bodyParametersJson": "={{ JSON.stringify({\n  birth_date: $json.birth_date,\n  health_conditions: $json.health_conditions || [],\n  occupation: $json.occupation || 'office',\n  insurance_type: $json.insurance_type\n}) }}"
      }
    },
    {
      "name": "Create Prospect (Database)",
      "type": "n8n-nodes-base.mysql",
      "parameters": {
        "operation": "insert",
        "table": "prospects",
        "columns": "first_name, last_name, email, birth_date, insurance_type, risk_category, status",
        "options": {}
      }
    },
    {
      "name": "Send Confirmation Email",
      "type": "n8n-nodes-base.emailSend",
      "parameters": {
        "fromEmail": "noreply@insurance-crm.com",
        "toEmail": "={{ $json.email }}",
        "subject": "Your Insurance Eligibility Results",
        "text": "Thank you for your interest. Based on your profile, we've checked eligibility with major providers..."
      }
    },
    {
      "name": "Response",
      "type": "n8n-nodes-base.respondToWebhook",
      "parameters": {
        "options": {}
      }
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Validate Data"}]]
    },
    "Validate Data": {
      "main": [[{"node": "Check Eligibility (AI)"}]]
    },
    "Check Eligibility (AI)": {
      "main": [[{"node": "Create Prospect (Database)"}]]
    },
    "Create Prospect (Database)": {
      "main": [[{"node": "Send Confirmation Email"}]]
    },
    "Send Confirmation Email": {
      "main": [[{"node": "Response"}]]
    }
  }
}
```

**Export & Document**:
```bash
# Export from n8n
# Save as workflows/lead-capture/workflow.json

# Create README
cat > workflows/lead-capture/README.md << 'EOF'
# Lead Capture & Eligibility Workflow

## Purpose
Automate prospect creation from web forms with AI-powered eligibility checking.

## Flow
1. Webhook receives form data
2. Validate required fields
3. AI eligibility check (FastAPI)
4. Create prospect in database
5. Send confirmation email
6. Respond to webhook

## Configuration
- Webhook URL: `/insurance-lead`
- Database: MySQL insurance_crm
- AI Service: http://localhost:8001

## Testing
\`\`\`bash
curl -X POST http://localhost:5678/webhook/insurance-lead \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Mario",
    "last_name": "Rossi",
    "email": "mario@example.com",
    "birth_date": "1985-05-15",
    "insurance_type": "life"
  }'
\`\`\`
EOF
```

#### Workflow 2: Quote Generation Automation

*Similar structure - document in workflows/quote-automation/*

#### Workflow 3: Follow-up Automation

*Similar structure - document in workflows/follow-up/*

---

### 📅 GIORNO 10: Weekend Week 2

**Tasks**:
- [ ] Complete database setup
- [ ] Test all API endpoints
- [ ] Verify PHP ↔ FastAPI communication
- [ ] Document n8n workflows (3 total)
- [ ] Architecture diagram
- [ ] LinkedIn post #4-5

**LinkedIn Post #4**:
```
🏗️ Building Insurance CRM: Week 2 Progress

Completed:
✓ Dual database (CRM + Eligibility)
✓ Repository pattern implementation
✓ FastAPI ↔ PHP bridge for AI features
✓ 3 n8n automation workflows

Architecture highlight:
• PHP for traditional CRUD (proven, stable)
• FastAPI for AI features (LangChain integration)
• n8n for workflow automation
• Hybrid = best of both worlds

Next week: Quote generator with multi-agent orchestration

[Architecture diagram]
[GitHub link]

#AIEngineering #SoftwareArchitecture #Insurance
```

---

### KPI Week 2 - CHECK ✓
- [ ] Database schema completo
- [ ] 5+ API endpoints funzionanti
- [ ] PHP ↔ FastAPI bridge operational
- [ ] 3 n8n workflows documented
- [ ] Architecture docs complete
- [ ] 4-5 post LinkedIn totali
- [ ] 50+ GitHub profile views
- [ ] 40+ LinkedIn connections

---

## 🗓️ SETTIMANA 3-4: Insurance CRM Complete

*[Continue with remaining weeks following same detailed format...]*

### Obiettivi Week 3-4
- Quote generator con LangChain
- Multi-provider comparison
- PDF policy generation
- Commission system
- Dashboard role-based

### Obiettivi Week 5-6
- LangGraph multi-agent
- Advanced RAG knowledge base
- Production optimization
- Deployment live

### Obiettivi Week 7-8
- Portfolio polish
- Blog posts (3)
- Applications (30+)
- Interview prep

---

## 📚 RISORSE COMPLETE

### LangChain Documentation
- Main: https://python.langchain.com
- Agents: https://python.langchain.com/docs/modules/agents/
- RAG: https://python.langchain.com/docs/tutorials/rag/
- LangGraph: https://langchain-ai.github.io/langgraph/

### Anthropic Resources
- Docs: https://docs.anthropic.com
- Cookbook: https://github.com/anthropics/anthropic-cookbook
- Prompt Library: https://docs.anthropic.com/claude/prompt-library

### Communities
- Discord LangChain: https://discord.gg/langchain
- Discord n8n: https://discord.gg/n8n
- Reddit r/LangChain: https://reddit.com/r/LangChain
- Reddit r/LocalLLaMA: https://reddit.com/r/LocalLLaMA

### Job Boards Italia
- LinkedIn Jobs: https://linkedin.com/jobs
- Wellfound: https://wellfound.com
- AIJobs.net: https://aijobs.net
- Stack Overflow: https://stackoverflow.com/jobs

---

## 🔧 TROUBLESHOOTING GUIDE

### Common Issues

**Issue: LangChain import errors**
```bash
# Solution
pip install --upgrade langchain langchain-anthropic langchain-community
```

**Issue: ChromaDB persistence errors**
```bash
# Solution
rm -rf ./chroma_db  # Clear cache
# Recreate vectorstore
```

**Issue: Anthropic API rate limits**
```python
# Solution: Add retry logic
from anthropic import RateLimitError
import time

def call_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if i < max_retries - 1:
                time.sleep(2 ** i)  # Exponential backoff
            else:
                raise
```

**Issue: MySQL connection errors**
```bash
# Check MySQL service
sudo systemctl status mysql

# Reset password if needed
sudo mysql_secure_installation
```

**Issue: FastAPI CORS errors**
```python
# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📝 DAILY LOG TEMPLATE

### Date: ____

**Morning (1h)**:
- Learned: ____
- Read: ____
- Notes: ____

**Lunch (30m)**:
- LinkedIn: ____
- Community: ____

**Evening (1h)**:
- Coded: ____
- Committed: ____
- Blockers: ____

**Tomorrow Priority**:
- [ ] ____
- [ ] ____
- [ ] ____

---

## ✅ WEEKLY CHECKLIST TEMPLATE

### Week __

**Projects**:
- [ ] Project __ completed
- [ ] Documentation updated
- [ ] Tests passing
- [ ] Deployed (if required)

**Community**:
- [ ] __ LinkedIn posts
- [ ] __ comments on posts
- [ ] __ new connections
- [ ] __ Discord/Reddit contributions

**KPIs**:
- GitHub views: __
- LinkedIn connections: __
- Interview invites: __
- Applications sent: __

**Blockers**:
- ____
- ____

**Next Week Focus**:
- ____
- ____

---

## 🎯 FINAL CHECKLIST (Week 8)

### Portfolio Ready
- [ ] 7-8 progetti pubblici
- [ ] Insurance CRM deployato live
- [ ] README professionale ogni progetto
- [ ] Demo GIFs/screenshots
- [ ] Architecture diagrams

### Visibility
- [ ] 12+ post LinkedIn tecnici
- [ ] 3 blog posts published
- [ ] 100+ LinkedIn connections
- [ ] Active in communities

### Job Ready
- [ ] CV updated con progetti
- [ ] 30+ applications sent
- [ ] Cover letters template
- [ ] Portfolio website (optional)
- [ ] GitHub profile optimized

### Interview Prep
- [ ] Can explain Insurance CRM architecture
- [ ] LangChain patterns understood
- [ ] Multi-agent design clear
- [ ] Production challenges documented
- [ ] Behavioral stories ready

---

## 💰 SUCCESS FORMULA

**Input**: 150-200h over 6-8 weeks  
**Process**: Build + Document + Share + Apply  
**Output**: €50k+ AI Engineer position

**Key Multipliers**:
- Production-level project (not toy)
- Domain adaptation (Telco → Insurance)
- LangChain integration (industry standard)
- Public visibility (LinkedIn + GitHub)
- Consistent execution (daily commits)

**€30k → €50k+ = 67% salary increase = Life changing**

---

**Master Document Version 1.0**  
*Last Updated: Start of Week 1*  
*Save this file and re-upload when starting new sessions*

🚀 **Ready to start Monday!**