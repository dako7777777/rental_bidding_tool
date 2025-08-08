"""Enhanced payoff calculations for three-player rental bidding"""

from models.market import classify_market_conditions


def evaluate(state):
    """
    Enhanced evaluation considering three-player dynamics
    
    Returns:
        float: Normalized payoff value between -1 and 1
    """
    # Terminal states after landlord decision
    if hasattr(state, 'landlord_final_decision') and state.landlord_final_decision:
        if state.landlord_final_decision == 'accept_tenant':
            # You won - calculate payoff
            fair_value = calculate_fair_market_value(
                state.listing_price,
                state.neighborhood_avg, 
                state.days_on_market,
                state.market_params
            )
            
            overpayment = state.user_bid - fair_value
            overpayment_ratio = overpayment / state.listing_price
            
            # Base payoff
            normalized_property_value = state.property_value / 5.0
            base_payoff = normalized_property_value - (overpayment_ratio * 2.0 * state.overpayment_weight)
            
            # Bonus for winning in competitive market
            competition_bonus = 0.1 * state.competitive_level / 3.0
            
            # Penalty for multiple rounds (time cost)
            round_penalty = state.negotiation_cost * (state.round - 1)
            
            # Risk adjustment
            risk_factor = (state.risk_tolerance - 3) / 10.0
            
            final_payoff = (base_payoff + competition_bonus - round_penalty) * (1 + risk_factor)
            
            return max(-1.0, min(1.0, final_payoff))
        
        elif state.landlord_final_decision == 'accept_competitor':
            # You lost to competitor
            opportunity_cost = -0.5 * (state.property_value / 5.0)
            
            # Small bonus if you forced competitor to pay more
            if hasattr(state, 'competitor_increase_forced') and state.competitor_increase_forced:
                opportunity_cost += 0.1
            
            return opportunity_cost
        
        elif state.landlord_final_decision == 'reject_all':
            # Everyone lost - minor penalty
            return -0.2
    
    # Non-terminal evaluation (for pruning decisions)
    return heuristic_evaluation(state)


def heuristic_evaluation(state):
    """
    Heuristic evaluation for non-terminal states
    Used for move ordering and pruning
    """
    if not state.user_bid:
        return 0  # No bid yet
        
    # Estimate probability of winning
    if state.highest_competitor_bid:
        if state.user_bid > state.highest_competitor_bid:
            win_prob = 0.7
        elif state.user_bid == state.highest_competitor_bid:
            win_prob = 0.5
        else:
            win_prob = 0.3
    else:
        # No competitor bid yet - estimate based on market
        from models.distributions import get_competitor_bid_distribution
        competitor_dist = get_competitor_bid_distribution(state)
        win_prob = sum(prob for comp_bid, prob in competitor_dist if state.user_bid > comp_bid)
    
    # Adjust for landlord's likely response
    bid_ratio = state.user_bid / state.listing_price
    from algorithm.landlord_model import LandlordProfile
    
    landlord_profile = LandlordProfile(
        state.days_on_market,
        classify_market_conditions(state.market_params),
        state.rental_situation.get('price_sens_landlord', 2)
    )
    
    if bid_ratio >= landlord_profile.acceptance_threshold:
        win_prob *= 1.2  # Likely immediate acceptance
    elif bid_ratio < landlord_profile.rejection_threshold:
        win_prob *= 0.3  # Likely rejection
    
    # Expected value calculation
    if win_prob > 0:
        fair_value = calculate_fair_market_value(
            state.listing_price,
            state.neighborhood_avg,
            state.days_on_market,
            state.market_params
        )
        overpayment = state.user_bid - fair_value
        overpayment_penalty = (overpayment / state.listing_price) * 2.0
        property_value = state.property_value / 5.0
        
        expected_value = win_prob * (property_value - overpayment_penalty)
    else:
        expected_value = -0.5 * (state.property_value / 5.0)
    
    return max(-1.0, min(1.0, expected_value))


def calculate_fair_market_value(listing_price, neighborhood_avg, days_on_market, market_params):
    """
    Calculate fair market value based on market data and property specifics
    
    Returns:
        float: Estimated fair market value
    """
    # Primary estimate from market data
    market_implied_value = market_params['parameters']['median'] * listing_price
    
    # Neighborhood adjustment factor
    neighborhood_factor = neighborhood_avg / listing_price
    
    # Classify market conditions
    market_condition = classify_market_conditions(market_params)
    
    # Weight market data vs neighborhood based on market conditions
    if market_condition in ['very_cool', 'cooling']:
        # In cooling markets, neighborhood average is more relevant
        base_value = 0.4 * market_implied_value + 0.6 * neighborhood_avg
    else:
        # In hot markets, recent market data is more relevant
        base_value = 0.7 * market_implied_value + 0.3 * neighborhood_avg
    
    # Apply days-on-market adjustment
    staleness_discount = get_staleness_discount(days_on_market, market_condition)
    
    return base_value * staleness_discount


def get_staleness_discount(days_on_market, market_condition):
    """
    Calculate discount factor based on how long property has been listed
    """
    discount_rates = {
        'very_cool': {7: 0.98, 14: 0.95, 30: 0.90, 'default': 0.85},
        'cooling': {7: 0.99, 14: 0.97, 30: 0.93, 'default': 0.88},
        'balanced': {7: 1.00, 14: 0.98, 30: 0.95, 'default': 0.92},
        'very_hot': {7: 1.00, 14: 0.99, 30: 0.97, 'default': 0.95}
    }
    
    rates = discount_rates[market_condition]
    
    # Sort only numeric thresholds, handle default separately
    numeric_thresholds = [(k, v) for k, v in rates.items() if isinstance(k, int)]
    numeric_thresholds.sort(key=lambda x: x[0])  # Sort by threshold value
    
    for threshold, discount in numeric_thresholds:
        if days_on_market <= threshold:
            return discount
    
    # If no threshold matched, return default
    return rates['default']
