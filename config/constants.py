"""Configuration constants for the rental bidding tool"""

# Algorithm parameters
TREE_DEPTH = 4                  # Depth of expectiminimax tree
NUM_BID_SAMPLES = 20           # Number of bid points to sample
PROBABILITY_THRESHOLD = 0.01    # Minimum probability to consider

# Payoff weights
PROPERTY_VALUE_WEIGHT = 1.0    # Weight for property value in payoff
OVERPAYMENT_WEIGHT = 1.0       # Weight for overpayment penalty
