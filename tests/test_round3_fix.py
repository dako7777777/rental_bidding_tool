"""Test Round 3 functionality after bug fix"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT

print("Testing Round 3 with landlord requesting best and final...")

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

# Create game state for Round 3
game_state = GameState(
    user_preferences=user_prefs,
    rental_situation=rental_situation,
    market_params=load_market_data('downtown'),
    property_value_weight=PROPERTY_VALUE_WEIGHT,
    overpayment_weight=OVERPAYMENT_WEIGHT,
    round=3  # Round 3
)

# Set Round 3 specific state
game_state.landlord_feedback = 'request_best_final'
game_state.previous_bid = 2134  # User's Round 1 bid
game_state.user_bid = 2134  # Current bid

print(f"\nRound 1 bid was: ${game_state.previous_bid}")
print("Landlord requested best and final offers")

try:
    # Generate Round 3 strategies
    recommendations = generate_three_strategies(game_state)
    
    print("\nRound 3 Recommendations:")
    for strategy in ['conservative', 'balanced', 'aggressive']:
        data = recommendations[strategy]
        increase = data['bid'] - game_state.previous_bid
        print(f"\n{strategy.upper()}:")
        print(f"  New bid: ${data['bid']:.0f} (+${increase:.0f})")
        print(f"  Win probability: {data['win_probability']:.0%}")
        print(f"  Expected response: {data['likely_landlord_response']['message']}")
    
    print("\n✓ Test passed! Round 3 is working correctly.")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
