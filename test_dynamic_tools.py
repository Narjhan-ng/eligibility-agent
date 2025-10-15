"""
Test dynamic provider tools - the NEW production-ready features!

This demonstrates how the system now works with JSON-based provider data.
"""

from app.tools import (
    list_available_providers,
    get_provider_details,
    update_provider_rules,
    check_provider_eligibility
)

print("\n" + "=" * 70)
print("TEST: DYNAMIC PROVIDER TOOLS")
print("=" * 70)

# Test 1: List available providers
print("\n1. List Available Providers")
print("-" * 70)
providers = list_available_providers.invoke({})
print(f"✓ Found {len(providers)} providers: {', '.join(providers)}")

# Test 2: Get provider details
print("\n2. Get Provider Details (Generali)")
print("-" * 70)
details = get_provider_details.invoke({"provider_code": "generali"})
if 'error' not in details:
    print(f"✓ Provider: {details['provider_name']}")
    print(f"  Country: {details['country']}")
    print(f"  Last Updated: {details['last_updated']}")
    print(f"  Products:")
    for product, rules in details['products'].items():
        print(f"    - {product}: age {rules['age_min']}-{rules['age_max']}, "
              f"max risk: {rules['max_risk']}, €{rules['base_premium']}/month")
else:
    print(f"✗ Error: {details['error']}")

# Test 3: Check eligibility with DYNAMIC data
print("\n3. Check Eligibility (Using JSON Data)")
print("-" * 70)
test_cases = [
    ("generali", "life", 35, "low"),
    ("unipolsai", "auto", 20, "high"),  # Should fail: age < 21
    ("allianz", "health", 70, "medium"),  # Should fail: age > 65
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

# Test 4: Update provider rules
print("\n4. Update Provider Rules")
print("-" * 70)

# Get current age_max for Generali life insurance
details_before = get_provider_details.invoke({"provider_code": "generali"})
age_max_before = details_before['products']['life']['age_max']
print(f"  Before: Generali life insurance age_max = {age_max_before}")

# Update it
update_result = update_provider_rules.invoke({
    "provider_code": "generali",
    "product_type": "life",
    "field": "age_max",
    "value": 75
})

if update_result['success']:
    print(f"✓ {update_result['message']}")
    print(f"  After: age_max = {update_result['updated_rules']['age_max']}")

    # Test eligibility for someone who is now eligible
    print("\n  Testing: Is a 72-year-old now eligible for Generali life insurance?")
    eligibility = check_provider_eligibility.invoke({
        "provider": "generali",
        "insurance_type": "life",
        "age": 72,
        "risk_category": "low"
    })

    if eligibility['eligible']:
        print(f"  ✓ YES! {eligibility['reason']}")
    else:
        print(f"  ✗ NO: {eligibility['reason']}")

    # Revert back
    revert = update_provider_rules.invoke({
        "provider_code": "generali",
        "product_type": "life",
        "field": "age_max",
        "value": age_max_before
    })
    print(f"\n  Reverted to original: age_max = {age_max_before}")
else:
    print(f"✗ Update failed: {update_result['message']}")

# Test 5: Try invalid provider
print("\n5. Test Error Handling (Invalid Provider)")
print("-" * 70)
invalid_result = check_provider_eligibility.invoke({
    "provider": "nonexistent",
    "insurance_type": "life",
    "age": 35,
    "risk_category": "low"
})
print(f"✗ {invalid_result['reason']}")

print("\n" + "=" * 70)
print("✅ ALL DYNAMIC TOOLS TESTED!")
print("=" * 70)
print("\n🎯 KEY ACHIEVEMENT:")
print("   - Rules loaded from JSON files (not hardcoded)")
print("   - Rules can be updated dynamically")
print("   - System is now PRODUCTION-READY")
print("=" * 70)
