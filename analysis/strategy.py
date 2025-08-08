"""Enhanced strategy generation for three-player rental bidding"""

import copy
from algorithm.expectiminimax_landlord import expectiminimax_with_landlord
from algorithm.landlord_model import LandlordProfile
from models.distributions import get_competitor_bid_distribution
from models.payoff import calculate_fair_market_value
from models.market import classify_market_conditions
from config.constants import TREE_DEPTH, PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT, BUDGET_FLEXIBILITY


def generate_three_strategies(base_state):
    """
    Generate three strategies accounting for landlord's strategic behavior
    """
    strategies = {}
    
    # Calculate proportional adjustments
    risk_adjustment_factor = 0.3
    
    # Conservative: Aims to avoid negotiation rounds
    conservative_state = copy.deepcopy(base_state)
    conservative_state.risk_tolerance = max(1, 
        base_state.risk_tolerance * (1 - risk_adjustment_factor))
    conservative_state.negotiation_cost = 0.1  # Higher penalty for multiple rounds
    conservative_state.overpayment_weight = OVERPAYMENT_WEIGHT * 1.3
    conservative_state.property_value_weight = PROPERTY_VALUE_WEIGHT * 0.9
    
    # Balanced: Standard preferences
    balanced_state = copy.deepcopy(base_state)
    balanced_state.negotiation_cost = 0.05  # Moderate penalty
    balanced_state.overpayment_weight = OVERPAYMENT_WEIGHT
    balanced_state.property_value_weight = PROPERTY_VALUE_WEIGHT
    
    # Aggressive: Willing to go through negotiation
    aggressive_state = copy.deepcopy(base_state)
    aggressive_state.risk_tolerance = min(5,
        base_state.risk_tolerance * (1 + risk_adjustment_factor))
    aggressive_state.negotiation_cost = 0.02  # Lower penalty for multiple rounds
    aggressive_state.overpayment_weight = OVERPAYMENT_WEIGHT * 0.7
    aggressive_state.property_value_weight = PROPERTY_VALUE_WEIGHT * 1.2
    
    for strategy_name, state in [
        ('conservative', conservative_state),
        ('balanced', balanced_state),
        ('aggressive', aggressive_state)
    ]:
        # Run enhanced expectiminimax
        value, bid = expectiminimax_with_landlord(
            state, TREE_DEPTH, -float('inf'), float('inf'), 'tenant_max'
        )
        
        # Handle None bid (fallback)
        if bid is None:
            bid = min(0.85 * state.listing_price, state.max_budget)
        
        # Calculate metrics including landlord response probability
        win_prob = calculate_win_probability_with_landlord(bid, state)
        exp_overpay = calculate_expected_overpayment(bid, state)
        landlord_response = predict_landlord_response(bid, state)
        
        strategies[strategy_name] = {
            'bid': bid,
            'win_probability': win_prob,
            'expected_overpayment': exp_overpay,
            'likely_landlord_response': landlord_response,
            'requires_negotiation': landlord_response['type'] != 'accept',
            'strategy_description': get_strategy_description(
                strategy_name, state, bid, win_prob, landlord_response
            ),
            'payoff_value': value
        }
    
    return strategies


def calculate_win_probability_with_landlord(bid, state):
    """
    Calculate win probability considering both competitor bids and landlord decisions
    """
    # First, probability of having highest bid
    competitor_dist = get_competitor_bid_distribution(state)
    prob_highest = sum(prob for comp_bid, prob in competitor_dist if bid >= comp_bid)
    
    # Then, probability landlord accepts given you have highest bid
    landlord_profile = LandlordProfile(
        state.days_on_market,
        classify_market_conditions(state.market_params),
        state.rental_situation.get('price_sens_landlord', 2)
    )
    
    bid_ratio = bid / state.listing_price
    if bid_ratio >= landlord_profile.acceptance_threshold:
        prob_accept = 0.95
    elif bid_ratio >= landlord_profile.acceptance_threshold - 0.05:
        prob_accept = 0.70
    elif bid_ratio >= landlord_profile.rejection_threshold:
        prob_accept = 0.40
    else:
        prob_accept = 0.10
    
    # Combined probability
    return prob_highest * prob_accept


def predict_landlord_response(bid, state):
    """
    Predict most likely landlord response to a bid
    """
    landlord_profile = LandlordProfile(
        state.days_on_market,
        classify_market_conditions(state.market_params),
        state.rental_situation.get('price_sens_landlord', 2)
    )
    
    bid_ratio = bid / state.listing_price
    
    if bid_ratio >= landlord_profile.acceptance_threshold:
        return {
            'type': 'accept',
            'probability': 0.9,
            'message': 'Likely immediate acceptance'
        }
    elif bid_ratio >= 1.0:  # At or above asking
        return {
            'type': 'request_best_final',
            'probability': 0.6,
            'message': 'May request best and final offers'
        }
    elif bid_ratio >= landlord_profile.rejection_threshold:
        return {
            'type': 'counter_offer', 
            'probability': 0.7,
            'message': f'Likely counter at ${state.listing_price:,.0f}'
        }
    else:
        return {
            'type': 'reject',
            'probability': 0.8,
            'message': 'Risk of rejection - bid may be too low'
        }


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


def get_strategy_description(strategy_name, state, bid, win_prob, landlord_response):
    """
    Generate enhanced strategy description including landlord response
    """
    market_condition = classify_market_conditions(state.market_params)
    bid_ratio = bid / state.listing_price
    
    # Base descriptions
    base_descriptions = {
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
    
    description = base_descriptions[strategy_name][market_condition]
    
    # Add landlord response info
    if landlord_response['type'] == 'accept':
        description += " Landlord likely to accept immediately."
    elif landlord_response['type'] == 'counter_offer':
        description += " Expect negotiation rounds."
    elif landlord_response['type'] == 'request_best_final':
        description += " May trigger bidding competition."
    
    return description
