"""Complete test of three-player game with Round 3"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT

def test_complete_flow():
    """Test complete bidding flow from Round 1 to Round 3"""
    
    print("=== Testing Complete Three-Player Game Flow ===\n")
    
    # Test data
    user_prefs = {
        'rent_type': '1b1b',
        'max_budget': 2500,
        'property_value': 4,
        'risk_tolerance': 3
    }
    
    rental_situation = {
        'listing_price': 2200,
        'neighborhood_avg': 2156,
        'days_on_market': 7,
        'competitive_level': 2,
        'price_sens_landlord': 2
    }
    
    market_data = load_market_data('downtown')
    
    # Round 1
    print("ROUND 1: Initial Bidding")
    print("-" * 30)
    
    game_state = GameState(
        user_preferences=user_prefs,
        rental_situation=rental_situation,
        market_params=market_data,
        property_value_weight=PROPERTY_VALUE_WEIGHT,
        overpayment_weight=OVERPAYMENT_WEIGHT,
        round=1
    )
    
    round1_recommendations = generate_three_strategies(game_state)
    
    # Let's say user chose balanced strategy
    chosen_bid = round1_recommendations['balanced']['bid']
    print(f"User chooses BALANCED strategy: ${chosen_bid:.0f}")
    print(f"Expected response: {round1_recommendations['balanced']['likely_landlord_response']['message']}")
    
    # Simulate landlord requesting best and final
    print("\n\nROUND 2: Landlord Response")
    print("-" * 30)
    print("Landlord requests best and final offers from all bidders")
    
    # Round 3
    print("\n\nROUND 3: Final Bidding")
    print("-" * 30)
    
    # Update game state for Round 3
    game_state.round = 3
    game_state.landlord_feedback = 'request_best_final'
    game_state.previous_bid = chosen_bid
    game_state.user_bid = chosen_bid
    
    try:
        round3_recommendations = generate_three_strategies(game_state)
        
        print(f"Previous bid: ${chosen_bid:.0f}")
        print("\nRound 3 Recommendations:")
        
        for strategy in ['conservative', 'balanced', 'aggressive']:
            data = round3_recommendations[strategy]
            increase = data['bid'] - chosen_bid
            increase_pct = (data['bid'] / chosen_bid - 1) * 100
            
            print(f"\n{strategy.upper()}:")
            print(f"  New bid: ${data['bid']:.0f} (+${increase:.0f}, +{increase_pct:.1f}%)")
            print(f"  Win probability: {data['win_probability']:.0%}")
            print(f"  Landlord response: {data['likely_landlord_response']['message']}")
        
        print("\n✓ Complete flow test passed!")
        
    except Exception as e:
        print(f"\n✗ Error in Round 3: {e}")
        import traceback
        traceback.print_exc()
        
    # Test counter-offer scenario
    print("\n\n=== Testing Counter-Offer Scenario ===\n")
    
    game_state2 = GameState(
        user_preferences=user_prefs,
        rental_situation=rental_situation,
        market_params=market_data,
        property_value_weight=PROPERTY_VALUE_WEIGHT,
        overpayment_weight=OVERPAYMENT_WEIGHT,
        round=3
    )
    
    # Conservative bid that triggers counter
    conservative_bid = 2090
    game_state2.landlord_feedback = 'counter_offer'
    game_state2.counter_price = 2200  # Landlord counters at asking
    game_state2.previous_bid = conservative_bid
    game_state2.user_bid = conservative_bid
    
    print(f"User's conservative bid: ${conservative_bid}")
    print(f"Landlord counters at: ${game_state2.counter_price}")
    
    try:
        counter_recommendations = generate_three_strategies(game_state2)
        
        print("\nOptions:")
        for strategy in ['conservative', 'balanced', 'aggressive']:
            data = counter_recommendations[strategy]
            print(f"\n{strategy.upper()}: ${data['bid']:.0f}")
            if data['bid'] == game_state2.counter_price:
                print("  → Accept counter offer")
            else:
                print("  → Stick with original bid (may lose property)")
                
        print("\n✓ Counter-offer test passed!")
        
    except Exception as e:
        print(f"\n✗ Error in counter-offer: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_complete_flow()
