"""
Test the provider loader to ensure JSON files are loaded correctly.
"""

from app.provider_loader import ProviderRulesLoader

print("=" * 60)
print("TEST: Provider Rules Loader")
print("=" * 60)

# Test 1: Load all providers
print("\n1. Loading all providers...")
try:
    all_providers = ProviderRulesLoader.load_all_providers()
    print(f"✓ Loaded {len(all_providers)} providers:")
    for code in all_providers.keys():
        provider_name = all_providers[code]['provider_name']
        num_products = len(all_providers[code]['products'])
        print(f"  - {code}: {provider_name} ({num_products} products)")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 2: Get specific provider
print("\n2. Getting specific provider (Generali)...")
try:
    generali = ProviderRulesLoader.get_provider('generali')
    if generali:
        print(f"✓ Provider: {generali['provider_name']}")
        print(f"  Country: {generali['country']}")
        print(f"  Last Updated: {generali['last_updated']}")
        print(f"  Products: {', '.join(generali['products'].keys())}")
    else:
        print("✗ Generali not found")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Get product rules
print("\n3. Getting product rules (Generali Life Insurance)...")
try:
    life_rules = ProviderRulesLoader.get_product_rules('generali', 'life')
    if life_rules:
        print(f"✓ Life Insurance Rules:")
        print(f"  Age Range: {life_rules['age_min']}-{life_rules['age_max']}")
        print(f"  Max Risk: {life_rules['max_risk']}")
        print(f"  Base Premium: €{life_rules['base_premium']}/month")
        print(f"  Description: {life_rules['description']}")
    else:
        print("✗ Life insurance rules not found")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: List all providers
print("\n4. Listing all provider codes...")
try:
    codes = ProviderRulesLoader.list_providers()
    print(f"✓ Available providers: {', '.join(codes)}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test 5: Update provider product
print("\n5. Testing update (Generali life age_max 70 -> 72)...")
try:
    # Get current value
    before = ProviderRulesLoader.get_product_rules('generali', 'life')
    print(f"  Before: age_max = {before['age_max']}")

    # Update
    success = ProviderRulesLoader.update_provider_product(
        'generali',
        'life',
        {'age_max': 72}
    )

    if success:
        # Get updated value
        after = ProviderRulesLoader.get_product_rules('generali', 'life')
        print(f"  After: age_max = {after['age_max']}")
        print("✓ Update successful")

        # Revert back to original
        ProviderRulesLoader.update_provider_product(
            'generali',
            'life',
            {'age_max': 70}
        )
        print("  (Reverted to original value)")
    else:
        print("✗ Update failed")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("✅ All tests completed!")
print("=" * 60)
