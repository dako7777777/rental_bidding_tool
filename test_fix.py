#!/usr/bin/env python3
"""Test script to verify the bug fix"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT


def test_bug_scenario():
    """Test the exact scenario from the bug report"""
    print("Testing Bug Fix: Burnaby Market with Budget < Listing Price")
    print("=" * 60)
    
    # Load Burnaby market data
    market_data = load_market_data('burnaby')
    
    # Create test inputs matching the bug scenario
    user_prefs = {
        'max_budget': 2500,
        'property_value': 3,
        'risk_tolerance': 3
    }
    
    rental_situation = {
        'listing_price': 2600,
        'neighborhood_avg': 2550,
        'days_on_market': 7,
        'price_sens_landlord': 2,
        'competitive_level': 2
    }
    
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
    print("\nGenerating strategies...")
    recommendations = generate_three_strategies(game_state)
    
    # Display results
    print("\nResults:")
    print("-" * 60)
    
    for strategy in ['conservative', 'balanced', 'aggressive']:
        data = recommendations[strategy]
        print(f"\n{strategy.upper()} STRATEGY:")
        print(f"  Bid: ${data['bid']:.0f} ({data['bid']/2600:.1%} of listing)")
        print(f"  Win Probability: {data['win_probability']:.0%}")
        print(f"  Expected Overpayment: ${data['expected_overpayment']:.0f}")
        print(f"  Payoff Value: {data['payoff_value']:.3f}")
    
    # Check if bug is fixed
    print("\n" + "=" * 60)
    print("Bug Fix Verification:")
    print("-" * 60)
    
    bids = [recommendations[s]['bid'] for s in ['conservative', 'balanced', 'aggressive']]
    unique_bids = len(set(bids))
    
    if unique_bids == 1:
        print("❌ BUG STILL PRESENT: All strategies have the same bid!")
        print(f"   All bids = ${bids[0]:.0f}")
    else:
        print("✅ BUG FIXED: Strategies have different bids!")
        print(f"   Conservative: ${bids[0]:.0f}")
        print(f"   Balanced: ${bids[1]:.0f}")
        print(f"   Aggressive: ${bids[2]:.0f}")
    
    # Additional checks
    if bids[0] <= bids[1] <= bids[2]:
        print("✅ Bid ordering correct (conservative ≤ balanced ≤ aggressive)")
    else:
        print("⚠️  Unexpected bid ordering")
    
    if all(bid <= 2500 for bid in bids):
        print("✅ All bids within budget constraint ($2500)")
    else:
        print("❌ Some bids exceed budget!")
    
    print("=" * 60)


if __name__ == "__main__":
    test_bug_scenario()
