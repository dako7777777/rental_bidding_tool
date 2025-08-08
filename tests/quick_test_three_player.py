"""Quick test of three-player game implementation"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT

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

# Create game state
print("Creating game state...")
game_state = GameState(
    user_preferences=user_prefs,
    rental_situation=rental_situation,
    market_params=load_market_data('downtown'),
    property_value_weight=PROPERTY_VALUE_WEIGHT,
    overpayment_weight=OVERPAYMENT_WEIGHT,
    round=1
)

print("Generating strategies...")
try:
    recommendations = generate_three_strategies(game_state)
    
    print("\nResults:")
    for strategy in ['conservative', 'balanced', 'aggressive']:
        data = recommendations[strategy]
        print(f"\n{strategy.upper()}:")
        print(f"  Bid: ${data['bid']:.0f}")
        print(f"  Win Prob: {data['win_probability']:.0%}")
        print(f"  Landlord: {data['likely_landlord_response']['message']}")
        
    print("\n✓ Test passed!")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
