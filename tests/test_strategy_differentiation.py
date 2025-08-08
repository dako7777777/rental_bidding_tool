"""Test strategy differentiation fix"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT

def test_strategy_differentiation():
    """Test that strategies are properly differentiated"""
    
    print("Testing Strategy Differentiation")
    print("=" * 60)
    
    # Test scenario from the user's run
    user_prefs = {
        'rent_type': '1b1b',
        'max_budget': 2500,
        'property_value': 4,
        'risk_tolerance': 3
    }
    
    rental_situation = {
        'listing_price': 2200,
        'neighborhood_avg': 2100,
        'days_on_market': 7,
        'competitive_level': 2,
        'price_sens_landlord': 2
    }
    
    # Test with Downtown (Very Cool market)
    market_data = load_market_data('downtown')
    
    print("\nRound 1 Test - Very Cool Market")
    print("-" * 40)
    
    game_state = GameState(
        user_preferences=user_prefs,
        rental_situation=rental_situation,
        market_params=market_data,
        property_value_weight=PROPERTY_VALUE_WEIGHT,
        overpayment_weight=OVERPAYMENT_WEIGHT,
        round=1
    )
    
    round1_strategies = generate_three_strategies(game_state)
    
    print("\nRound 1 Strategies:")
    for strategy in ['conservative', 'balanced', 'aggressive']:
        data = round1_strategies[strategy]
        print(f"\n{strategy.upper()}:")
        print(f"  Bid: ${data['bid']:.0f} ({data['bid']/2200:.1%} of asking)")
        print(f"  Win Prob: {data['win_probability']:.0%}")
        print(f"  Overpayment: ${data['expected_overpayment']:.0f}")
        print(f"  Payoff Value: {data['payoff_value']:.3f}")
    
    # Check differentiation
    conservative_bid = round1_strategies['conservative']['bid']
    balanced_bid = round1_strategies['balanced']['bid']
    aggressive_bid = round1_strategies['aggressive']['bid']
    
    print(f"\nDifferentiation Check:")
    print(f"Conservative to Balanced: ${balanced_bid - conservative_bid:.0f}")
    print(f"Balanced to Aggressive: ${aggressive_bid - balanced_bid:.0f}")
    
    if conservative_bid >= balanced_bid or balanced_bid >= aggressive_bid:
        print("⚠️ WARNING: Strategies not properly ordered!")
    else:
        print("✓ Strategies properly ordered (Conservative < Balanced < Aggressive)")
    
    # Test Round 3
    print("\n\nRound 3 Test - After Best & Final Request")
    print("-" * 40)
    
    game_state.round = 3
    game_state.landlord_feedback = 'request_best_final'
    game_state.previous_bid = balanced_bid
    game_state.user_bid = balanced_bid
    
    round3_strategies = generate_three_strategies(game_state)
    
    print("\nRound 3 Strategies:")
    for strategy in ['conservative', 'balanced', 'aggressive']:
        data = round3_strategies[strategy]
        increase = data['bid'] - balanced_bid
        print(f"\n{strategy.upper()}:")
        print(f"  Bid: ${data['bid']:.0f} (+${increase:.0f} from Round 1)")
        print(f"  Win Prob: {data['win_probability']:.0%}")
        print(f"  Payoff Value: {data['payoff_value']:.3f}")
    
    # Check Round 3 differentiation
    r3_conservative = round3_strategies['conservative']['bid']
    r3_balanced = round3_strategies['balanced']['bid']
    r3_aggressive = round3_strategies['aggressive']['bid']
    
    print(f"\nRound 3 Differentiation Check:")
    print(f"Conservative to Balanced: ${r3_balanced - r3_conservative:.0f}")
    print(f"Balanced to Aggressive: ${r3_aggressive - r3_balanced:.0f}")
    
    if r3_conservative >= r3_balanced or r3_balanced >= r3_aggressive:
        print("⚠️ WARNING: Round 3 strategies not properly ordered!")
    else:
        print("✓ Round 3 strategies properly ordered")
    
    # Test different market conditions
    print("\n\nTesting Different Market Conditions")
    print("-" * 40)
    
    for market_name, market_type in [('Downtown', 'downtown'), ('Burnaby', 'burnaby')]:
        market_data = load_market_data(market_type)
        game_state.market_params = market_data
        game_state.round = 1
        
        strategies = generate_three_strategies(game_state)
        
        print(f"\n{market_name} Market:")
        cons_bid = strategies['conservative']['bid']
        bal_bid = strategies['balanced']['bid']
        agg_bid = strategies['aggressive']['bid']
        
        print(f"  Conservative: ${cons_bid:.0f} ({cons_bid/2200:.1%})")
        print(f"  Balanced: ${bal_bid:.0f} ({bal_bid/2200:.1%})")
        print(f"  Aggressive: ${agg_bid:.0f} ({agg_bid/2200:.1%})")
        print(f"  Spread: ${agg_bid - cons_bid:.0f}")


if __name__ == "__main__":
    test_strategy_differentiation()
