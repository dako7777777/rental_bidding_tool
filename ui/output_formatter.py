"""Output formatting for terminal display"""

from models.market import classify_market_conditions


def display_recommendations(recommendations, round=1):
    """Display recommendations with market-aware formatting"""
    print(f"\nROUND {round} RECOMMENDATIONS:")
    print("=" * 60)
    
    # Sort strategies for consistent display
    strategy_order = ['conservative', 'balanced', 'aggressive']
    
    for i, strategy in enumerate(strategy_order, 1):
        data = recommendations[strategy]
        print(f"\n{i}. {strategy.upper()} STRATEGY", end="")
        if strategy == 'balanced':
            print(" [RECOMMENDED - Best Expected Value]")
        else:
            print()
        
        # Main metrics
        print(f"   Recommended Bid: ${data['bid']:,.0f}")
        print(f"   Win Probability: {data['win_probability']:.0%}")
        
        # Savings or overpayment
        if data['expected_overpayment'] < 0:
            print(f"   Expected Savings: ${-data['expected_overpayment']:,.0f} below market")
        else:
            print(f"   Expected Overpayment: ${data['expected_overpayment']:,.0f} above market")
        
        # Strategy description
        print(f"   Strategy: {data['strategy_description']}")
        
        # Show algorithm confidence (payoff value)
        confidence = "High" if data['payoff_value'] > 0.5 else "Medium" if data['payoff_value'] > 0 else "Low"
        print(f"   Algorithm Confidence: {confidence}")


def display_market_analysis(market_data, rental_situation):
    """Display market analysis summary"""
    market_condition = classify_market_conditions(market_data)
    median_bid = market_data['parameters']['median']
    
    print("\nMARKET ANALYSIS:")
    print("-" * 40)
    print(f"Market Condition: {market_condition.replace('_', ' ').title()}")
    print(f"Typical Winning Bid: {median_bid:.0%} of listing price")
    print(f"Property Freshness: ", end="")
    
    if rental_situation['days_on_market'] < 7:
        print("Fresh listing (high interest expected)")
    elif rental_situation['days_on_market'] < 14:
        print("Recent listing (moderate interest)")
    elif rental_situation['days_on_market'] < 30:
        print("Aging listing (negotiation opportunity)")
    else:
        print("Stale listing (strong negotiation position)") 