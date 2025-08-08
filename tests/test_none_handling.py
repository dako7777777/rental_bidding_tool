"""Test the bug fixes for None value handling"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT

def test_none_handling():
    """Test that the system handles None values properly"""
    
    print("Testing None value handling in three-player game...")
    print("=" * 60)
    
    # Test scenario from the error report
    user_prefs = {
        'rent_type': '1b1b',
        'max_budget': 2500,
        'property_value': 4,
        'risk_tolerance': 3
    }
    
    rental_situation = {
        'listing_price': 2200,
        'neighborhood_avg': 2100,  # Different from error report
        'days_on_market': 7,
        'competitive_level': 2,
        'price_sens_landlord': 2
    }
    
    # Load very cool market (as shown in error)
    market_data = load_market_data('burnaby')  # Burnaby has more pronounced cooling
    
    print("\nTest Case 1: Initial strategy generation")
    print("-" * 40)
    print(f"Market: {market_data['distribution_type']}")
    print(f"Median: {market_data['parameters']['median']:.2f}")
    
    try:
        # Create initial game state
        game_state = GameState(
            user_preferences=user_prefs,
            rental_situation=rental_situation,
            market_params=market_data,
            property_value_weight=PROPERTY_VALUE_WEIGHT,
            overpayment_weight=OVERPAYMENT_WEIGHT,
            round=1
        )
        
        # This should not have user_bid set yet
        assert game_state.user_bid is None, "Initial state should have None user_bid"
        
        # Generate strategies
        recommendations = generate_three_strategies(game_state)
        
        print("\nSuccessfully generated strategies:")
        for strategy in ['conservative', 'balanced', 'aggressive']:
            data = recommendations[strategy]
            print(f"\n{strategy.upper()}:")
            print(f"  Bid: ${data['bid']:.0f} ({data['bid']/2200:.1%} of asking)")
            print(f"  Win Prob: {data['win_probability']:.0%}")
            
        print("\n✓ Test Case 1 passed!")
        
    except Exception as e:
        print(f"\n✗ Test Case 1 failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Case 2: Intermediate state with partial information
    print("\n\nTest Case 2: Intermediate state handling")
    print("-" * 40)
    
    try:
        # Create a state that might occur during tree exploration
        intermediate_state = GameState(
            user_preferences=user_prefs,
            rental_situation=rental_situation,
            market_params=market_data,
            property_value_weight=PROPERTY_VALUE_WEIGHT,
            overpayment_weight=OVERPAYMENT_WEIGHT,
            round=1
        )
        
        # Manually set some fields to test edge cases
        intermediate_state.user_bid = None
        intermediate_state.highest_competitor_bid = 2100
        
        # Test landlord actions with partial state
        from algorithm.landlord_model import get_landlord_actions
        actions = get_landlord_actions(intermediate_state)
        
        print(f"Landlord actions with None user_bid: {len(actions)} actions")
        print("Expected: 0 actions (no tenant bid to evaluate)")
        
        assert len(actions) == 0, "Should return no actions when user_bid is None"
        
        print("\n✓ Test Case 2 passed!")
        
    except Exception as e:
        print(f"\n✗ Test Case 2 failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n\nAll tests passed! The None value handling is working correctly.")
    return True


if __name__ == "__main__":
    test_none_handling()
