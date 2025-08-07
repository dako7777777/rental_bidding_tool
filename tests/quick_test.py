#!/usr/bin/env python3
"""Quick test of the exact user scenario"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT, BUDGET_FLEXIBILITY

print("\nTesting User's Exact Scenario:")
print("=" * 60)

# Load Burnaby market
market_data = load_market_data('burnaby')

# Exact user inputs
user_prefs = {
    'max_budget': 2500,
    'property_value': 3,
    'risk_tolerance': 3
}

rental_situation = {
    'listing_price': 2500,
    'neighborhood_avg': 2450,
    'days_on_market': 7,
    'price_sens_landlord': 2,
    'competitive_level': 2
}

print(f"Budget: ${user_prefs['max_budget']}")
print(f"Flexible Budget (110%): ${user_prefs['max_budget'] * 1.1:.0f}")
print(f"Listing: ${rental_situation['listing_price']}")
print(f"Market Median: {market_data['parameters']['median']:.0%} = ${market_data['parameters']['median'] * rental_situation['listing_price']:.0f}")

# Create game state
game_state = GameState(
    user_preferences=user_prefs,
    rental_situation=rental_situation,
    market_params=market_data,
    property_value_weight=PROPERTY_VALUE_WEIGHT,
    overpayment_weight=OVERPAYMENT_WEIGHT,
    round=1,
    risk_tolerance=user_prefs['risk_tolerance'],
    user_bid=None,
    won_property=False
)

# Generate strategies
print("\nGenerating recommendations...")
recommendations = generate_three_strategies(game_state)

print("\nRESULTS:")
print("=" * 60)

for strategy in ['conservative', 'balanced', 'aggressive']:
    data = recommendations[strategy]
    print(f"\n{strategy.upper()}:")
    print(f"  Bid: ${data['bid']:.0f} ({data['bid']/2500:.1%} of listing)")
    print(f"  Win Probability: {data['win_probability']:.0%}")
    print(f"  Expected Overpayment: ${data['expected_overpayment']:.0f}")

# Check improvements
print("\n" + "=" * 60)
bids = [recommendations[s]['bid'] for s in ['conservative', 'balanced', 'aggressive']]
probs = [recommendations[s]['win_probability'] for s in ['conservative', 'balanced', 'aggressive']]

if len(set(bids)) >= 2 and max(probs) > 0.20:
    print("✅ SUCCESS: Algorithm is working correctly!")
    print(f"   - Bids are differentiated: ${bids[0]:.0f}, ${bids[1]:.0f}, ${bids[2]:.0f}")
    print(f"   - Win probabilities are reasonable: {probs[0]:.0%}, {probs[1]:.0%}, {probs[2]:.0%}")
else:
    print("⚠️  Algorithm needs further tuning")
