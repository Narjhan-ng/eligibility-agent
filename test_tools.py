"""
Quick test script to verify all tools work correctly.
This is a learning-by-doing approach: test each tool independently before integration.
"""

from app.tools import (
    calculate_age,
    assess_risk_category,
    estimate_premium,
    check_provider_eligibility
)

def test_calculate_age():
    """Test age calculation"""
    print("=" * 50)
    print("TEST 1: Calculate Age")
    print("=" * 50)

    test_cases = [
        "1985-05-15",  # Should be ~40 in 2025
        "2000-01-01",  # Should be ~25 in 2025
        "1960-12-31",  # Should be ~65 in 2025
    ]

    for birth_date in test_cases:
        age = calculate_age.invoke({"birth_date": birth_date})
        print(f"Birth date: {birth_date} -> Age: {age}")

    print()


def test_assess_risk():
    """Test risk assessment"""
    print("=" * 50)
    print("TEST 2: Assess Risk Category")
    print("=" * 50)

    test_profiles = [
        {
            "age": 30,
            "health_conditions": [],
            "occupation": "software engineer"
        },
        {
            "age": 55,
            "health_conditions": ["diabetes"],
            "occupation": "office"
        },
        {
            "age": 22,
            "health_conditions": [],
            "occupation": "construction"
        }
    ]

    for i, profile in enumerate(test_profiles, 1):
        risk = assess_risk_category.invoke({"profile": profile})
        print(f"\nProfile {i}:")
        print(f"  Age: {profile['age']}")
        print(f"  Health: {profile['health_conditions']}")
        print(f"  Job: {profile['occupation']}")
        print(f"  → Risk Category: {risk}")

    print()


def test_estimate_premium():
    """Test premium estimation"""
    print("=" * 50)
    print("TEST 3: Estimate Premium")
    print("=" * 50)

    test_cases = [
        ("life", 35, "low"),
        ("auto", 22, "high"),
        ("health", 55, "medium"),
        ("home", 45, "low")
    ]

    for insurance_type, age, risk in test_cases:
        premium = estimate_premium.invoke({
            "insurance_type": insurance_type,
            "age": age,
            "risk_category": risk
        })
        print(f"{insurance_type.capitalize()} | Age {age} | Risk {risk} → €{premium}/month")

    print()


def test_provider_eligibility():
    """Test provider eligibility checking"""
    print("=" * 50)
    print("TEST 4: Check Provider Eligibility")
    print("=" * 50)

    test_cases = [
        ("generali", "life", 35, "low"),
        ("unipolsai", "auto", 20, "high"),  # Should fail: age < 21
        ("allianz", "health", 70, "medium"),  # Should fail: age > 65
        ("axa", "home", 40, "high"),  # Should pass
    ]

    for provider, ins_type, age, risk in test_cases:
        result = check_provider_eligibility.invoke({
            "provider": provider,
            "insurance_type": ins_type,
            "age": age,
            "risk_category": risk
        })

        status = "✓ ELIGIBLE" if result['eligible'] else "✗ NOT ELIGIBLE"
        print(f"\n{provider.upper()} | {ins_type} | Age {age} | Risk {risk}")
        print(f"  {status}")
        print(f"  Reason: {result['reason']}")

    print()


if __name__ == "__main__":
    print("\n🧪 TESTING INSURANCE ELIGIBILITY TOOLS\n")

    test_calculate_age()
    test_assess_risk()
    test_estimate_premium()
    test_provider_eligibility()

    print("=" * 50)
    print("✅ All tests completed!")
    print("=" * 50)
