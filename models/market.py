"""Market parameter handling and classification"""


def classify_market_conditions(market_params):
    """
    Classify market as very_cool, cooling, balanced, or very_hot
    """
    median = market_params['parameters']['median']
    sigma = market_params['parameters']['sigma']
    
    if median < 0.95 and sigma < 0.08:
        return 'very_cool'
    elif median < 1.0:
        return 'cooling'
    elif median > 1.05 and sigma > 0.10:
        return 'very_hot'
    else:
        return 'balanced' 