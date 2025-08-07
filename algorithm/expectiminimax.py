"""Core expectiminimax algorithm implementation with alpha-beta pruning"""

import numpy as np
from models.distributions import get_competitor_bid_distribution
from models.payoff import evaluate
from config.constants import PROBABILITY_THRESHOLD

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
            
            # Terminal evaluation (no more depth needed for simple payoff)
            eval_score = evaluate(child)
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
    Generate possible bid amounts for the user
    
    Returns:
        list: List of bid amounts to consider
    """
    listing_price = state.listing_price
    max_budget = state.max_budget
    
    # Generate bid range from 85% to min(130%, budget)
    min_bid = 0.85 * listing_price
    max_bid = min(1.30 * listing_price, max_budget)
    
    # Create a reasonable number of bid points
    num_bids = 15  # Fewer than competitor samples for efficiency
    bids = np.linspace(min_bid, max_bid, num=num_bids)
    
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