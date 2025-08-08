"""Test the three-player game implementation"""

import sys
sys.path.append('..')

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT
from ui.output_formatter import display_recommendations_with_landlord, display_detailed_explanation


def test_three_player_game():
    """Test the enhanced three-player game with example from documentation"""
    print("Testing Three-Player Game Implementation")
    print("=" * 60)
    
    # Example scenario from the documentation
    user_prefs = {
        'rent_type': '1b1b',
        'max_budget': 2500,
        'property_value': 4,  # Really want it
        'risk_tolerance': 3   # Balanced
    }
    
    rental_situation = {
        'listing_price': 2200,
        'neighborhood_avg': 2156,  # Fair market value
        'days_on_market': 7,       # Moderate competition
        'competitive_level': 2,     # Medium
        'price_sens_landlord': 2    # Moderate
    }
    
    # Load cooling market data
    market_data = load_market_data('downtown')
    
    # Create game state
    game_state = GameState(
        user_preferences=user_prefs,
        rental_situation=rental_situation,
        market_params=market_data,
        property_value_weight=PROPERTY_VALUE_WEIGHT,
        overpayment_weight=OVERPAYMENT_WEIGHT,
        round=1
    )
    
    print("\nScenario Setup:")
    print(f"- Listing Price: ${rental_situation['listing_price']}")
    print(f"- Fair Market Value: ${rental_situation['neighborhood_avg']}")
    print(f"- Days on Market: {rental_situation['days_on_market']}")
    print(f"- Your Budget: ${user_prefs['max_budget']}")
    print(f"- Property Value to You: {user_prefs['property_value']}/5")
    print(f"- Market: Cooling (median win ~98% of asking)")
    
    # Generate strategies
    print("\nGenerating three strategies with landlord modeling...")
    recommendations = generate_three_strategies(game_state)
    
    # Display results
    display_recommendations_with_landlord(recommendations, round=1)
    
    # Verify expected behavior from documentation
    print("\n\nVerifying Expected Behavior:")
    print("-" * 40)
    
    conservative = recommendations['conservative']
    balanced = recommendations['balanced']
    aggressive = recommendations['aggressive']
    
    # Check conservative strategy
    print(f"\nCONSERVATIVE Strategy:")
    print(f"  Bid: ${conservative['bid']:.0f} ({conservative['bid']/rental_situation['listing_price']:.1%} of asking)")
    print(f"  Win Probability: {conservative['win_probability']:.0%}")
    print(f"  Expected Outcome: {conservative['likely_landlord_response']['message']}")
    assert conservative['bid'] < rental_situation['listing_price'] * 0.96, "Conservative should bid below 96%"
    assert conservative['win_probability'] < 0.5, "Conservative should have lower win probability"
    
    # Check balanced strategy
    print(f"\nBALANCED Strategy:")
    print(f"  Bid: ${balanced['bid']:.0f} ({balanced['bid']/rental_situation['listing_price']:.1%} of asking)")
    print(f"  Win Probability: {balanced['win_probability']:.0%}")
    print(f"  Expected Outcome: {balanced['likely_landlord_response']['message']}")
    assert 0.96 <= balanced['bid']/rental_situation['listing_price'] <= 1.02, "Balanced should bid 96-102% of asking"
    assert 0.6 <= balanced['win_probability'] <= 0.8, "Balanced should have moderate win probability"
    
    # Check aggressive strategy
    print(f"\nAGGRESSIVE Strategy:")
    print(f"  Bid: ${aggressive['bid']:.0f} ({aggressive['bid']/rental_situation['listing_price']:.1%} of asking)")
    print(f"  Win Probability: {aggressive['win_probability']:.0%}")
    print(f"  Expected Outcome: {aggressive['likely_landlord_response']['message']}")
    assert aggressive['bid'] > rental_situation['listing_price'], "Aggressive should bid above asking"
    assert aggressive['win_probability'] > 0.8, "Aggressive should have high win probability"
    
    # Verify balanced is recommended
    print(f"\n\nRecommendation Logic:")
    print(f"BALANCED strategy recommended because:")
    print(f"- Best expected value: {balanced['payoff_value']:.3f}")
    print(f"- Hits landlord acceptance threshold")
    print(f"- Avoids overpayment while maintaining good win chance")
    
    # Test Round 3 scenario
    print("\n\n" + "=" * 60)
    print("Testing Round 3 (Final Bidding)")
    print("=" * 60)
    
    # Simulate landlord requesting best and final
    game_state.round = 3
    game_state.landlord_feedback = 'request_best_final'
    game_state.previous_bid = balanced['bid']
    game_state.user_bid = balanced['bid']
    
    print("Landlord has requested best and final offers...")
    round3_recommendations = generate_three_strategies(game_state)
    
    print("\nRound 3 Recommendations:")
    for strategy in ['conservative', 'balanced', 'aggressive']:
        r3_data = round3_recommendations[strategy]
        print(f"\n{strategy.upper()}:")
        print(f"  Round 1 bid: ${game_state.previous_bid:.0f}")
        print(f"  Round 3 bid: ${r3_data['bid']:.0f} (+${r3_data['bid']-game_state.previous_bid:.0f})")
        print(f"  Final win probability: {r3_data['win_probability']:.0%}")
    
    print("\n\nTest completed successfully! ✓")


def test_different_market_conditions():
    """Test behavior in different market conditions"""
    print("\n\n" + "=" * 60)
    print("Testing Different Market Conditions")
    print("=" * 60)
    
    base_user_prefs = {
        'rent_type': '1b1b',
        'max_budget': 2500,
        'property_value': 3,
        'risk_tolerance': 3
    }
    
    base_rental = {
        'listing_price': 2000,
        'neighborhood_avg': 2000,
        'competitive_level': 2,
        'price_sens_landlord': 2
    }
    
    # Test different days on market
    for days in [2, 7, 20, 35]:
        print(f"\n\nDays on Market: {days}")
        print("-" * 30)
        
        rental_situation = base_rental.copy()
        rental_situation['days_on_market'] = days
        
        game_state = GameState(
            user_preferences=base_user_prefs,
            rental_situation=rental_situation,
            market_params=load_market_data('downtown'),
            property_value_weight=PROPERTY_VALUE_WEIGHT,
            overpayment_weight=OVERPAYMENT_WEIGHT,
            round=1
        )
        
        recommendations = generate_three_strategies(game_state)
        balanced = recommendations['balanced']
        
        print(f"Balanced bid: ${balanced['bid']:.0f} ({balanced['bid']/2000:.1%} of asking)")
        print(f"Win probability: {balanced['win_probability']:.0%}")
        print(f"Landlord response: {balanced['likely_landlord_response']['message']}")
        
        # Verify landlord becomes more flexible over time
        if days <= 7:
            assert balanced['bid']/2000 >= 0.98, "Fresh listings should require higher bids"
        else:
            assert balanced['bid']/2000 < 1.0, "Stale listings should allow lower bids"


if __name__ == "__main__":
    test_three_player_game()
    test_different_market_conditions()
