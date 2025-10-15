"""
Insurance eligibility tools for LangChain agent.

These tools provide the core functionality for assessing insurance eligibility:
- Age calculation from birth date
- Risk category assessment based on customer profile
- Premium estimation
- Provider-specific eligibility checking

=== LANGCHAIN TOOLS EXPLAINED ===

In LangChain, a "tool" is a FUNCTION that an agent can call autonomously.
Instead of writing procedural code (step 1, step 2, step 3),
we give the agent a "toolbox" and it decides which tools to use.

Example:
- User: "Mario is 35 years old, born 1990-01-01. Can he get life insurance?"
- Agent DECIDES:
  1. Use calculate_age to verify age
  2. Use assess_risk_category to calculate risk
  3. Use check_provider_eligibility for each provider
  4. Use estimate_premium to provide cost estimate

The agent orchestrates tools AUTONOMOUSLY based on context.
"""

# === LANGCHAIN IMPORTS ===
# @tool: Decorator that transforms a regular Python function into a LangChain Tool
# This tells LangChain: "this function can be called by the agent"
from langchain.tools import tool

# Standard Python imports (not LangChain)
from datetime import datetime
from typing import Dict, Any, List

# Import our custom provider loader for dynamic rule management
from app.provider_loader import ProviderRulesLoader


# === DECORATOR @tool EXPLAINED ===
# This decorator does 3 MAGIC things:
#
# 1. REGISTERS the function as a "tool" available to the agent
# 2. EXTRACTS the docstring (""") and uses it to explain to the LLM what the tool does
# 3. EXTRACTS type hints (birth_date: str -> int) to validate input/output
#
# The LLM reads the docstring and decides when to use this tool!
# That's why the docstring must be CLEAR and DESCRIPTIVE.
@tool
def calculate_age(birth_date: str) -> int:
    """
    Calculate age from birth date.

    Args:
        birth_date: Date in format YYYY-MM-DD

    Returns:
        Age in years

    Example:
        calculate_age("1985-05-15") -> 40 (in 2025)

    === WHEN THE AGENT USES THIS TOOL ===
    The agent will use this tool when:
    - User provides a birth date instead of age
    - Need to calculate age to verify eligibility
    - Need exact age to calculate premiums
    """
    try:
        # BUSINESS LOGIC (regular Python - no LangChain here)
        birth = datetime.strptime(birth_date, "%Y-%m-%d")
        today = datetime.today()
        # Calculate age considering if birthday has passed this year
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    except ValueError as e:
        # If date is invalid, raise error that agent can handle
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. Error: {e}")


# === TOOL WITH COMPLEX INPUT ===
# This tool accepts a Dict (complex object) instead of a simple parameter.
# LangChain automatically:
# - Validates that the Dict contains the right keys
# - Converts types (if LLM passes strings instead of int, converts them)
# - Passes the Dict to the function
#
# IMPORTANT: The type hint Dict[str, Any] tells LangChain:
# - Keys are strings
# - Values can be of any type
@tool
def assess_risk_category(profile: Dict[str, Any]) -> str:
    """
    Assess risk category based on customer profile.

    Args:
        profile: Dict with keys:
            - age: int (customer age)
            - health_conditions: list of str (medical conditions)
            - occupation: str (job type)

    Returns:
        Risk category: 'low', 'medium', or 'high'

    Example:
        assess_risk_category({
            "age": 30,
            "health_conditions": [],
            "occupation": "office"
        }) -> "low"

    === WHEN THE AGENT USES THIS TOOL ===
    The agent will use this tool when:
    - Need to assess customer's risk level
    - Before checking eligibility (providers have risk limits)
    - To calculate premiums (risk affects cost)

    === IMPORTANT NOTE ===
    This tool implements BUSINESS RULES.
    In a real system, these rules could:
    - Come from a database
    - Be configurable
    - Use ML/AI for more accurate predictions
    """
    # BUSINESS LOGIC: Extract data from profile
    # .get() with default prevents errors if a key is missing
    age = profile.get('age', 0)
    health_conditions = profile.get('health_conditions', [])
    occupation = profile.get('occupation', 'office')

    # Scoring system to calculate total risk
    risk_score = 0

    # === AGE FACTOR ===
    # Young (<25) and elderly (>65) have higher risk
    if age < 25 or age > 65:
        risk_score += 2
    elif age > 50:
        risk_score += 1

    # === HEALTH FACTOR ===
    # Lists of medical conditions with different risk levels
    high_risk_conditions = ['diabetes', 'heart_disease', 'cancer_history', 'hypertension']
    medium_risk_conditions = ['asthma', 'allergies', 'arthritis']

    for condition in health_conditions:
        condition_lower = condition.lower()
        if any(high_risk in condition_lower for high_risk in high_risk_conditions):
            risk_score += 3
            break  # One serious condition is enough
        elif any(medium_risk in condition_lower for medium_risk in medium_risk_conditions):
            risk_score += 1

    # === OCCUPATION FACTOR ===
    # Dangerous jobs increase risk
    high_risk_jobs = ['construction', 'mining', 'firefighter', 'police', 'pilot']
    medium_risk_jobs = ['driver', 'electrician', 'mechanic']

    occupation_lower = occupation.lower()
    if any(job in occupation_lower for job in high_risk_jobs):
        risk_score += 2
    elif any(job in occupation_lower for job in medium_risk_jobs):
        risk_score += 1

    # === FINAL CLASSIFICATION ===
    # Converts numeric score to text category
    # This is what the agent will receive as response
    if risk_score >= 5:
        return 'high'
    elif risk_score >= 2:
        return 'medium'
    else:
        return 'low'


# === TOOL WITH MULTIPLE PARAMETERS ===
# This tool shows how LangChain handles functions with multiple simple parameters.
# The LLM must provide ALL required parameters when calling this tool.
# LangChain will validate:
# - All parameters are present
# - Types match (str, int, etc.)
# - Returns the expected type
@tool
def estimate_premium(insurance_type: str, age: int, risk_category: str) -> float:
    """
    Estimate monthly insurance premium based on type, age, and risk.

    Args:
        insurance_type: 'life', 'auto', 'home', or 'health'
        age: Customer age in years
        risk_category: 'low', 'medium', or 'high'

    Returns:
        Estimated monthly premium in euros

    Example:
        estimate_premium("life", 35, "low") -> 45.0

    === WHEN THE AGENT USES THIS TOOL ===
    The agent will use this tool when:
    - User asks "how much will it cost?"
    - Need to provide price estimates
    - Comparing different insurance options

    === PRICING LOGIC ===
    Premium = base_price × age_multiplier × risk_multiplier

    This is a simplified formula. Real insurance pricing uses:
    - Actuarial tables
    - Historical data
    - Market conditions
    - Regulatory requirements
    """
    # Base premiums by insurance type (monthly, in euros)
    # These would typically come from a database or pricing engine
    base_premiums = {
        'life': 50.0,
        'auto': 80.0,
        'home': 60.0,
        'health': 100.0
    }

    insurance_type_lower = insurance_type.lower()
    base = base_premiums.get(insurance_type_lower, 50.0)

    # === AGE MULTIPLIER ===
    # Higher for young and elderly customers
    age_multiplier = 1.0
    if age < 25:
        age_multiplier = 1.5  # Young drivers/applicants
    elif age > 50:
        # Gradual increase after 50
        age_multiplier = 1.2 + (age - 50) * 0.02

    # === RISK MULTIPLIER ===
    # Higher risk = higher premium
    risk_multipliers = {
        'low': 1.0,      # No increase
        'medium': 1.3,   # +30%
        'high': 1.8      # +80%
    }
    risk_mult = risk_multipliers.get(risk_category.lower(), 1.0)

    # === FINAL CALCULATION ===
    premium = base * age_multiplier * risk_mult

    # Round to 2 decimal places (cents)
    return round(premium, 2)


# === TOOL WITH DICT RETURN TYPE ===
# This tool returns a complex Dict instead of a simple value.
# LangChain handles this automatically - the agent will receive
# the entire Dict and can use the information to make decisions.
#
# WHY RETURN A DICT?
# - Provides structured data (not just yes/no)
# - Agent can use the 'reason' to explain to the user
# - Multiple pieces of information in one tool call
@tool
def check_provider_eligibility(
    provider: str,
    insurance_type: str,
    age: int,
    risk_category: str
) -> Dict[str, Any]:
    """
    Check eligibility with a specific insurance provider.

    Each provider has different eligibility rules for age ranges and risk acceptance.

    Args:
        provider: 'generali', 'unipolsai', 'allianz', or 'axa'
        insurance_type: 'life', 'auto', 'home', or 'health'
        age: Customer age in years
        risk_category: 'low', 'medium', or 'high'

    Returns:
        Dict with keys:
            - eligible: bool (True if eligible, False otherwise)
            - provider: str (provider name)
            - insurance_type: str (insurance type)
            - reason: str (detailed explanation)

    Example:
        check_provider_eligibility("generali", "life", 35, "low")
        -> {
            "eligible": True,
            "provider": "generali",
            "insurance_type": "life",
            "reason": "Customer meets all eligibility criteria"
        }

    === WHEN THE AGENT USES THIS TOOL ===
    The agent will use this tool when:
    - Need to check if customer qualifies with a specific provider
    - Comparing multiple providers
    - User asks "which companies accept me?"

    === BUSINESS RULES ===
    Each provider has different rules:
    - Age ranges (min/max accepted age)
    - Risk tolerance (max accepted risk level)
    - Product availability (not all offer all insurance types)

    === NOW WITH DYNAMIC LOADING ===
    Rules are loaded from JSON files in data/providers/
    This means:
    - Rules can be updated without changing code
    - New providers can be added by adding JSON files
    - Business users can modify rules directly
    """
    # Normalize inputs to lowercase for comparison
    provider_lower = provider.lower()
    insurance_type_lower = insurance_type.lower()

    # === LOAD PROVIDER RULES DYNAMICALLY ===
    # Instead of hardcoded dict, load from JSON files
    # This is what makes the system production-ready!
    try:
        provider_data = ProviderRulesLoader.get_provider(provider_lower)
    except Exception as e:
        return {
            'eligible': False,
            'provider': provider,
            'insurance_type': insurance_type,
            'reason': f'Error loading provider rules: {str(e)}'
        }

    # === VALIDATION 1: Check if provider exists ===
    if not provider_data:
        # Get list of available providers dynamically
        available = ProviderRulesLoader.list_providers()
        return {
            'eligible': False,
            'provider': provider,
            'insurance_type': insurance_type,
            'reason': f'Unknown provider: {provider}. Available: {", ".join(available)}'
        }

    # === VALIDATION 2: Check if insurance type is available ===
    # Get product rules from the loaded provider data
    provider_rules = provider_data.get('products', {}).get(insurance_type_lower)

    if not provider_rules:
        return {
            'eligible': False,
            'provider': provider,
            'insurance_type': insurance_type,
            'reason': f'Provider {provider} does not offer {insurance_type} insurance'
        }

    # === VALIDATION 3: Check age eligibility ===
    if age < provider_rules['age_min'] or age > provider_rules['age_max']:
        return {
            'eligible': False,
            'provider': provider,
            'insurance_type': insurance_type,
            'reason': f'Age {age} is outside acceptable range ({provider_rules["age_min"]}-{provider_rules["age_max"]} years)'
        }

    # === VALIDATION 4: Check risk category eligibility ===
    # Risk levels in order of severity
    risk_levels = ['low', 'medium', 'high']

    # Find index of maximum accepted risk
    max_risk_idx = risk_levels.index(provider_rules['max_risk'])

    # Find index of customer's risk
    current_risk_idx = risk_levels.index(risk_category.lower())

    # If customer's risk exceeds max accepted, not eligible
    if current_risk_idx > max_risk_idx:
        return {
            'eligible': False,
            'provider': provider,
            'insurance_type': insurance_type,
            'reason': f'Risk category "{risk_category}" exceeds maximum accepted risk ("{provider_rules["max_risk"]}")'
        }

    # === ALL CHECKS PASSED ===
    # Customer is eligible!
    return {
        'eligible': True,
        'provider': provider,
        'insurance_type': insurance_type,
        'reason': 'Customer meets all eligibility criteria'
    }


# === NEW TOOLS: DYNAMIC PROVIDER MANAGEMENT ===
# These tools allow the agent to work with dynamically loaded provider data
# instead of hardcoded rules. This makes the system production-ready.


@tool
def list_available_providers() -> List[str]:
    """
    Get list of all available insurance providers.

    Returns:
        List of provider codes (e.g., ['generali', 'axa', 'allianz'])

    === WHEN THE AGENT USES THIS TOOL ===
    The agent will use this tool when:
    - User asks "which providers are available?"
    - Need to know all options before checking eligibility
    - Comparing all providers for a customer

    === WHY DYNAMIC? ===
    In a real system:
    - New providers can be added by adding JSON files
    - Providers can be temporarily disabled
    - Different regions might have different providers
    """
    try:
        providers = ProviderRulesLoader.list_providers()
        return providers
    except Exception as e:
        # If loading fails, return empty list and log error
        print(f"Error loading providers: {e}")
        return []


@tool
def get_provider_details(provider_code: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific provider.

    Args:
        provider_code: Provider code (e.g., 'generali', 'axa')

    Returns:
        Dict with provider information including all products

    Example:
        get_provider_details("generali") ->
        {
            "provider_name": "Generali",
            "country": "IT",
            "products": {...}
        }

    === WHEN THE AGENT USES THIS TOOL ===
    The agent will use this tool when:
    - User asks about a specific provider
    - Need to see all products offered by a provider
    - Comparing provider offerings
    """
    try:
        provider = ProviderRulesLoader.get_provider(provider_code)
        if not provider:
            return {
                'error': f'Provider {provider_code} not found',
                'available_providers': ProviderRulesLoader.list_providers()
            }
        return provider
    except Exception as e:
        return {'error': str(e)}


@tool
def update_provider_rules(
    provider_code: str,
    product_type: str,
    field: str,
    value: Any
) -> Dict[str, Any]:
    """
    Update a specific field in a provider's product rules.

    Args:
        provider_code: Provider to update (e.g., 'generali')
        product_type: Product to update (e.g., 'life', 'auto', 'home', 'health')
        field: Field to update (e.g., 'age_max', 'base_premium', 'max_risk')
        value: New value for the field

    Returns:
        Dict with success status and message

    Example:
        update_provider_rules("generali", "life", "age_max", 75) ->
        {
            "success": True,
            "message": "Updated generali life insurance: age_max = 75",
            "updated_rules": {...}
        }

    === WHEN THE AGENT USES THIS TOOL ===
    The agent will use this tool when:
    - User requests to update provider rules
    - Provider changes their requirements
    - Testing different rule configurations

    === IMPORTANT: SECURITY ===
    In production, this tool should:
    - Require authentication/authorization
    - Log all changes with user info
    - Have approval workflow
    - Validate value types and ranges

    For learning purposes, it's unrestricted.
    """
    try:
        # Create updates dict with single field
        updates = {field: value}

        # Attempt update
        success = ProviderRulesLoader.update_provider_product(
            provider_code,
            product_type,
            updates
        )

        if success:
            # Get updated rules to return
            updated_rules = ProviderRulesLoader.get_product_rules(
                provider_code,
                product_type
            )

            return {
                'success': True,
                'message': f'Updated {provider_code} {product_type} insurance: {field} = {value}',
                'updated_rules': updated_rules
            }
        else:
            return {
                'success': False,
                'message': f'Failed to update {provider_code} {product_type}',
                'error': 'Update operation failed'
            }

    except Exception as e:
        return {
            'success': False,
            'message': 'Update failed',
            'error': str(e)
        }


# === EXPORT ALL TOOLS ===
# This makes it easy to import all tools at once:
# from app.tools import *
# or
# from app.tools import calculate_age, assess_risk_category, ...
__all__ = [
    'calculate_age',
    'assess_risk_category',
    'estimate_premium',
    'check_provider_eligibility',
    'list_available_providers',
    'get_provider_details',
    'update_provider_rules'
]
