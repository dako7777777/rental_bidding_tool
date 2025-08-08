"""Enhanced output formatting for three-player game display"""

from models.market import classify_market_conditions
from config.constants import BUDGET_FLEXIBILITY


def display_recommendations_with_landlord(recommendations, round=1):
    """Display recommendations with landlord response predictions"""
    print(f"\nROUND {round} RECOMMENDATIONS:")
    print("=" * 60)
    
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
        
        # Landlord response prediction
        response = data.get('likely_landlord_response', {})
        if response:
            print(f"   Likely Landlord Response: {response.get('message', 'Unknown')}")
        
        if data.get('requires_negotiation'):
            print(f"   ⚠️  May require additional negotiation rounds")
        
        # Savings or overpayment
        if data['expected_overpayment'] < 0:
            print(f"   Expected Savings: ${-data['expected_overpayment']:,.0f} below market")
        else:
            print(f"   Expected Overpayment: ${data['expected_overpayment']:,.0f} above market")
        
        # Strategy description
        print(f"   Strategy: {data['strategy_description']}")
        
        # Algorithm confidence
        confidence = "High" if data['payoff_value'] > 0.5 else "Medium" if data['payoff_value'] > 0 else "Low"
        print(f"   Algorithm Confidence: {confidence}")


def display_recommendations(recommendations, round=1):
    """Legacy compatibility - redirect to enhanced version"""
    display_recommendations_with_landlord(recommendations, round)


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
    
    # Add landlord behavior prediction
    print(f"\nLandlord Behavior Prediction:")
    days = rental_situation['days_on_market']
    
    if days < 7:
        print("   - Landlord likely firm on price")
        print("   - May wait for multiple offers")
    elif days < 14:
        print("   - Landlord becoming more flexible")
        print("   - Open to reasonable offers")
    elif days < 30:
        print("   - Landlord motivated to close")
        print("   - Good negotiation opportunity")
    else:
        print("   - Landlord very motivated")
        print("   - Strong negotiation position for tenants")


def display_detailed_explanation(recommendations, market_data, rental_situation):
    """Provide detailed explanation of the recommendation logic"""
    print("\n\nDETAILED EXPLANATION:")
    print("=" * 60)
    
    # Market context
    market_condition = classify_market_conditions(market_data)
    print(f"\nMarket Context: {market_condition.replace('_', ' ').title()}")
    
    # Explain why balanced is recommended
    balanced = recommendations['balanced']
    print(f"\nWhy BALANCED strategy is recommended:")
    print(f"- Optimal trade-off between win probability ({balanced['win_probability']:.0%}) and value")
    
    if balanced['expected_overpayment'] < 0:
        print(f"- Potential to save ${-balanced['expected_overpayment']:,.0f} below market value")
    else:
        print(f"- Minimal overpayment of ${balanced['expected_overpayment']:,.0f}")
    
    # Landlord dynamics
    response = balanced.get('likely_landlord_response', {})
    if response.get('type') == 'accept':
        print("- High chance of immediate acceptance, avoiding negotiation")
    elif response.get('type') == 'counter_offer':
        print("- May require negotiation, but positions you well")
    
    # Compare with other strategies
    print("\nComparison with other strategies:")
    
    conservative = recommendations['conservative']
    aggressive = recommendations['aggressive']
    
    print(f"\nCONSERVATIVE:")
    print(f"- Lower win chance ({conservative['win_probability']:.0%})")
    if conservative.get('requires_negotiation'):
        print("- Likely requires negotiation, reducing its appeal")
    
    print(f"\nAGGRESSIVE:")
    print(f"- Higher win chance ({aggressive['win_probability']:.0%})")
    print(f"- But overpays by ${aggressive['expected_overpayment']:,.0f}")
    print(f"- The extra cost isn't justified by the probability gain")
