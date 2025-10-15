"""
Test the Insurance Eligibility Agent

This script demonstrates the agent in action.

BEFORE RUNNING:
1. Add your Anthropic API key to .env file:
   ANTHROPIC_API_KEY=your_actual_key_here

2. Ensure you have credits in your Anthropic account

WHAT THIS TESTS:
- Agent's ability to orchestrate multiple tools
- Natural language understanding
- Multi-provider comparison
- Premium estimation
"""

import os
from dotenv import load_dotenv
from app.agent import create_agent

# Load environment variables
load_dotenv()

# Check if API key is set
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key or api_key == "your_api_key_here":
    print("=" * 70)
    print("⚠️  ANTHROPIC API KEY NOT SET")
    print("=" * 70)
    print("\nBefore running this test:")
    print("1. Get your API key from: https://console.anthropic.com/")
    print("2. Edit .env file and replace 'your_api_key_here' with your actual key")
    print("3. Ensure you have credits in your account")
    print("\nExample .env file:")
    print("ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx")
    print("=" * 70)
    exit(1)

print("=" * 70)
print("INSURANCE ELIGIBILITY AGENT - TEST")
print("=" * 70)

# Create agent (verbose=True shows reasoning process)
print("\n📝 Creating agent...")
agent = create_agent(verbose=True)

print(f"✓ Agent created successfully!")
print(f"✓ Available tools: {', '.join(agent.get_available_tools())}")

# === TEST 1: Simple Query ===
print("\n" + "=" * 70)
print("TEST 1: List Available Providers")
print("=" * 70)

question1 = "What insurance providers are available?"
print(f"\n👤 User: {question1}\n")

try:
    response1 = agent.query(question1)
    print(f"\n🤖 Agent: {response1}\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")

# === TEST 2: Eligibility Check ===
print("\n" + "=" * 70)
print("TEST 2: Check Eligibility for Specific Customer")
print("=" * 70)

question2 = """
I need to check if Mario Rossi can get life insurance.
He is 35 years old, works as a software engineer, and has no health conditions.
Which providers would accept him and what would be the approximate cost?
"""
print(f"\n👤 User: {question2}\n")

try:
    response2 = agent.query(question2)
    print(f"\n🤖 Agent: {response2}\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")

# === TEST 3: Edge Case (Young Driver) ===
print("\n" + "=" * 70)
print("TEST 3: Edge Case - Young Driver")
print("=" * 70)

question3 = """
Can a 20-year-old get auto insurance?
Check with all providers and explain which ones accept young drivers.
"""
print(f"\n👤 User: {question3}\n")

try:
    response3 = agent.query(question3)
    print(f"\n🤖 Agent: {response3}\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")

# === TEST 4: Comparison ===
print("\n" + "=" * 70)
print("TEST 4: Compare Multiple Providers")
print("=" * 70)

question4 = """
I'm 45 years old, work in an office, and want health insurance.
Compare all providers - which offers the best value?
"""
print(f"\n👤 User: {question4}\n")

try:
    response4 = agent.query(question4)
    print(f"\n🤖 Agent: {response4}\n")
except Exception as e:
    print(f"\n❌ Error: {e}\n")

print("=" * 70)
print("✅ ALL TESTS COMPLETED")
print("=" * 70)
print("\n💡 WHAT YOU JUST SAW:")
print("   - Agent autonomously decided which tools to call")
print("   - Agent compared multiple providers automatically")
print("   - Agent calculated premiums and explained differences")
print("   - Agent handled edge cases (young drivers, etc.)")
print("\nThis is the power of LangChain agents! 🚀")
print("=" * 70)
