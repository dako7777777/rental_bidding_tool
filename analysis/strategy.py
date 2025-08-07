"""Strategy generation logic for rental bidding"""

import copy
from algorithm.expectiminimax import expectiminimax
from models.distributions import get_competitor_bid_distribution
from models.payoff import calculate_fair_market_value, evaluate
from models.market import classify_market_conditions
from config.constants import TREE_DEPTH, PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT


def generate_three_strategies(base_state):
    """
    Generate aggressive, balanced, and conservative strategies
    
    Returns:
        dict: Three strategy recommendations
    """
    strategies = {}
    
    # Calculate proportional adjustments based on current risk tolerance
    risk_adjustment_factor = 0.3  # 30% adjustment from base
    
    # Conservative: Lower risk tolerance, prioritize avoiding overpayment
    conservative_state = copy.deepcopy(base_state)
    conservative_state.risk_tolerance = max(1, 
        base_state.risk_tolerance * (1 - risk_adjustment_factor))
    conservative_state.overpayment_weight = OVERPAYMENT_WEIGHT * 1.5
    
    # Balanced: Use original user preferences
    balanced_state = base_state
    
    # Aggressive: Higher risk tolerance, prioritize winning
    aggressive_state = copy.deepcopy(base_state)
    aggressive_state.risk_tolerance = min(5, 
        base_state.risk_tolerance * (1 + risk_adjustment_factor))
    aggressive_state.property_value_weight = PROPERTY_VALUE_WEIGHT * 1.3
    
    # Run expectiminimax for each strategy
    for strategy_name, state in [
        ('conservative', conservative_state),
        ('balanced', balanced_state),
        ('aggressive', aggressive_state)
    ]:
        # Use consistent tree depth
        value, bid = expectiminimax(state, TREE_DEPTH, -float('inf'), float('inf'), True)
        
        # Ensure bid is within budget constraints
        if bid and bid > state.max_budget:
            bid = state.max_budget
            # Recalculate value for budget-constrained bid
            state.user_bid = bid
            value = evaluate(state)
        
        # Calculate metrics
        win_prob = calculate_win_probability(bid, state) if bid else 0
        exp_overpay = calculate_expected_overpayment(bid, state) if bid else 0
        
        strategies[strategy_name] = {
            'bid': bid if bid else state.listing_price,
            'win_probability': win_prob,
            'expected_overpayment': exp_overpay,
            'strategy_description': get_strategy_description(
                strategy_name, state, bid if bid else state.listing_price, win_prob
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