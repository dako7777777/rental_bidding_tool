#!/usr/bin/env python3
"""
Test script to verify all imports and basic functionality
Run this after setting up the project to ensure everything works
"""

import sys
import traceback


def test_imports():
    """Test that all modules can be imported"""
    
    print("Testing Rental Bidding Strategy Tool imports...")
    print("=" * 50)
    
    modules_to_test = [
        # External dependencies
        ('numpy', 'External dependency'),
        ('scipy', 'External dependency'),
        ('scipy.stats', 'External dependency'),
        
        # Config modules
        ('config.constants', 'Configuration'),
        ('config.market_data', 'Market data'),
        
        # Algorithm modules
        ('algorithm.game_state', 'Game state'),
        ('algorithm.expectiminimax', 'Core algorithm'),
        
        # Model modules
        ('models.mixture', 'Mixture distribution'),
        ('models.market', 'Market classification'),
        ('models.payoff', 'Payoff calculations'),
        ('models.distributions', 'Bid distributions'),
        
        # Analysis modules
        ('analysis.strategy', 'Strategy generation'),
        
        # UI modules
        ('ui.input_validator', 'Input validation'),
        ('ui.output_formatter', 'Output formatting'),
        ('ui.terminal_ui', 'Terminal interface'),
    ]
    
    failed = []
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✓ {description:25} ({module_name})")
        except ImportError as e:
            print(f"✗ {description:25} ({module_name})")
            print(f"  Error: {e}")
            failed.append((module_name, str(e)))
        except Exception as e:
            print(f"✗ {description:25} ({module_name})")
            print(f"  Unexpected error: {e}")
            failed.append((module_name, str(e)))
    
    print("=" * 50)
    
    if failed:
        print(f"\n❌ {len(failed)} module(s) failed to import:")
        for module, error in failed:
            print(f"   - {module}: {error}")
        print("\nPlease ensure:")
        print("1. All files are in the correct directories")
        print("2. Dependencies are installed: pip install numpy scipy")
        return False
    else:
        print("\n✅ All modules imported successfully!")
        return True


def test_basic_functionality():
    """Test basic functionality of key components"""
    
    print("\nTesting basic functionality...")
    print("=" * 50)
    
    try:
        # Test market data loading
        from config.market_data import load_market_data
        downtown_data = load_market_data('downtown')
        burnaby_data = load_market_data('burnaby')
        print("✓ Market data loading works")
        
        # Test game state creation
        from algorithm.game_state import GameState
        from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT
        
        test_state = GameState(
            user_preferences={'max_budget': 2500, 'property_value': 4, 'risk_tolerance': 3},
            rental_situation={
                'listing_price': 2200,
                'neighborhood_avg': 2100,
                'days_on_market': 7,
                'price_sens_landlord': 2,
                'competitive_level': 2
            },
            market_params=downtown_data,
            property_value_weight=PROPERTY_VALUE_WEIGHT,
            overpayment_weight=OVERPAYMENT_WEIGHT
        )
        print("✓ Game state creation works")
        
        # Test market classification
        from models.market import classify_market_conditions
        market_condition = classify_market_conditions(downtown_data)
        print(f"✓ Market classification works (Downtown: {market_condition})")
        
        # Test validator
        from ui.input_validator import InputValidator
        validator = InputValidator()
        validator.validate_budget(2500, 2200)
        print("✓ Input validation works")
        
        print("=" * 50)
        print("\n✅ All functionality tests passed!")
        print("\nThe tool is ready to use. Run: python main.py")
        return True
        
    except Exception as e:
        print(f"\n❌ Functionality test failed: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # First test imports
    if test_imports():
        # Then test functionality
        test_basic_functionality()
    else:
        sys.exit(1) 