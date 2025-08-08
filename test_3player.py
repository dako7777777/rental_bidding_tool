#!/usr/bin/env python3
"""
Quick test of the new 3-player game implementation
"""

import sys
sys.path.append('/Users/seal/Projects/rental_bidding_tool')

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT

def test_3player_implementation():
    """Test the new 3-player game implementation"""
    
    print("Testing 3-Player Game Implementation")
    print("=" * 50)
    
    # Test market data
    market_data = load_market_data('downtown_vancouver')
    
    # Test user preferences
    user_prefs = {
        'max_budget': 2500,
        'property_value': 4,
        'risk_tolerance': 3
    }
    
    # Test rental situation
    rental_situation = {
        'listing_price': 2200,
        'neighborhood_avg': 2100,
        'days_on_market': 7,
        'price_sens_landlord': 2,
        'competitive_level': 2
    }
    
    # Create game state
    try:
        game_state = GameState(
            user_preferences=user_prefs,
            rental_situation=rental_situation,
            market_params=market_data,
            property_value_weight=PROPERTY_VALUE_WEIGHT,
            overpayment_weight=OVERPAYMENT_WEIGHT,
            round=1
        )
        print("✓ GameState creation successful")
        
        # Test strategy generation
        recommendations = generate_three_strategies(game_state)
        print("✓ Strategy generation successful")
        
        # Display results
        print("\nStrategy Results:")
        print("-" * 30)
        for strategy in ['conservative', 'balanced', 'aggressive']:
            data = recommendations[strategy]
            print(f"\n{strategy.upper()}:")
            print(f"  Bid: ${data['bid']:,.0f}")
            print(f"  Win Probability: {data['win_probability']:.1%}")
            if 'likely_landlord_response' in data:
                print(f"  Landlord Response: {data['likely_landlord_response']['message']}")
            print(f"  Expected Overpayment: ${data['expected_overpayment']:,.0f}")
            print(f"  Algorithm Confidence: {data['payoff_value']:.3f}")
        
        print("\n✅ 3-Player implementation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_3player_implementation()
