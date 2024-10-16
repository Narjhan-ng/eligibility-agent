"""
FastAPI REST API for Insurance Eligibility Agent

This module provides HTTP endpoints to interact with the LangChain agent.
It wraps the agent functionality in a REST API that can be consumed by:
- Web frontends
- Mobile apps
- Other backend services
- Integration tests

=== ARCHITECTURE ===

FastAPI (HTTP Layer)
    ↓
Agent (Business Logic)
    ↓
Tools (Domain Logic)
    ↓
Provider Data (JSON)

This separation allows:
- API versioning
- Authentication/authorization
- Rate limiting
- Monitoring
- Independent scaling
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv

# Import our agent
from app.agent import create_agent

# Load environment variables
load_dotenv()

# === FASTAPI APP INITIALIZATION ===
# Create FastAPI application instance
# title: Shown in OpenAPI docs
# description: API documentation
# version: For API versioning
app = FastAPI(
    title="Insurance Eligibility Agent API",
    description="AI-powered insurance eligibility checking across multiple Italian providers",
    version="1.0.0"
)

# === CORS MIDDLEWARE ===
# Allow cross-origin requests from frontend
# In production, restrict allow_origins to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # PRODUCTION: Change to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === MOUNT STATIC FILES ===
# Day 6: Mount static directory for chat.html
import os
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# === INITIALIZE AGENT ===
# Create agent instance on startup
# This is done once to avoid re-initialization on every request
# In production, consider using dependency injection for better testability
try:
    agent = create_agent(verbose=False)  # verbose=False for production
    print("✓ Agent initialized successfully")
except Exception as e:
    print(f"✗ Error initializing agent: {e}")
    agent = None

# === PYDANTIC MODELS ===
# These models define request/response schemas
# FastAPI uses these for:
# - Request validation
# - Response serialization
# - OpenAPI documentation generation

class CustomerProfile(BaseModel):
    """
    Customer profile for eligibility checking.

    This model validates incoming request data and ensures
    all required fields are present with correct types.
    """
    birth_date: str = Field(
        ...,
        description="Birth date in YYYY-MM-DD format",
        example="1985-05-15"
    )
    health_conditions: List[str] = Field(
        default=[],
        description="List of health conditions",
        example=["diabetes", "hypertension"]
    )
    occupation: str = Field(
        ...,
        description="Customer's occupation",
        example="software engineer"
    )
    insurance_type: str = Field(
        ...,
        description="Type of insurance: life, auto, home, or health",
        example="life"
    )

class InteractiveQuery(BaseModel):
    """
    Model for interactive questions to the agent.

    Allows natural language queries without structured data.
    """
    question: str = Field(
        ...,
        description="Natural language question about insurance eligibility",
        example="Can a 35-year-old software engineer get life insurance?"
    )
    chat_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Previous conversation history for context"
    )

# === DAY 6: SESSION-BASED CONVERSATION MODELS ===

class SessionQuery(BaseModel):
    """
    Model for session-based queries with conversation memory.

    This is the NEW way to interact with the agent (Day 6).
    """
    question: str = Field(
        ...,
        description="User's question",
        example="Can I get life insurance?"
    )
    session_key: Optional[str] = Field(
        default=None,
        description="Session key for continuing a conversation (optional, will create new if not provided)",
        example="550e8400-e29b-41d4-a716-446655440000"
    )
    user_identifier: Optional[str] = Field(
        default=None,
        description="Optional user identifier (email, user_id, etc.)",
        example="user@example.com"
    )
    customer_profile: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional customer profile data to store with session"
    )

class SessionQueryResponse(BaseModel):
    """Response model for session-based queries"""
    answer: str = Field(description="Agent's response")
    session_key: str = Field(description="Session key (store this in browser)")
    session_id: str = Field(description="Internal session ID")
    message_count: int = Field(description="Total messages in this session")
    is_new_session: bool = Field(description="Whether this is a new session")

class ConversationHistoryResponse(BaseModel):
    """Response model for conversation history"""
    session_id: str
    messages: List[Dict[str, Any]]
    session_info: Optional[Dict[str, Any]]

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str
    agent_ready: bool
    message: str

# === API ENDPOINTS ===

@app.get("/chat", response_class=HTMLResponse)
async def chat_interface():
    """
    NEW Chat interface with conversation memory (Day 6).

    Features:
    - Multi-turn dialogues with context memory
    - Session persistence across page reloads
    - Chat history loading
    - Modern chat UI

    This demonstrates the new /api/v2/query endpoint with session management.
    """
    with open(os.path.join(static_path, "chat.html"), 'r', encoding='utf-8') as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def home():
    """
    Home page with embedded HTML interface.

    This serves a web UI for testing the agent with two modes:
    1. Structured form - For predefined customer profiles
    2. Natural language - For free-form questions

    In production, this would typically be a separate frontend app (React, Vue, etc.)
    but for demo/testing purposes, we embed it directly.

    The frontend uses vanilla JavaScript to:
    - Call FastAPI endpoints via fetch()
    - Display results dynamically
    - Handle errors gracefully

    Returns:
        HTML page with interactive forms for eligibility checking
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Insurance Eligibility Checker</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            /* === GLOBAL STYLES === */
            /* Modern font stack for cross-platform consistency */
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }

            /* === CONTAINER === */
            /* Main content container with card design */
            .container {
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }

            /* === TYPOGRAPHY === */
            h1 {
                color: #333;
                border-bottom: 4px solid #667eea;
                padding-bottom: 15px;
                margin-bottom: 30px;
                font-size: 32px;
            }

            h2 {
                color: #667eea;
                margin-top: 30px;
                font-size: 24px;
            }

            /* === INFO BOXES === */
            /* Status message boxes for user feedback */
            .info {
                background: #e7f3ff;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
                border-left: 4px solid #007bff;
            }

            .success {
                background: #d4edda;
                border-left: 4px solid #28a745;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }

            .error {
                background: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 15px;
                border-radius: 8px;
                margin: 20px 0;
            }

            /* === TABS === */
            /* Tab navigation for switching between structured/NL modes */
            .tabs {
                display: flex;
                border-bottom: 2px solid #ddd;
                margin-bottom: 30px;
            }

            .tab {
                padding: 12px 24px;
                cursor: pointer;
                border: none;
                background: none;
                font-size: 16px;
                color: #666;
                border-bottom: 3px solid transparent;
                transition: all 0.3s;
            }

            .tab:hover {
                color: #667eea;
            }

            .tab.active {
                color: #667eea;
                border-bottom: 3px solid #667eea;
                font-weight: 600;
            }

            /* === FORMS === */
            /* Form layout and styling */
            .tab-content {
                display: none;
            }

            .tab-content.active {
                display: block;
                animation: fadeIn 0.3s;
            }

            /* Fade-in animation for tab switching */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .form-group {
                margin-bottom: 20px;
            }

            label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 500;
            }

            /* === INPUT FIELDS === */
            input, select, textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.3s;
                box-sizing: border-box;
            }

            input:focus, select:focus, textarea:focus {
                outline: none;
                border-color: #667eea;
            }

            textarea {
                resize: vertical;
                min-height: 120px;
                font-family: inherit;
            }

            /* === BUTTONS === */
            /* Primary action buttons with loading state */
            button {
                background: #667eea;
                color: white;
                padding: 14px 28px;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                cursor: pointer;
                transition: all 0.3s;
                font-weight: 600;
            }

            button:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }

            button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }

            /* === RESULTS === */
            /* Results display area */
            .result {
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 8px;
                border-left: 4px solid #667eea;
                white-space: pre-wrap;
                line-height: 1.6;
            }

            /* === LOADING SPINNER === */
            /* Visual feedback during API calls */
            .spinner {
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 3px solid rgba(255,255,255,.3);
                border-radius: 50%;
                border-top-color: white;
                animation: spin 1s ease-in-out infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* === LINKS === */
            a {
                color: #667eea;
                text-decoration: none;
                transition: color 0.3s;
            }

            a:hover {
                color: #5568d3;
                text-decoration: underline;
            }

            /* === RESPONSIVE DESIGN === */
            /* Mobile-friendly adjustments */
            @media (max-width: 768px) {
                .container {
                    padding: 20px;
                }

                h1 {
                    font-size: 24px;
                }

                .tabs {
                    flex-direction: column;
                }

                .tab {
                    border-left: 3px solid transparent;
                    border-bottom: none;
                    text-align: left;
                }

                .tab.active {
                    border-left: 3px solid #667eea;
                    border-bottom: none;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <!-- === HEADER === -->
            <h1>🏥 Insurance Eligibility Agent</h1>

            <div class="info">
                <strong>✓ AI Agent Ready!</strong> Powered by LangChain and Claude 3.5 Sonnet.
                Ask questions or fill the form to check eligibility across 4 Italian providers.
                <br><br>
                <strong>🆕 NEW!</strong> Try the <a href="/chat" style="color: #667eea; font-weight: bold;">Chat Interface</a> with conversation memory (Day 6 feature)!
            </div>

            <!-- === TAB NAVIGATION === -->
            <!-- Allows switching between structured form and natural language interface -->
            <div class="tabs">
                <button class="tab active" onclick="switchTab('structured')">
                    📋 Structured Form
                </button>
                <button class="tab" onclick="switchTab('natural')">
                    💬 Natural Language
                </button>
            </div>

            <!-- === TAB 1: STRUCTURED FORM === -->
            <!-- Predefined form fields for structured API endpoint -->
            <div id="structured-tab" class="tab-content active">
                <h2>Check Eligibility</h2>
                <p style="color: #666; margin-bottom: 20px;">
                    Fill in the customer details to check eligibility with all providers.
                </p>

                <form id="eligibility-form" onsubmit="checkEligibility(event)">
                    <!-- Birth Date Field -->
                    <div class="form-group">
                        <label for="birth_date">Birth Date:</label>
                        <input
                            type="date"
                            id="birth_date"
                            name="birth_date"
                            required
                            max="2006-01-01"
                            value="1985-05-15"
                        >
                        <small style="color: #666;">Format: YYYY-MM-DD</small>
                    </div>

                    <!-- Occupation Field -->
                    <div class="form-group">
                        <label for="occupation">Occupation:</label>
                        <input
                            type="text"
                            id="occupation"
                            name="occupation"
                            required
                            placeholder="e.g., software engineer, teacher, doctor"
                            value="software engineer"
                        >
                    </div>

                    <!-- Insurance Type Field -->
                    <div class="form-group">
                        <label for="insurance_type">Insurance Type:</label>
                        <select id="insurance_type" name="insurance_type" required>
                            <option value="life">Life Insurance</option>
                            <option value="auto">Auto Insurance</option>
                            <option value="home">Home Insurance</option>
                            <option value="health">Health Insurance</option>
                        </select>
                    </div>

                    <!-- Health Conditions Field -->
                    <div class="form-group">
                        <label for="health_conditions">Health Conditions (optional):</label>
                        <input
                            type="text"
                            id="health_conditions"
                            name="health_conditions"
                            placeholder="Separate multiple conditions with commas (e.g., diabetes, hypertension)"
                        >
                        <small style="color: #666;">Leave empty if none</small>
                    </div>

                    <!-- Submit Button -->
                    <button type="submit" id="submit-btn">
                        Check Eligibility
                    </button>
                </form>

                <!-- Results Display Area -->
                <div id="result-structured" style="display: none;"></div>
            </div>

            <!-- === TAB 2: NATURAL LANGUAGE === -->
            <!-- Free-form question interface for /api/query endpoint -->
            <div id="natural-tab" class="tab-content">
                <h2>Ask a Question</h2>
                <p style="color: #666; margin-bottom: 20px;">
                    Ask anything about insurance eligibility. The AI agent will use its tools to answer.
                </p>

                <form id="query-form" onsubmit="askQuestion(event)">
                    <!-- Question Textarea -->
                    <div class="form-group">
                        <label for="question">Your Question:</label>
                        <textarea
                            id="question"
                            name="question"
                            required
                            placeholder="Example: Can a 35-year-old software engineer get life insurance? Compare all providers and estimate costs."
                        >Can a 35-year-old software engineer get life insurance? Compare all providers.</textarea>
                    </div>

                    <!-- Submit Button -->
                    <button type="submit" id="query-btn">
                        Ask Agent
                    </button>
                </form>

                <!-- Results Display Area -->
                <div id="result-natural" style="display: none;"></div>
            </div>

            <!-- === FOOTER INFO === -->
            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd;">
                <h2>API Documentation</h2>
                <ul>
                    <li><a href="/docs" target="_blank">📚 Swagger UI - Interactive API Docs</a></li>
                    <li><a href="/redoc" target="_blank">📖 ReDoc - Alternative API Docs</a></li>
                    <li><a href="/health" target="_blank">❤️ Health Check</a></li>
                    <li><a href="/api/providers" target="_blank">🏢 List Providers</a></li>
                </ul>
            </div>

            <p style="margin-top: 30px; color: #666; font-size: 14px; text-align: center;">
                Built with LangChain, Claude 3.5 Sonnet, and FastAPI
            </p>
        </div>

        <script>
            /* === JAVASCRIPT FOR FRONTEND INTERACTIVITY === */

            /**
             * Switch between tabs (Structured vs Natural Language)
             *
             * @param {string} tabName - 'structured' or 'natural'
             *
             * How it works:
             * 1. Remove 'active' class from all tabs and content
             * 2. Add 'active' class to selected tab and its content
             * 3. CSS handles the visibility and animation
             */
            function switchTab(tabName) {
                // Remove active class from all tabs and content
                document.querySelectorAll('.tab').forEach(tab => {
                    tab.classList.remove('active');
                });
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });

                // Add active class to selected tab
                event.target.classList.add('active');
                document.getElementById(tabName + '-tab').classList.add('active');

                // Hide all result divs when switching tabs
                document.getElementById('result-structured').style.display = 'none';
                document.getElementById('result-natural').style.display = 'none';
            }

            /**
             * Handle structured form submission
             *
             * @param {Event} event - Form submit event
             *
             * Flow:
             * 1. Prevent default form submission (avoid page reload)
             * 2. Extract form data
             * 3. Show loading state
             * 4. Call /api/check-eligibility endpoint
             * 5. Display results or error
             */
            async function checkEligibility(event) {
                event.preventDefault(); // Prevent page reload

                // Get form values
                const formData = new FormData(event.target);
                const birthDate = formData.get('birth_date');
                const occupation = formData.get('occupation');
                const insuranceType = formData.get('insurance_type');
                const healthConditionsRaw = formData.get('health_conditions');

                // Parse health conditions (comma-separated string to array)
                const healthConditions = healthConditionsRaw
                    ? healthConditionsRaw.split(',').map(c => c.trim()).filter(c => c)
                    : [];

                // Build request payload matching CustomerProfile Pydantic model
                const payload = {
                    birth_date: birthDate,
                    health_conditions: healthConditions,
                    occupation: occupation,
                    insurance_type: insuranceType
                };

                // Show loading state
                const submitBtn = document.getElementById('submit-btn');
                const resultDiv = document.getElementById('result-structured');

                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner"></span> Checking...';
                resultDiv.style.display = 'none';

                try {
                    // Call FastAPI endpoint
                    const response = await fetch('/api/check-eligibility', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(payload)
                    });

                    const data = await response.json();

                    if (response.ok) {
                        // Success: Display agent's analysis
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h3>✓ Eligibility Analysis</h3>
                            <p><strong>Profile:</strong></p>
                            <ul>
                                <li>Birth Date: ${payload.birth_date}</li>
                                <li>Occupation: ${payload.occupation}</li>
                                <li>Insurance Type: ${payload.insurance_type}</li>
                                <li>Health Conditions: ${payload.health_conditions.length > 0 ? payload.health_conditions.join(', ') : 'None'}</li>
                            </ul>
                            <p><strong>Agent Analysis:</strong></p>
                            <p>${data.analysis}</p>
                        `;
                    } else {
                        // Error from API
                        throw new Error(data.detail || 'Unknown error');
                    }

                } catch (error) {
                    // Network or other errors
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>✗ Error</h3>
                        <p>${error.message}</p>
                        <p><small>Check console for details.</small></p>
                    `;
                    console.error('Error:', error);
                } finally {
                    // Reset button state
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = 'Check Eligibility';
                    resultDiv.style.display = 'block';
                }
            }

            /**
             * Handle natural language query submission
             *
             * @param {Event} event - Form submit event
             *
             * Flow:
             * 1. Prevent default form submission
             * 2. Extract question text
             * 3. Show loading state
             * 4. Call /api/query endpoint
             * 5. Display agent's answer
             */
            async function askQuestion(event) {
                event.preventDefault();

                // Get question text
                const formData = new FormData(event.target);
                const question = formData.get('question');

                // Build request payload matching InteractiveQuery Pydantic model
                const payload = {
                    question: question,
                    chat_history: null  // Future: implement conversation memory
                };

                // Show loading state
                const queryBtn = document.getElementById('query-btn');
                const resultDiv = document.getElementById('result-natural');

                queryBtn.disabled = true;
                queryBtn.innerHTML = '<span class="spinner"></span> Agent thinking...';
                resultDiv.style.display = 'none';

                try {
                    // Call FastAPI endpoint
                    const response = await fetch('/api/query', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(payload)
                    });

                    const data = await response.json();

                    if (response.ok) {
                        // Success: Display agent's answer
                        resultDiv.className = 'result success';
                        resultDiv.innerHTML = `
                            <h3>🤖 Agent Response</h3>
                            <p><strong>Your Question:</strong></p>
                            <p style="font-style: italic; color: #666;">"${question}"</p>
                            <p><strong>Answer:</strong></p>
                            <p>${data.answer}</p>
                        `;
                    } else {
                        throw new Error(data.detail || 'Unknown error');
                    }

                } catch (error) {
                    resultDiv.className = 'result error';
                    resultDiv.innerHTML = `
                        <h3>✗ Error</h3>
                        <p>${error.message}</p>
                        <p><small>Ensure the agent is properly initialized with API key.</small></p>
                    `;
                    console.error('Error:', error);
                } finally {
                    // Reset button state
                    queryBtn.disabled = false;
                    queryBtn.innerHTML = 'Ask Agent';
                    resultDiv.style.display = 'block';
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """
    Health check endpoint.

    Used by:
    - Load balancers to verify service is running
    - Monitoring systems to track uptime
    - CI/CD pipelines to verify deployment

    Returns:
        Health status with agent readiness
    """
    return HealthCheckResponse(
        status="healthy" if agent else "degraded",
        agent_ready=agent is not None,
        message="Agent is ready" if agent else "Agent initialization failed"
    )

@app.post("/api/check-eligibility")
async def check_eligibility(profile: CustomerProfile):
    """
    Check insurance eligibility for a customer profile.

    This endpoint performs a comprehensive eligibility check:
    1. Calculates age from birth date
    2. Assesses risk category based on profile
    3. Checks eligibility with all providers
    4. Estimates premiums for eligible options

    Args:
        profile: Customer profile data

    Returns:
        Agent's analysis with provider eligibility and recommendations

    Raises:
        HTTPException 503: If agent is not initialized
        HTTPException 500: If agent execution fails

    Example:
        ```python
        import requests

        response = requests.post(
            "http://localhost:8000/api/check-eligibility",
            json={
                "birth_date": "1985-05-15",
                "health_conditions": [],
                "occupation": "software engineer",
                "insurance_type": "life"
            }
        )
        print(response.json())
        ```
    """
    # Verify agent is initialized
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Agent is not initialized. Check API key configuration."
        )

    try:
        # Call agent with structured profile
        result = agent.check_eligibility(profile.dict())

        return {
            "success": True,
            "profile": profile.dict(),
            "analysis": result["output"],
            "metadata": {
                "agent_version": "1.0.0",
                "model": "claude-3-5-sonnet-20241022"
            }
        }

    except Exception as e:
        # Log error (in production, use proper logging)
        print(f"Error in check_eligibility: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )

@app.post("/api/query")
async def query_agent(query: InteractiveQuery):
    """
    Ask the agent a question in natural language.

    This endpoint allows free-form questions without structured data.
    The agent will use its tools to answer based on available information.

    Args:
        query: Natural language question and optional chat history

    Returns:
        Agent's response to the question

    Raises:
        HTTPException 503: If agent is not initialized
        HTTPException 500: If agent execution fails

    Example:
        ```python
        import requests

        response = requests.post(
            "http://localhost:8000/api/query",
            json={
                "question": "What providers are available for life insurance?"
            }
        )
        print(response.json())
        ```
    """
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Agent is not initialized. Check API key configuration."
        )

    try:
        # Call agent with natural language query
        result = agent.query(
            question=query.question,
            chat_history=query.chat_history or []
        )

        return {
            "success": True,
            "question": query.question,
            "answer": result,
            "metadata": {
                "agent_version": "1.0.0",
                "model": "claude-3-5-sonnet-20241022"
            }
        }

    except Exception as e:
        print(f"Error in query_agent: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {str(e)}"
        )

@app.get("/api/providers")
async def list_providers():
    """
    Get list of available insurance providers.

    Returns static list of providers currently supported by the system.
    In production, this could be dynamically loaded from the provider database.

    Returns:
        List of provider information
    """
    return {
        "providers": [
            {
                "code": "generali",
                "name": "Generali",
                "country": "IT",
                "products": ["life", "auto", "home", "health"]
            },
            {
                "code": "unipolsai",
                "name": "UnipolSai",
                "country": "IT",
                "products": ["life", "auto", "home", "health"]
            },
            {
                "code": "allianz",
                "name": "Allianz",
                "country": "IT",
                "products": ["life", "auto", "home", "health"]
            },
            {
                "code": "axa",
                "name": "AXA",
                "country": "IT",
                "products": ["life", "auto", "home", "health"]
            }
        ],
        "total": 4
    }

# === DAY 6: NEW ENDPOINTS FOR SESSION-BASED CONVERSATIONS ===

@app.post("/api/v2/query", response_model=SessionQueryResponse)
async def query_with_session(query: SessionQuery):
    """
    Query the agent with session-based conversation memory (Day 6 enhancement).

    This endpoint enables multi-turn dialogues where the agent remembers
    previous context within a session.

    === HOW IT WORKS ===

    1. First request (no session_key): Creates new session
    2. Subsequent requests (with session_key): Continues conversation
    3. Agent has full context from previous messages

    === EXAMPLE FLOW ===

    ```javascript
    // First question
    response1 = await fetch('/api/v2/query', {
        method: 'POST',
        body: JSON.stringify({
            question: "I'm 35 years old, can I get life insurance?"
        })
    });
    // Response includes session_key, store it!

    // Follow-up question (agent remembers age!)
    response2 = await fetch('/api/v2/query', {
        method: 'POST',
        body: JSON.stringify({
            question: "What about health insurance?",
            session_key: session_key_from_response1
        })
    });
    ```

    Args:
        query: SessionQuery object with question and optional session_key

    Returns:
        SessionQueryResponse with answer and session info

    Raises:
        HTTPException: If agent is not initialized or query fails
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized. Check ANTHROPIC_API_KEY configuration."
        )

    try:
        # Step 1: Check if continuing existing session or creating new one
        session_id = None
        session_key = query.session_key
        is_new_session = False

        if session_key:
            # Try to find existing session
            session = agent.get_session_by_key(session_key)

            if session:
                session_id = session['id']
                print(f"✓ Continuing session: {session_id}")
            else:
                # Session expired or not found, create new one
                print(f"✗ Session not found or expired: {session_key}")
                session_key = None  # Will create new below

        if not session_key:
            # Create new session
            session_id, session_key = agent.create_session(
                user_identifier=query.user_identifier,
                customer_profile=query.customer_profile,
                initial_query=query.question
            )
            is_new_session = True
            print(f"✓ Created new session: {session_id}")

        # Step 2: Query agent with session context
        result = agent.query_with_session(
            question=query.question,
            session_id=session_id,
            save_to_db=True
        )

        # Step 3: Return response with session info
        return SessionQueryResponse(
            answer=result["output"],
            session_key=session_key,
            session_id=session_id,
            message_count=result.get("message_count", 2),
            is_new_session=is_new_session
        )

    except Exception as e:
        print(f"Error in query_with_session: {str(e)}")
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        )


@app.get("/api/v2/conversation/{session_key}", response_model=ConversationHistoryResponse)
async def get_conversation_history(session_key: str):
    """
    Get conversation history for a session.

    Useful for:
    - Loading conversation when user returns
    - Displaying chat history in UI
    - Debugging and support

    Args:
        session_key: Session key from client

    Returns:
        ConversationHistoryResponse with messages and session info

    Raises:
        HTTPException: If session not found or error occurs
    """
    if not agent:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized"
        )

    try:
        # Get session
        session = agent.get_session_by_key(session_key)

        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found or expired: {session_key}"
            )

        # Get messages
        messages = agent.get_conversation_messages(session['id'])

        # Format messages for response
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"],
                "created_at": msg["created_at"].isoformat() if msg.get("created_at") else None
            })

        return ConversationHistoryResponse(
            session_id=str(session['id']),
            messages=formatted_messages,
            session_info={
                "session_key": session_key,
                "created_at": session["created_at"].isoformat() if session.get("created_at") else None,
                "status": session.get("status", "unknown"),
                "message_count": len(formatted_messages)
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting conversation history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get conversation history: {str(e)}"
        )

# === STARTUP EVENT ===
@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.

    Good place for:
    - Database connections
    - Cache warming
    - Background tasks initialization
    """
    print("=" * 60)
    print("Insurance Eligibility Agent API")
    print("=" * 60)
    print(f"Agent Status: {'Ready ✓' if agent else 'Not Ready ✗'}")
    print(f"API Documentation: http://localhost:8000/docs")
    print("=" * 60)

# === SHUTDOWN EVENT ===
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.

    Good place for:
    - Closing database connections
    - Cleanup tasks
    - Saving state
    """
    print("Shutting down Insurance Eligibility Agent API...")

# === RUN APPLICATION ===
# This is used when running with: python app/main.py
# For production, use: uvicorn app.main:app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (dev only)
    )
