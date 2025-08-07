#!/usr/bin/env python3
"""Test script to verify the improved bidding algorithm"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT, BUDGET_FLEXIBILITY
from models.market import classify_market_conditions


def test_improved_algorithm():
    """Test the improved algorithm with budget flexibility"""
    print("=" * 70)
    print("    TESTING IMPROVED RENTAL BIDDING ALGORITHM")
    print("=" * 70)
    
    # Test scenario from user feedback
    print("\nTest Scenario: Burnaby Market")
    print("-" * 40)
    
    # Load Burnaby market data
    market_data = load_market_data('burnaby')
    
    # Create test inputs
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
    
    print(f"User Budget: ${user_prefs['max_budget']}")
    print(f"Flexible Budget (with {BUDGET_FLEXIBILITY:.0%} flexibility): ${user_prefs['max_budget'] * (1 + BUDGET_FLEXIBILITY):.0f}")
    print(f"Listing Price: ${rental_situation['listing_price']}")
    print(f"Neighborhood Average: ${rental_situation['neighborhood_avg']}")
    print(f"Market Median Bid: {market_data['parameters']['median']:.0%} of listing = ${market_data['parameters']['median'] * rental_situation['listing_price']:.0f}")
    print(f"Market Condition: {classify_market_conditions(market_data).replace('_', ' ').title()}")
    
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
    print("\n" + "=" * 70)
    print("GENERATING STRATEGIES...")
    print("=" * 70)
    recommendations = generate_three_strategies(game_state)
    
    # Display results
    for strategy in ['conservative', 'balanced', 'aggressive']:
        data = recommendations[strategy]
        print(f"\n{strategy.upper()} STRATEGY:")
        print("-" * 40)
        print(f"  Recommended Bid: ${data['bid']:.0f} ({data['bid']/rental_situation['listing_price']:.1%} of listing)")
        print(f"  Win Probability: {data['win_probability']:.0%}")
        
        if data['expected_overpayment'] < 0:
            print(f"  Expected Savings: ${-data['expected_overpayment']:.0f} below market")
        else:
            print(f"  Expected Overpayment: ${data['expected_overpayment']:.0f} above market")
        
        print(f"  Payoff Value: {data['payoff_value']:.3f}")
        
        # Check if bid is within flexible budget
        flexible_budget = user_prefs['max_budget'] * (1 + BUDGET_FLEXIBILITY)
        if data['bid'] <= user_prefs['max_budget']:
            print(f"  ✅ Within stated budget")
        elif data['bid'] <= flexible_budget:
            print(f"  ⚠️  Uses budget flexibility (up to ${flexible_budget:.0f})")
        else:
            print(f"  ❌ Exceeds flexible budget!")
    
    # Verification checks
    print("\n" + "=" * 70)
    print("VERIFICATION CHECKS:")
    print("=" * 70)
    
    bids = [recommendations[s]['bid'] for s in ['conservative', 'balanced', 'aggressive']]
    win_probs = [recommendations[s]['win_probability'] for s in ['conservative', 'balanced', 'aggressive']]
    
    # Check 1: Different bids
    unique_bids = len(set(bids))
    if unique_bids >= 2:  # At least 2 different bids
        print("✅ Strategies have differentiated bids")
    else:
        print("❌ Strategies have identical bids!")
    
    # Check 2: Bid ordering
    if bids[0] <= bids[1] <= bids[2]:
        print("✅ Bid ordering correct (conservative ≤ balanced ≤ aggressive)")
    else:
        print("⚠️  Unexpected bid ordering")
    
    # Check 3: Win probability ordering
    if win_probs[0] <= win_probs[1] <= win_probs[2]:
        print("✅ Win probability ordering correct")
    else:
        print("⚠️  Unexpected win probability ordering")
    
    # Check 4: Reasonable win probabilities
    if win_probs[1] >= 0.20:  # Balanced should have at least 20% chance
        print("✅ Balanced strategy has reasonable win probability")
    else:
        print("⚠️  Win probabilities seem too low")
    
    # Check 5: Budget compliance
    flexible_budget = user_prefs['max_budget'] * (1 + BUDGET_FLEXIBILITY)
    if all(bid <= flexible_budget for bid in bids):
        print(f"✅ All bids within flexible budget (${flexible_budget:.0f})")
    else:
        print("❌ Some bids exceed flexible budget!")
    
    # Check 6: Market alignment
    market_median = market_data['parameters']['median'] * rental_situation['listing_price']
    balanced_bid = bids[1]
    if 0.9 * market_median <= balanced_bid <= 1.1 * market_median:
        print(f"✅ Balanced strategy near market median (${market_median:.0f})")
    else:
        print(f"⚠️  Balanced strategy far from market median")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


def test_different_scenarios():
    """Test multiple scenarios to ensure robustness"""
    print("\n\n" + "=" * 70)
    print("    TESTING DIFFERENT SCENARIOS")
    print("=" * 70)
    
    scenarios = [
        {
            'name': 'Budget Equals Listing',
            'budget': 2500,
            'listing': 2500,
            'neighborhood': 2450,
            'risk': 3
        },
        {
            'name': 'Budget Below Listing',
            'budget': 2300,
            'listing': 2500,
            'neighborhood': 2450,
            'risk': 3
        },
        {
            'name': 'Budget Above Listing',
            'budget': 2700,
            'listing': 2500,
            'neighborhood': 2450,
            'risk': 3
        },
        {
            'name': 'High Risk Tolerance',
            'budget': 2500,
            'listing': 2500,
            'neighborhood': 2450,
            'risk': 5
        },
        {
            'name': 'Low Risk Tolerance',
            'budget': 2500,
            'listing': 2500,
            'neighborhood': 2450,
            'risk': 1
        }
    ]
    
    market_data = load_market_data('burnaby')
    
    for scenario in scenarios:
        print(f"\n\nScenario: {scenario['name']}")
        print("-" * 40)
        print(f"Budget: ${scenario['budget']}, Listing: ${scenario['listing']}, Risk: {scenario['risk']}")
        
        user_prefs = {
            'max_budget': scenario['budget'],
            'property_value': 3,
            'risk_tolerance': scenario['risk']
        }
        
        rental_situation = {
            'listing_price': scenario['listing'],
            'neighborhood_avg': scenario['neighborhood'],
            'days_on_market': 7,
            'price_sens_landlord': 2,
            'competitive_level': 2
        }
        
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
        
        recommendations = generate_three_strategies(game_state)
        
        print("\nResults:")
        for strategy in ['conservative', 'balanced', 'aggressive']:
            data = recommendations[strategy]
            print(f"  {strategy.capitalize():12} Bid: ${data['bid']:6.0f} ({data['bid']/scenario['listing']:5.1%}) Win Prob: {data['win_probability']:5.0%}")


if __name__ == "__main__":
    test_improved_algorithm()
    test_different_scenarios()
