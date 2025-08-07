"""Pre-analyzed market parameters for Vancouver rental markets"""

# Downtown Vancouver: Cooling market
DOWNTOWN_MARKET_DATA = {
    'distribution_type': 'log_normal',
    'parameters': {
        'median': 0.94,      # Reduced from 0.98 - tenants expect discounts in cooling market
        'sigma': 0.05,       # Reduced spread - less variation in cooling market
        'skew': 0.1,         # Reduced skew - fewer people overbid in cooling market
    }
}

# Burnaby: More pronounced cooling market
BURNABY_MARKET_DATA = {
    'distribution_type': 'log_normal',
    'parameters': {
        'median': 0.92,      # Reduced from 0.96 - stronger cooling effect
        'sigma': 0.06,       # Slightly reduced spread
        'skew': 0.05,        # Minimal skew - almost no overbids in cooling market
    }
}

def load_market_data(market_choice):
    """Load market data for selected market"""
    if market_choice == 'downtown':
        return DOWNTOWN_MARKET_DATA
    elif market_choice == 'burnaby':
        return BURNABY_MARKET_DATA
    else:
        raise ValueError(f"Unknown market: {market_choice}") 