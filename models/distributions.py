"""Bid distribution models for competitor behavior"""

import numpy as np
import scipy.stats
from models.mixture import MixtureDistribution
from models.market import classify_market_conditions
from config.constants import NUM_BID_SAMPLES, PROBABILITY_THRESHOLD


def get_competitor_bid_distribution(state):
    """
    Generate probability distribution for highest competing bid
    accounting for the number of competitors
    
    Returns:
        list: [(bid_amount, probability), ...]
    """
    # Validate market parameters
    validate_market_parameters(state.market_params)
    
    # Extract parameters
    params = state.market_params['parameters']
    median = params['median'] * state.listing_price
    sigma = params['sigma']
    skew = params['skew']
    
    # Map competitive_level to number of competitors
    # Updated for more realistic cooling market competition
    num_competitors_map = {
        1: 1,      # Low competition: 1 other bidder
        2: 2,      # Medium: 2 bidders (reduced from 2.5)
        3: 3       # High: 3 bidders (reduced from 5)
    }
    comp_level = state.competitive_level
    
    # Get dynamic bid range based on market conditions
    bid_range = get_dynamic_bid_range(
        median, sigma, state.listing_price, 
        classify_market_conditions(state.market_params)
    )
    
    # Calculate probabilities - simplified, no fractional competitors
    num_competitors = num_competitors_map[comp_level]
    probabilities = calculate_order_statistics(
        bid_range, median, sigma, skew, num_competitors
    )
    
    # Normalize and return
    total = sum(probabilities)
    if total == 0:
        # Fallback to uniform if something goes wrong
        probabilities = [1.0 / len(bid_range)] * len(bid_range)
        total = 1.0
    
    return [(bid, prob/total) for bid, prob in zip(bid_range, probabilities)]


def calculate_order_statistics(bid_range, median, sigma, skew, num_competitors):
    """
    Calculate probability distribution for maximum of N competitor bids
    """
    probabilities = []
    
    # Use skewed log-normal distribution
    distribution = create_skewed_lognormal(median, sigma, skew)
    
    for i, bid in enumerate(bid_range):
        # CDF for single competitor
        single_bid_cdf = distribution.cdf(bid)
        
        # Order statistics: P(max of N bids <= x) = P(single bid <= x)^N
        max_bid_cdf = single_bid_cdf ** num_competitors
        
        # Convert CDF to discrete probability
        if i == 0:
            # First point: use difference from 0
            pdf = max_bid_cdf
        else:
            # Finite difference approximation
            prev_bid = bid_range[i-1]
            prev_cdf = distribution.cdf(prev_bid) ** num_competitors
            pdf = max_bid_cdf - prev_cdf
        
        probabilities.append(max(0, pdf))  # Ensure non-negative
    
    return probabilities


def create_skewed_lognormal(median, sigma, skew):
    """
    Create a skewed log-normal distribution using mixture model
    """
    if abs(skew) < 0.01:
        # Regular log-normal for negligible skew
        return scipy.stats.lognorm(s=sigma, scale=median)
    
    # For skewed distributions, use a mixture of two log-normals
    # This provides better control than sinh-arcsinh transformation
    if skew > 0:
        # Positive skew: mix with higher-variance component
        component1 = scipy.stats.lognorm(s=sigma, scale=median)
        component2 = scipy.stats.lognorm(s=sigma*1.5, scale=median*1.1)
        weight = 0.8 - 0.3 * min(skew, 1.0)
    else:
        # Negative skew: mix with lower-variance component
        component1 = scipy.stats.lognorm(s=sigma, scale=median)
        component2 = scipy.stats.lognorm(s=sigma*0.7, scale=median*0.95)
        weight = 0.8 + 0.3 * max(skew, -1.0)
    
    # Return mixture distribution
    return MixtureDistribution([component1, component2], [weight, 1-weight])


def get_dynamic_bid_range(median, sigma, listing_price, market_condition):
    """
    Generate bid range based on market conditions
    """
    range_params = {
        'very_cool': {'lower_mult': -1.5, 'upper_mult': 2.0},
        'cooling': {'lower_mult': -2.0, 'upper_mult': 2.5},
        'balanced': {'lower_mult': -1.0, 'upper_mult': 3.0},
        'very_hot': {'lower_mult': -0.5, 'upper_mult': 4.0}
    }
    
    params = range_params[market_condition]
    lower_bound = max(0.85 * listing_price, median + params['lower_mult'] * sigma * listing_price)
    upper_bound = min(1.30 * listing_price, median + params['upper_mult'] * sigma * listing_price)
    
    return np.linspace(lower_bound, upper_bound, num=NUM_BID_SAMPLES)


def validate_market_parameters(market_params):
    """
    Validate market parameters are within reasonable ranges
    """
    params = market_params['parameters']
    assert 0.5 <= params['median'] <= 1.5, "Median bid multiplier out of range"
    assert 0.01 <= params['sigma'] <= 0.5, "Sigma out of reasonable range"
    assert -1 <= params['skew'] <= 1, "Skew parameter out of range"
    assert market_params['distribution_type'] in ['log_normal', 'skewed_normal'] 