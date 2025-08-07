"""Payoff calculations for rental bidding decisions"""

from models.market import classify_market_conditions


def evaluate(state):
    """
    Evaluate the game state from user's perspective
    
    Returns:
        float: Normalized payoff value between -1 and 1
    """
    if not state.won_property:
        # Normalize losing penalty based on property value preference
        return -0.5 * (state.property_value / 5.0)
    
    # Calculate fair market value aligned with market data
    fair_market_value = calculate_fair_market_value(
        state.listing_price, 
        state.neighborhood_avg,
        state.days_on_market,
        state.market_params
    )
    
    # Calculate normalized overpayment
    overpayment = state.user_bid - fair_market_value
    overpayment_ratio = overpayment / state.listing_price
    
    # Normalize property value to 0-1 scale
    normalized_property_value = state.property_value / 5.0
    
    # Calculate base payoff (normalized to -1 to 1 range)
    base_payoff = normalized_property_value - (overpayment_ratio * 2.0)
    
    # Apply risk adjustment
    risk_factor = (state.risk_tolerance - 3) / 10.0  # -0.2 to +0.2
    risk_adjusted_payoff = base_payoff * (1 + risk_factor)
    
    # Ensure payoff stays within bounds
    return max(-1.0, min(1.0, risk_adjusted_payoff))


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