"""Enhanced expectiminimax algorithm with three player types including landlord"""

import numpy as np
from models.distributions import get_competitor_bid_distribution
from models.payoff import evaluate
from config.constants import PROBABILITY_THRESHOLD, BUDGET_FLEXIBILITY
from models.market import classify_market_conditions
from algorithm.landlord_model import LandlordProfile, get_landlord_actions, filter_landlord_actions

def expectiminimax_with_landlord(node, depth, alpha, beta, player_type):
    """
    Enhanced expectiminimax with three player types:
    - 'tenant_max': Tenant maximizing their utility
    - 'competitor_chance': Probability distribution of competitor bids  
    - 'landlord_min': Landlord minimizing tenant surplus
    
    Args:
        node: Current game state
        depth: Remaining depth to explore
        alpha: Best value for maximizer (tenant)
        beta: Best value for minimizer (landlord)
        player_type: Current player type
        
    Returns:
        tuple: (best_value, best_action)
    """
    if depth == 0 or is_terminal(node):
        return evaluate(node), None
    
    if player_type == 'tenant_max':
        max_eval = float('-inf')
        best_action = None
        
        # Get possible bids for current round
        possible_bids = get_possible_bids(node)
        
        # Sort bids by expected value heuristic for better pruning
        possible_bids = sorted(possible_bids, 
                             key=lambda b: bid_heuristic_value(b, node), 
                             reverse=True)
        
        for bid in possible_bids:
            if bid > node.max_budget * (1 + BUDGET_FLEXIBILITY):
                continue
                
            child = make_tenant_bid(node, bid)
            
            # Next player depends on round
            if node.round == 1:
                # After initial bid, competitors bid
                next_player = 'competitor_chance'
            else:  # Round 3
                # After final bid, landlord makes final decision
                child.all_final_bids_submitted = True
                next_player = 'landlord_min'
            
            eval_score, _ = expectiminimax_with_landlord(
                child, depth-1, alpha, beta, next_player
            )
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_action = bid
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break  # Beta cutoff
                
        return max_eval, best_action
    
    elif player_type == 'competitor_chance':
        expected_value = 0
        cumulative_prob = 0
        
        # Get competitor bid distribution
        bid_distribution = get_competitor_bid_distribution(node)
        
        # Sort by probability descending for better pruning
        bid_distribution = sorted(bid_distribution, 
                                key=lambda x: x[1], 
                                reverse=True)
        
        for competitor_bid, probability in bid_distribution:
            if probability < PROBABILITY_THRESHOLD:
                continue  # Prune low probability branches
            
            child = apply_competitor_bid(node, competitor_bid)
            
            # After all initial bids, landlord evaluates
            eval_score, _ = expectiminimax_with_landlord(
                child, depth-1, alpha, beta, 'landlord_min'
            )
            
            expected_value += probability * eval_score
            cumulative_prob += probability
            
            # Enhanced probabilistic pruning
            remaining_prob = 1 - cumulative_prob
            
            # Best possible outcome with remaining probability
            MAX_POSSIBLE_SCORE = 1.0
            optimistic_bound = expected_value + remaining_prob * MAX_POSSIBLE_SCORE
            if optimistic_bound < alpha:
                break  # Can't exceed alpha even in best case
            
            # Worst possible outcome with remaining probability  
            MIN_POSSIBLE_SCORE = -1.0
            pessimistic_bound = expected_value + remaining_prob * MIN_POSSIBLE_SCORE
            if pessimistic_bound > beta:
                break  # Will exceed beta even in worst case
                
        return expected_value, None
    
    else:  # landlord_min
        min_eval = float('inf')
        best_action = None
        
        # Get landlord's possible actions based on current bids
        landlord_actions = get_landlord_actions(node)
        
        # Sort actions by expected tenant surplus (ascending) for better pruning
        landlord_actions = sorted(landlord_actions,
                                key=lambda a: estimate_tenant_surplus(a, node))
        
        for action in landlord_actions:
            child = apply_landlord_decision(node, action)
            
            if action['type'] in ['accept_tenant', 'accept_competitor']:
                # Terminal decision
                eval_score = evaluate(child)
            
            elif action['type'] == 'reject_all':
                # Terminal - everyone loses
                eval_score = evaluate(child)
            
            elif action['type'] in ['request_best_final', 'counter_offer']:
                # Continues to round 3
                child.round = 3
                child.landlord_feedback = action['type']
                
                # Tenant responds to landlord's action
                eval_score, _ = expectiminimax_with_landlord(
                    child, depth-1, alpha, beta, 'tenant_max'
                )
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_action = action
            
            beta = min(beta, eval_score)
            if beta <= alpha:
                break  # Alpha cutoff
                
        return min_eval, best_action


def is_terminal(node):
    """Check if this is a terminal state"""
    return hasattr(node, 'landlord_final_decision') and node.landlord_final_decision is not None


def make_tenant_bid(node, bid):
    """Apply tenant bid to create new state"""
    new_state = node.copy()
    new_state.user_bid = bid
    return new_state


def apply_competitor_bid(state, competitor_bid):
    """Apply competitor bid to state"""
    new_state = state.copy()
    new_state.highest_competitor_bid = competitor_bid
    return new_state


def apply_landlord_decision(state, action):
    """Apply landlord's decision to state"""
    new_state = state.copy()
    
    if action['type'] == 'accept_tenant':
        new_state.landlord_final_decision = 'accept_tenant'
        new_state.won_property = True
    elif action['type'] == 'accept_competitor':
        new_state.landlord_final_decision = 'accept_competitor'
        new_state.won_property = False
    elif action['type'] == 'reject_all':
        new_state.landlord_final_decision = 'reject_all'
        new_state.won_property = False
    elif action['type'] == 'counter_offer':
        new_state.counter_price = action['counter_price']
    elif action['type'] == 'request_best_final':
        new_state.min_increase = action.get('min_increase', 0)
    
    return new_state


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
    
    # If round 3, adjust based on landlord feedback
    if state.round == 3:
        if state.landlord_feedback == 'counter_offer' and hasattr(state, 'counter_price'):
            # Can accept counter or walk away
            return [state.counter_price, state.user_bid]  # Accept or keep original
        elif state.landlord_feedback == 'request_best_final':
            # Need to increase bid
            current_bid = state.previous_bid if hasattr(state, 'previous_bid') and state.previous_bid else state.user_bid
            # If still no bid, use listing price as reference
            if current_bid is None:
                current_bid = state.listing_price * 0.98  # Default to reasonable bid
            min_bid = current_bid * 1.02  # At least 2% increase
            max_bid = min(current_bid * 1.10, flexible_budget)  # Up to 10% increase
            # Ensure we have reasonable bids
            if min_bid > max_bid:
                max_bid = min_bid * 1.05
            return np.linspace(min_bid, max_bid, num=10)
    
    # Get market median from parameters
    market_median_ratio = state.market_params['parameters']['median']
    market_median_bid = market_median_ratio * listing_price
    
    # Classify market conditions
    market_condition = classify_market_conditions(state.market_params)
    
    # Adjust bid range based on risk tolerance and market conditions
    if market_condition in ['cooling', 'very_cool']:
        # Cooling market: wider ranges to capture realistic win probabilities
        risk_levels = {
            1: {'center_offset': -0.08, 'range': 0.10},  # Very conservative: 84-94% of listing
            1.5: {'center_offset': -0.06, 'range': 0.12},  # Conservative: 86-98% of listing
            2: {'center_offset': -0.04, 'range': 0.14},  # Somewhat conservative: 88-102% of listing
            3: {'center_offset': -0.02, 'range': 0.16},  # Balanced: 90-106% of listing
            4: {'center_offset': 0.00, 'range': 0.18},   # Somewhat aggressive: 91-109% of listing
            4.5: {'center_offset': 0.02, 'range': 0.20},  # Aggressive: 92-112% of listing
            5: {'center_offset': 0.04, 'range': 0.22}    # Very aggressive: 93-115% of listing
        }
    else:
        # Hot/balanced market: higher bid ranges
        risk_levels = {
            1: {'center_offset': -0.04, 'range': 0.10},  # Very conservative: 88-98% of listing
            1.5: {'center_offset': -0.02, 'range': 0.12},  # Conservative: 90-102% of listing
            2: {'center_offset': 0.00, 'range': 0.14},   # Somewhat conservative: 93-107% of listing
            3: {'center_offset': 0.02, 'range': 0.16},   # Balanced: 94-110% of listing
            4: {'center_offset': 0.04, 'range': 0.18},   # Somewhat aggressive: 95-113% of listing
            4.5: {'center_offset': 0.06, 'range': 0.20},  # Aggressive: 96-116% of listing
            5: {'center_offset': 0.08, 'range': 0.22}    # Very aggressive: 97-119% of listing
        }
    
    risk_level = state.risk_tolerance  # Now can be float
    # Find closest risk level
    available_levels = sorted(risk_levels.keys())
    closest_level = min(available_levels, key=lambda x: abs(x - risk_level))
    risk_params = risk_levels[closest_level]
    
    # Center the bid range around market median, adjusted for risk
    center_ratio = market_median_ratio + risk_params['center_offset']
    range_width = risk_params['range']
    
    # Calculate bid range
    min_ratio = center_ratio - (range_width / 2)
    max_ratio = center_ratio + (range_width / 2)
    
    # Convert to actual dollar amounts
    min_bid = max(min_ratio * listing_price, 0.85 * listing_price)  # Never go below 85%
    max_bid = min(max_ratio * listing_price, flexible_budget)  # Respect flexible budget
    
    # Ensure min doesn't exceed max
    if min_bid >= max_bid:
        # Fallback: use a narrow range around the budget limit
        max_bid = min(flexible_budget, listing_price * 1.05)
        min_bid = max_bid * 0.95
    
    # Create bid points with more density around market median
    num_bids = 15
    if min_bid < max_bid:
        bids = np.linspace(min_bid, max_bid, num=num_bids)
    else:
        bids = [min_bid]
    
    return bids


def bid_heuristic_value(bid, state):
    """
    Heuristic for ordering bids to improve pruning
    Higher values = more promising bids to try first
    """
    # Estimate win probability
    competitor_dist = get_competitor_bid_distribution(state)
    win_prob = sum(prob for comp_bid, prob in competitor_dist if bid > comp_bid)
    
    # Estimate landlord acceptance probability
    bid_ratio = bid / state.listing_price
    landlord_profile = LandlordProfile(
        state.days_on_market,
        classify_market_conditions(state.market_params),
        state.rental_situation.get('price_sens_landlord', 2)  # Default moderate
    )
    
    if bid_ratio >= landlord_profile.acceptance_threshold:
        accept_prob = 0.9
    elif bid_ratio >= landlord_profile.acceptance_threshold - 0.05:
        accept_prob = 0.6
    else:
        accept_prob = 0.3
    
    # Overpayment penalty
    from models.payoff import calculate_fair_market_value
    fair_value = calculate_fair_market_value(
        state.listing_price,
        state.neighborhood_avg,
        state.days_on_market,
        state.market_params
    )
    overpayment_penalty = max(0, (bid - fair_value) / state.listing_price)
    
    # Combined heuristic
    return win_prob * accept_prob - overpayment_penalty * 0.5


def estimate_tenant_surplus(landlord_action, state):
    """
    Estimate tenant surplus for move ordering in landlord MIN node
    Lower surplus = better for landlord = try first
    """
    from models.payoff import calculate_fair_market_value
    
    if landlord_action['type'] == 'accept_tenant':
        # Tenant gets property at their bid price
        fair_value = calculate_fair_market_value(
            state.listing_price,
            state.neighborhood_avg,
            state.days_on_market,
            state.market_params
        )
        # Use user_bid if available, otherwise estimate
        tenant_bid = state.user_bid if state.user_bid is not None else fair_value
        return fair_value - tenant_bid  # Negative if overpaying
    
    elif landlord_action['type'] == 'accept_competitor':
        # Tenant loses
        return -0.5 * state.property_value
    
    elif landlord_action['type'] == 'reject_all':
        # Everyone loses
        return -0.2
    
    elif landlord_action['type'] == 'request_best_final':
        # Tenant will have to bid higher
        estimated_increase = state.listing_price * 0.03
        return -estimated_increase
    
    elif landlord_action['type'] == 'counter_offer':
        # Tenant will pay at least asking
        # Use user_bid if available, otherwise estimate based on market
        tenant_bid = state.user_bid if state.user_bid is not None else state.listing_price * 0.95
        return state.listing_price - tenant_bid
