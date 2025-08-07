"""Core expectiminimax algorithm implementation with alpha-beta pruning"""

import numpy as np
from models.distributions import get_competitor_bid_distribution
from models.payoff import evaluate
from config.constants import PROBABILITY_THRESHOLD, BUDGET_FLEXIBILITY
from models.market import classify_market_conditions

def expectiminimax(node, depth, alpha, beta, maximizing_player):
    """
    Expectiminimax algorithm with alpha-beta pruning
    
    Args:
        node: Current game state
        depth: Remaining depth to explore
        alpha: Best value for maximizer
        beta: Best value for minimizer
        maximizing_player: True if current player is maximizer
    
    Returns:
        tuple: (best_value, best_action)
    """
    if depth == 0 or node.is_terminal():
        return evaluate(node), None
    
    if maximizing_player:
        max_eval = float('-inf')
        best_action = None
        
        # Get possible bids for the user
        possible_bids = get_possible_bids(node)
        
        for bid in possible_bids:
            # Make move
            child = node.make_move(bid)
            
            # Evaluate against competitor distribution (chance node)
            eval_score, _ = expectiminimax(child, depth-1, alpha, beta, False)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_action = bid
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff
        
        return max_eval, best_action
    
    else:  # Chance node (competitor bids)
        expected_value = 0
        bid_distribution = get_competitor_bid_distribution(node)
        cumulative_prob = 0
        
        for competitor_bid, probability in bid_distribution:
            if probability < PROBABILITY_THRESHOLD:
                continue  # Prune low probability branches
            
            # Apply competitor bid to determine win/loss
            child = apply_competitor_bid(node, competitor_bid)
            
            # For simple 2-player game against field, evaluate directly at terminal
            # This is appropriate since win/loss is determined here
            if depth <= 1 or child.won_property is not None:
                eval_score = evaluate(child)
            else:
                # Continue tree exploration if more depth available
                eval_score, _ = expectiminimax(child, depth-1, alpha, beta, True)
            
            expected_value += probability * eval_score
            cumulative_prob += probability
            
            # Probabilistic pruning
            remaining_prob = 1 - cumulative_prob
            max_possible_score = 1.0  # Maximum payoff
            min_possible_score = -1.0  # Minimum payoff
            
            if expected_value + remaining_prob * max_possible_score < alpha:
                break
            if expected_value + remaining_prob * min_possible_score > beta:
                break
        
        return expected_value, None


def get_possible_bids(state):
    """
    Generate possible bid amounts for the user, centered around market reality
    
    Returns:
        list: List of bid amounts to consider
    """
    listing_price = state.listing_price
    max_budget = state.max_budget
    
    # Allow budget flexibility for competitive bidding
    flexible_budget = max_budget * (1 + BUDGET_FLEXIBILITY)
    
    # Get market median from parameters
    market_median_ratio = state.market_params['parameters']['median']
    market_median_bid = market_median_ratio * listing_price
    
    # Classify market conditions
    market_condition = classify_market_conditions(state.market_params)
    
    # Adjust bid range based on risk tolerance
    # Risk tolerance 1-5 maps to different strategy levels
    risk_levels = {
        1: {'center_offset': -0.06, 'range': 0.08},  # Very conservative: 90-98% of listing
        2: {'center_offset': -0.04, 'range': 0.08},  # Conservative: 92-100% of listing
        3: {'center_offset': -0.02, 'range': 0.10},  # Balanced: 94-104% of listing
        4: {'center_offset': 0.00, 'range': 0.10},   # Aggressive: 96-106% of listing
        5: {'center_offset': 0.02, 'range': 0.12}    # Very aggressive: 98-110% of listing
    }
    
    risk_level = int(state.risk_tolerance)
    risk_params = risk_levels.get(risk_level, risk_levels[3])  # Default to balanced
    
    # Center the bid range around market median, adjusted for risk
    center_ratio = market_median_ratio + risk_params['center_offset']
    range_width = risk_params['range']
    
    # Calculate bid range
    min_ratio = center_ratio - (range_width / 2)
    max_ratio = center_ratio + (range_width / 2)
    
    # Convert to actual dollar amounts
    min_bid = max(min_ratio * listing_price, 0.85 * listing_price)  # Never go below 85%
    max_bid = min(max_ratio * listing_price, flexible_budget)  # Respect flexible budget
    
    # In cooling markets, extend the lower range for conservative strategies
    if market_condition in ['cooling', 'very_cool'] and risk_level <= 2:
        min_bid = max(0.88 * listing_price, min_bid - 0.02 * listing_price)
    
    # Ensure min doesn't exceed max
    if min_bid >= max_bid:
        # Fallback: use a narrow range around the budget limit
        max_bid = min(flexible_budget, listing_price * 1.05)
        min_bid = max_bid * 0.95
    
    # Create bid points with more density around market median
    num_bids = 15
    if min_bid < max_bid:
        # Create more points near the market median for better granularity
        bids = np.linspace(min_bid, max_bid, num=num_bids)
    else:
        bids = [min_bid]
    
    return bids


def apply_competitor_bid(state, competitor_bid):
    """
    Apply competitor bid to determine if user wins
    
    Returns:
        GameState: New state with win/loss determined
    """
    new_state = state.copy()
    
    # User wins if their bid is higher than the highest competitor bid
    if state.user_bid and state.user_bid > competitor_bid:
        new_state.won_property = True
    else:
        new_state.won_property = False
    
    return new_state 