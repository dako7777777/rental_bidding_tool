"""Strategy generation logic for rental bidding"""

import copy
from algorithm.expectiminimax import expectiminimax
from models.distributions import get_competitor_bid_distribution
from models.payoff import calculate_fair_market_value, evaluate
from models.market import classify_market_conditions
from config.constants import TREE_DEPTH, PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT, BUDGET_FLEXIBILITY


def generate_three_strategies(base_state):
    """
    Generate aggressive, balanced, and conservative strategies
    
    Returns:
        dict: Three strategy recommendations
    """
    strategies = {}
    
    # Create more differentiated strategies
    # Map base risk tolerance to strategy-specific values
    base_risk = base_state.risk_tolerance
    
    # Conservative: Lower risk tolerance, prioritize avoiding overpayment
    conservative_state = copy.deepcopy(base_state)
    # Conservative maps to 1-2 risk level
    conservative_state.risk_tolerance = max(1, base_risk - 1.5)
    conservative_state.overpayment_weight = OVERPAYMENT_WEIGHT * 1.3  # More cautious about overpaying
    conservative_state.property_value_weight = PROPERTY_VALUE_WEIGHT * 0.9  # Less aggressive about winning
    
    # Balanced: Use original user preferences with slight adjustments
    balanced_state = copy.deepcopy(base_state)
    balanced_state.risk_tolerance = base_risk  # Keep original
    balanced_state.overpayment_weight = OVERPAYMENT_WEIGHT  # Standard weights
    balanced_state.property_value_weight = PROPERTY_VALUE_WEIGHT
    
    # Aggressive: Higher risk tolerance, prioritize winning
    aggressive_state = copy.deepcopy(base_state)
    # Aggressive maps to 4-5 risk level
    aggressive_state.risk_tolerance = min(5, base_risk + 1.5)
    aggressive_state.overpayment_weight = OVERPAYMENT_WEIGHT * 0.7  # Less concerned about overpaying
    aggressive_state.property_value_weight = PROPERTY_VALUE_WEIGHT * 1.2  # Prioritize winning
    
    # Run expectiminimax for each strategy
    for strategy_name, state in [
        ('conservative', conservative_state),
        ('balanced', balanced_state),
        ('aggressive', aggressive_state)
    ]:
        # Use consistent tree depth
        value, bid = expectiminimax(state, TREE_DEPTH, -float('inf'), float('inf'), True)
        
        # Calculate flexible budget
        flexible_budget = state.max_budget * (1 + BUDGET_FLEXIBILITY)
        
        # Handle None bid (fallback to minimum viable bid)
        if bid is None:
            bid = min(0.85 * state.listing_price, flexible_budget)
            state.user_bid = bid
            value = evaluate(state)
        
        # Ensure bid is within flexible budget constraints
        if bid > flexible_budget:
            bid = flexible_budget
            # Recalculate value for budget-constrained bid
            state.user_bid = bid
            value = evaluate(state)
        
        # Calculate metrics
        win_prob = calculate_win_probability(bid, state)
        exp_overpay = calculate_expected_overpayment(bid, state)
        
        strategies[strategy_name] = {
            'bid': bid,
            'win_probability': win_prob,
            'expected_overpayment': exp_overpay,
            'strategy_description': get_strategy_description(
                strategy_name, state, bid, win_prob
            ),
            'payoff_value': value
        }
    
    return strategies


def calculate_win_probability(bid, state):
    """
    Calculate probability of winning with given bid
    """
    competitor_dist = get_competitor_bid_distribution(state)
    win_prob = sum(prob for comp_bid, prob in competitor_dist if bid > comp_bid)
    return win_prob


def calculate_expected_overpayment(bid, state):
    """
    Calculate expected overpayment conditional on winning
    """
    fair_value = calculate_fair_market_value(
        state.listing_price, 
        state.neighborhood_avg,
        state.days_on_market,
        state.market_params
    )
    overpayment = bid - fair_value
    
    # Return actual overpayment (can be negative for good deals)
    return overpayment


def get_strategy_description(strategy_name, state, bid, win_prob):
    """
    Generate strategy description based on market conditions and bid details
    """
    market_condition = classify_market_conditions(state.market_params)
    bid_ratio = bid / state.listing_price
    
    descriptions = {
        'conservative': {
            'very_cool': f"Bid at {bid_ratio:.1%} of listing. Strong negotiating position in buyer's market.",
            'cooling': f"Bid at {bid_ratio:.1%} of listing to leverage market conditions while showing interest.",
            'balanced': f"Modest bid at {bid_ratio:.1%} of listing, accepting lower win probability for value.",
            'very_hot': f"Careful bid at {bid_ratio:.1%} of listing, may need to be flexible in hot market."
        },
        'balanced': {
            'very_cool': f"Strategic bid at {bid_ratio:.1%} of listing with {win_prob:.0%} win probability.",
            'cooling': f"Market-aligned bid at {bid_ratio:.1%} of listing, balancing value and success rate.",
            'balanced': f"Fair bid at {bid_ratio:.1%} of listing, matching market expectations.",
            'very_hot': f"Competitive bid at {bid_ratio:.1%} of listing to stay in contention."
        },
        'aggressive': {
            'very_cool': f"Strong bid at {bid_ratio:.1%} of listing to secure property despite market advantage.",
            'cooling': f"Above-market bid at {bid_ratio:.1%} of listing for {win_prob:.0%} win probability.",
            'balanced': f"Premium bid at {bid_ratio:.1%} of listing to maximize success chances.",
            'very_hot': f"Maximum competitive bid at {bid_ratio:.1%} of listing in seller's market."
        }
    }
    
    return descriptions[strategy_name][market_condition] 