"""
Provider rules loader - Dynamic provider data management.

This module handles loading and updating insurance provider rules from JSON files.
This makes the system more realistic and maintainable:
- Rules can be updated without changing code
- New providers can be added by adding JSON files
- Business users can modify rules without developer intervention

=== WHY DYNAMIC LOADING? ===

In real insurance systems:
- Rules change frequently (new regulations, market conditions)
- Different regions have different rules
- Providers update their offerings
- Manual code changes are slow and error-prone

By loading from JSON:
- Changes take effect immediately
- Non-technical users can update rules
- Version control for rule changes (git diff on JSON)
- Easy to add new providers
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime


class ProviderRulesLoader:
    """
    Manages loading and updating insurance provider rules from JSON files.

    === SINGLETON PATTERN ===
    This class uses a singleton-like pattern with class variables.
    This ensures all tools use the same loaded data without reloading files.

    In production, you might use:
    - Redis cache
    - Database with caching layer
    - API calls with local cache
    """

    # Class variable - shared across all instances
    # This acts as an in-memory cache of loaded rules
    _rules_cache: Dict[str, Any] = {}

    # Directory where provider JSON files are stored
    _providers_dir = Path(__file__).parent.parent / "data" / "providers"

    @classmethod
    def load_all_providers(cls) -> Dict[str, Any]:
        """
        Load all provider rules from JSON files.

        Returns:
            Dict with provider_code as key, full provider data as value

        Example:
            {
                "generali": {
                    "provider_name": "Generali",
                    "products": {...}
                },
                "axa": {...}
            }

        === HOW IT WORKS ===
        1. Scan data/providers/ directory for .json files
        2. Load each file
        3. Validate structure
        4. Store in cache
        5. Return all rules
        """
        # If already loaded, return cached version
        # This avoids reading files on every tool call
        if cls._rules_cache:
            return cls._rules_cache

        # Ensure directory exists
        if not cls._providers_dir.exists():
            raise FileNotFoundError(
                f"Providers directory not found: {cls._providers_dir}. "
                "Please create data/providers/ and add provider JSON files."
            )

        # Load all JSON files in the providers directory
        rules = {}

        # Get all .json files
        json_files = list(cls._providers_dir.glob("*.json"))

        if not json_files:
            raise ValueError(
                f"No provider JSON files found in {cls._providers_dir}. "
                "Please add at least one provider file (e.g., generali.json)."
            )

        # Load each provider file
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    provider_data = json.load(f)

                # Validate required fields
                required_fields = ['provider_code', 'provider_name', 'products']
                for field in required_fields:
                    if field not in provider_data:
                        raise ValueError(
                            f"Provider file {json_file.name} missing required field: {field}"
                        )

                # Store using provider_code as key
                provider_code = provider_data['provider_code'].lower()
                rules[provider_code] = provider_data

            except json.JSONDecodeError as e:
                # Skip invalid JSON files but log the error
                print(f"Warning: Could not parse {json_file.name}: {e}")
                continue
            except Exception as e:
                print(f"Warning: Error loading {json_file.name}: {e}")
                continue

        if not rules:
            raise ValueError("No valid provider rules could be loaded.")

        # Cache the loaded rules
        cls._rules_cache = rules

        return rules

    @classmethod
    def get_provider(cls, provider_code: str) -> Optional[Dict[str, Any]]:
        """
        Get rules for a specific provider.

        Args:
            provider_code: Provider code (e.g., 'generali', 'axa')

        Returns:
            Provider data dict or None if not found

        === USAGE IN TOOLS ===
        Tools can call this to get provider-specific rules:

        rules = ProviderRulesLoader.get_provider('generali')
        if rules:
            life_insurance = rules['products']['life']
        """
        # Ensure rules are loaded
        if not cls._rules_cache:
            cls.load_all_providers()

        return cls._rules_cache.get(provider_code.lower())

    @classmethod
    def list_providers(cls) -> List[str]:
        """
        Get list of all available provider codes.

        Returns:
            List of provider codes

        Example:
            ['generali', 'axa', 'allianz', 'unipolsai']
        """
        if not cls._rules_cache:
            cls.load_all_providers()

        return list(cls._rules_cache.keys())

    @classmethod
    def update_provider_product(
        cls,
        provider_code: str,
        product_type: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update a specific product's rules for a provider.

        Args:
            provider_code: Provider to update (e.g., 'generali')
            product_type: Product to update (e.g., 'life', 'auto')
            updates: Dict with fields to update (e.g., {'age_max': 75})

        Returns:
            True if successful, False otherwise

        Example:
            ProviderRulesLoader.update_provider_product(
                'generali',
                'life',
                {'age_max': 75, 'max_risk': 'high'}
            )

        === WHAT THIS DOES ===
        1. Load current rules
        2. Update specified fields in memory
        3. Write updated data back to JSON file
        4. Update cache

        === WHY USEFUL ===
        - Provider changes their rules -> update via API/tool
        - A/B testing different rules
        - Temporary rule changes (promotions)
        """
        # Ensure rules are loaded
        if not cls._rules_cache:
            cls.load_all_providers()

        provider_code_lower = provider_code.lower()

        # Check if provider exists
        if provider_code_lower not in cls._rules_cache:
            print(f"Error: Provider '{provider_code}' not found")
            return False

        # Check if product exists
        provider_data = cls._rules_cache[provider_code_lower]
        if product_type not in provider_data['products']:
            print(f"Error: Product '{product_type}' not found for provider '{provider_code}'")
            return False

        # Update the product rules in memory
        for key, value in updates.items():
            provider_data['products'][product_type][key] = value

        # Update last_updated timestamp
        provider_data['last_updated'] = datetime.now().strftime('%Y-%m-%d')

        # Write back to JSON file
        json_file = cls._providers_dir / f"{provider_code_lower}.json"

        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(provider_data, f, indent=2, ensure_ascii=False)

            # Update cache
            cls._rules_cache[provider_code_lower] = provider_data

            return True

        except Exception as e:
            print(f"Error writing to {json_file}: {e}")
            return False

    @classmethod
    def reload_providers(cls) -> Dict[str, Any]:
        """
        Force reload all provider rules from disk.

        Returns:
            Updated rules dict

        === WHEN TO USE ===
        - After manual JSON file edits
        - After updates from external systems
        - To ensure fresh data
        """
        # Clear cache
        cls._rules_cache = {}

        # Reload from files
        return cls.load_all_providers()

    @classmethod
    def get_product_rules(
        cls,
        provider_code: str,
        product_type: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get rules for a specific product from a specific provider.

        Args:
            provider_code: Provider code
            product_type: Product type (life, auto, home, health)

        Returns:
            Product rules dict or None if not found

        Example:
            rules = ProviderRulesLoader.get_product_rules('generali', 'life')
            # Returns: {'age_min': 18, 'age_max': 70, 'max_risk': 'high', ...}
        """
        provider = cls.get_provider(provider_code)
        if not provider:
            return None

        return provider.get('products', {}).get(product_type)


# === MODULE-LEVEL CONVENIENCE FUNCTION ===
# This allows simple imports: from app.provider_loader import load_providers
def load_providers() -> Dict[str, Any]:
    """Convenience function to load all providers."""
    return ProviderRulesLoader.load_all_providers()
