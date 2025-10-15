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
from typing import Dict, Any, List, Optional
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
    - Maintain conversation state (future enhancement)
    - Easy to test and mock
    - Clean API for external use
    """

    def __init__(self, verbose: bool = True):
        """
        Initialize the agent with LLM and tools.

        Args:
            verbose: If True, prints agent's reasoning process
                    (useful for debugging and learning)

        === INITIALIZATION STEPS ===
        1. Create LLM instance (Claude)
        2. Collect all tools
        3. Create system prompt
        4. Build agent
        5. Wrap in executor
        """
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
