"""
Insurance Eligibility Agent - LangChain Agent with Tool Orchestration

This module creates an AI agent that can:
- Answer questions about insurance eligibility
- Check multiple providers autonomously
- Calculate premiums and risk categories
- Update provider rules dynamically

=== WHAT IS AN AGENT? ===

An agent is different from a simple LLM call:

SIMPLE LLM:
  User: "Can Mario get insurance?"
  LLM: "I don't know, I need more information"

AGENT WITH TOOLS:
  User: "Can Mario, 35 years old, get life insurance?"
  Agent THINKS: "I need to check eligibility. Let me use my tools."
  Agent CALLS: check_provider_eligibility('generali', 'life', 35, 'low')
  Agent CALLS: check_provider_eligibility('axa', 'life', 35, 'low')
  Agent RESPONDS: "Yes! Both Generali and AXA accept Mario..."

The agent DECIDES which tools to call and in what order!

=== AGENT WORKFLOW ===

1. User asks a question (natural language)
2. Agent analyzes what information is needed
3. Agent decides which tools to call
4. Agent calls tools (can call multiple tools)
5. Agent synthesizes results
6. Agent responds to user (natural language)

This is the CORE of GenAI Engineering!
"""

import os
from typing import Dict, Any, List, Optional, Tuple
from dotenv import load_dotenv

# === LANGCHAIN IMPORTS ===
# These are the core components for building an agent

# ChatAnthropic: The LLM that powers the agent (Claude)
from langchain_anthropic import ChatAnthropic

# Agent components
from langchain.agents import AgentExecutor, create_tool_calling_agent

# Prompt templates for agent instructions
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import all our custom tools
from app.tools import (
    calculate_age,
    assess_risk_category,
    estimate_premium,
    check_provider_eligibility,
    list_available_providers,
    get_provider_details,
    update_provider_rules
)

# === DAY 6 ADDITION: Session Manager for Conversation Memory ===
# Import the SessionManager to enable multi-turn conversations
from app.session_manager import SessionManager

# Load environment variables from .env file
load_dotenv()


class EligibilityAgent:
    """
    Insurance Eligibility Agent - Orchestrates multiple tools to help customers.

    === ARCHITECTURE ===

    This class wraps a LangChain agent with:
    - LLM (Claude 3.5 Sonnet) for reasoning
    - 7 tools for specific tasks
    - System prompt with insurance domain knowledge
    - Conversation memory (optional)

    === WHY A CLASS? ===

    Using a class allows us to:
    - Initialize once, use many times (efficiency)
    - Maintain conversation state (Day 6: NOW IMPLEMENTED!)
    - Easy to test and mock
    - Clean API for external use

    === DAY 6 ENHANCEMENT: CONVERSATION MEMORY ===

    Now supports multi-turn dialogues with:
    - Session-based conversation tracking
    - Persistent message history
    - Context awareness across requests
    - Automatic session management
    """

    def __init__(self, verbose: bool = True, session_manager: Optional[SessionManager] = None):
        """
        Initialize the agent with LLM and tools.

        Args:
            verbose: If True, prints agent's reasoning process
                    (useful for debugging and learning)
            session_manager: Optional SessionManager instance for conversation memory
                           If None, creates a new one (Day 6 addition)

        === INITIALIZATION STEPS ===
        1. Create LLM instance (Claude)
        2. Collect all tools
        3. Create system prompt
        4. Build agent
        5. Wrap in executor
        6. (Day 6) Initialize session manager for memory
        """

        # === DAY 6: Initialize Session Manager ===
        # Session manager handles conversation memory and persistence
        self.session_manager = session_manager or SessionManager()
        # === STEP 1: Initialize the LLM ===
        # Claude 3.5 Sonnet is the "brain" of the agent
        # It decides which tools to call and interprets results
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",  # Latest Claude model
            temperature=0,  # 0 = deterministic, 1 = creative
            # Lower temperature for insurance = more consistent, reliable answers
        )

        # === STEP 2: Collect All Tools ===
        # These are the "skills" the agent can use
        # The agent will read each tool's docstring to understand when to use it
        self.tools = [
            # Core eligibility tools
            calculate_age,              # Convert birth date to age
            assess_risk_category,       # Analyze customer risk profile
            estimate_premium,           # Calculate insurance costs
            check_provider_eligibility, # Check if provider accepts customer

            # Dynamic provider management tools
            list_available_providers,   # Get all available providers
            get_provider_details,       # Get detailed provider info
            update_provider_rules,      # Update provider rules (admin)
        ]

        # === STEP 3: Create System Prompt ===
        # This is the "personality" and "instructions" for the agent
        # CRITICAL: The prompt defines how the agent behaves!
        self.prompt = ChatPromptTemplate.from_messages([
            # === SYSTEM MESSAGE ===
            # This tells the agent WHO it is and WHAT it should do
            ("system", """You are an expert insurance eligibility advisor.

Your role is to help customers understand their insurance options by:
1. Analyzing their profile (age, health, occupation)
2. Checking eligibility with all major Italian providers
3. Estimating costs and explaining differences
4. Providing clear, actionable recommendations

=== AVAILABLE PROVIDERS ===
You can check eligibility with these Italian insurance companies:
- Generali
- UnipolSai
- Allianz
- AXA

Each provider has different rules for age ranges and risk acceptance.

=== YOUR APPROACH ===

When a customer asks about insurance:

1. GATHER INFORMATION
   - If you have a birth date, use calculate_age to get exact age
   - Use assess_risk_category to evaluate their risk level
   - Consider their occupation and health conditions

2. CHECK ELIGIBILITY
   - Use check_provider_eligibility for EACH provider
   - Don't assume - actually check the rules!
   - Compare all providers to find best options

3. ESTIMATE COSTS
   - Use estimate_premium to give price estimates
   - Explain what affects the premium (age, risk)

4. PROVIDE RECOMMENDATIONS
   - List all eligible providers
   - Highlight best value options
   - Explain any rejections clearly

=== COMMUNICATION STYLE ===

- Be professional but friendly
- Explain insurance jargon in simple terms
- Always cite specific numbers (age ranges, premiums)
- If multiple providers are eligible, compare them
- If NO providers are eligible, explain why and suggest alternatives

=== IMPORTANT ===

- NEVER make up eligibility rules - always use the tools!
- If you're not sure, check the provider details
- Premium estimates are approximate - explain this
- Be transparent about why someone might be rejected

You have access to tools that load provider rules from a database,
so your information is always current and accurate.
"""),

            # === CONVERSATION HISTORY ===
            # MessagesPlaceholder allows the agent to remember previous messages
            # (optional, not used in basic version but good for multi-turn conversations)
            MessagesPlaceholder(variable_name="chat_history", optional=True),

            # === USER INPUT ===
            # The actual user question goes here
            ("human", "{input}"),

            # === AGENT SCRATCHPAD ===
            # This is where the agent's "thinking" process goes
            # LangChain uses this to track which tools were called and their results
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        # === STEP 4: Create the Agent ===
        # This combines the LLM, tools, and prompt into a reasoning agent
        #
        # create_tool_calling_agent is a LangChain helper that:
        # - Gives the LLM access to tools
        # - Handles tool call formatting
        # - Manages the reasoning loop
        self.agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        # === STEP 5: Wrap in Executor ===
        # AgentExecutor handles the actual execution loop:
        # 1. Send prompt to LLM
        # 2. If LLM wants to call a tool, call it
        # 3. Send tool result back to LLM
        # 4. Repeat until LLM has final answer
        # 5. Return final answer to user
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose,  # Print reasoning steps if True
            handle_parsing_errors=True,  # Gracefully handle LLM errors
            max_iterations=15,  # Prevent infinite loops
            # If agent tries >15 tool calls, stop and return what it has
        )

    def check_eligibility(self, customer_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check insurance eligibility for a customer profile.

        This is a structured interface for programmatic use.

        Args:
            customer_profile: Dict with keys:
                - birth_date: str (YYYY-MM-DD) or age: int
                - health_conditions: list of str (optional)
                - occupation: str (optional)
                - insurance_type: str (life/auto/home/health)

        Returns:
            Dict with agent's response and metadata

        Example:
            agent = EligibilityAgent()
            result = agent.check_eligibility({
                'birth_date': '1985-05-15',
                'health_conditions': [],
                'occupation': 'software engineer',
                'insurance_type': 'life'
            })
            print(result['output'])

        === HOW IT WORKS ===
        1. Format profile into natural language
        2. Send to agent
        3. Agent decides which tools to call
        4. Agent synthesizes results
        5. Return structured response
        """
        # Format the profile into a natural language prompt
        # This helps the agent understand what the user wants
        input_text = f"""
        Please check insurance eligibility for this customer:

        Customer Profile:
        - Birth Date: {customer_profile.get('birth_date', 'Not provided')}
        - Age: {customer_profile.get('age', 'Calculate from birth date')}
        - Health Conditions: {customer_profile.get('health_conditions', [])}
        - Occupation: {customer_profile.get('occupation', 'Not specified')}
        - Insurance Type: {customer_profile.get('insurance_type', 'Not specified')}

        Please:
        1. Check eligibility with ALL major providers (Generali, UnipolSai, Allianz, AXA)
        2. Calculate estimated premiums for eligible options
        3. Provide a clear recommendation
        """

        # Invoke the agent executor
        # This starts the reasoning loop
        result = self.agent_executor.invoke({
            "input": input_text
        })

        return result

    def query(self, question: str, chat_history: Optional[List] = None) -> str:
        """
        Ask the agent a question in natural language.

        This is the simple interface for interactive use.

        Args:
            question: Natural language question
            chat_history: Optional list of previous messages (for context)

        Returns:
            Agent's response as string

        Example:
            agent = EligibilityAgent()
            response = agent.query("Can a 35 year old get life insurance?")
            print(response)

        === USE CASES ===
        - Interactive chat interface
        - Customer support bot
        - API endpoint for web app
        - Testing and experimentation
        """
        result = self.agent_executor.invoke({
            "input": question,
            "chat_history": chat_history or []
        })

        # Return just the output text
        # (agent_executor returns a dict with 'input' and 'output')
        return result["output"]

    def get_available_tools(self) -> List[str]:
        """
        Get list of available tool names.

        Useful for debugging and documentation.

        Returns:
            List of tool names
        """
        return [tool.name for tool in self.tools]

    # === DAY 6: NEW METHODS FOR SESSION-BASED CONVERSATIONS ===

    def query_with_session(
        self,
        question: str,
        session_id: str,
        save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Ask a question with session-based conversation memory.

        This is the NEW way to interact with the agent (Day 6).

        Args:
            question: User's question
            session_id: Session UUID for conversation tracking
            save_to_db: Whether to persist messages (default True)

        Returns:
            Dict with:
                - output: Agent's response
                - session_id: Session UUID
                - message_count: Total messages in session

        === HOW IT WORKS ===

        1. Load conversation history from database
        2. Pass history to agent (gives context)
        3. Agent responds with full context awareness
        4. Save user message and agent response to database

        === EXAMPLE ===

        ```python
        # First question
        result = agent.query_with_session(
            question="I'm 35 years old, can I get life insurance?",
            session_id="abc-123"
        )
        # Agent checks eligibility

        # Follow-up question (agent remembers context!)
        result = agent.query_with_session(
            question="What about health insurance?",
            session_id="abc-123"  # Same session
        )
        # Agent remembers user is 35, checks health insurance
        ```

        === WHY THIS IS POWERFUL ===

        Without sessions:
        User: "What about health insurance?"
        Agent: "I need more information. How old are you?"

        With sessions:
        User: "What about health insurance?"
        Agent: "Since you're 35 years old (from our previous conversation),
                let me check health insurance eligibility..."
        """

        # Step 1: Load conversation history from database
        chat_history = self.session_manager.get_conversation_history(
            session_id=session_id,
            include_tool_messages=False  # Don't include tool calls in history (too verbose)
        )

        # Step 2: Save user message to database (before agent responds)
        if save_to_db:
            self.session_manager.add_message(
                session_id=session_id,
                role="user",
                content=question
            )

        # Step 3: Invoke agent with conversation history
        result = self.agent_executor.invoke({
            "input": question,
            "chat_history": chat_history  # Agent now has full context!
        })

        # Step 4: Save agent response to database
        if save_to_db:
            self.session_manager.add_message(
                session_id=session_id,
                role="assistant",
                content=result["output"]
            )

            # Extend session expiry (user is active)
            self.session_manager.extend_session_expiry(session_id, hours=24)

        # Step 5: Return structured response
        return {
            "output": result["output"],
            "session_id": session_id,
            "message_count": len(chat_history) + 2  # +2 for current exchange
        }

    def create_session(
        self,
        user_identifier: Optional[str] = None,
        customer_profile: Optional[Dict[str, Any]] = None,
        initial_query: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Create a new conversation session.

        Args:
            user_identifier: Optional user ID/email
            customer_profile: Optional customer data
            initial_query: Optional first question
            metadata: Optional metadata (user_agent, ip, etc.)

        Returns:
            Tuple of (session_id, session_key)

        === USAGE ===

        ```python
        # Create session when user starts conversation
        session_id, session_key = agent.create_session(
            user_identifier="user@example.com",
            customer_profile={"age": 35, "occupation": "engineer"}
        )

        # Return session_key to client (store in browser)
        # Client sends session_key with each request
        ```
        """
        return self.session_manager.create_session(
            user_identifier=user_identifier,
            customer_profile=customer_profile,
            initial_query=initial_query,
            metadata=metadata
        )

    def get_session_by_key(self, session_key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve session by client-facing session key.

        Args:
            session_key: Session key from client

        Returns:
            Session dict or None if not found/expired

        === TYPICAL API FLOW ===

        ```python
        # Client sends session_key
        session = agent.get_session_by_key(session_key)

        if session:
            # Continue existing conversation
            session_id = session['id']
        else:
            # Create new session
            session_id, session_key = agent.create_session()
        ```
        """
        return self.session_manager.get_session_by_key(session_key)

    def get_conversation_messages(
        self,
        session_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all messages for a session (for display in UI).

        Args:
            session_id: Session UUID

        Returns:
            List of message dicts with role, content, timestamp

        === USAGE ===

        ```python
        # Load conversation history for UI
        messages = agent.get_conversation_messages(session_id)

        # Display in chat interface
        for msg in messages:
            print(f"{msg['role']}: {msg['content']}")
        ```
        """
        return self.session_manager.get_messages(session_id)


# === CONVENIENCE FUNCTION ===
# This allows simple usage without creating a class instance
def create_agent(verbose: bool = True) -> EligibilityAgent:
    """
    Create and return an EligibilityAgent instance.

    Args:
        verbose: Whether to print agent's reasoning

    Returns:
        Configured EligibilityAgent

    Example:
        agent = create_agent()
        response = agent.query("What providers are available?")
    """
    return EligibilityAgent(verbose=verbose)
