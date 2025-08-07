"""Pre-analyzed market parameters for Vancouver rental markets"""

# Downtown Vancouver: Cooling market
DOWNTOWN_MARKET_DATA = {
    'distribution_type': 'log_normal',
    'parameters': {
        'median': 0.98,      # Median bid slightly below listing (reflects cooling market)
        'sigma': 0.06,       # Lower spread due to less competition
        'skew': 0.2,         # Minimal positive skew (fewer extreme overbids)
    }
}

# Burnaby: More pronounced cooling market
BURNABY_MARKET_DATA = {
    'distribution_type': 'log_normal',
    'parameters': {
        'median': 0.96,      # Lower median reflects steeper price declines
        'sigma': 0.07,       # Slightly higher spread due to varied neighborhood conditions
        'skew': 0.15,        # Lower skew (even fewer overbids)
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