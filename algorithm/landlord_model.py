"""Landlord modeling and decision logic"""

from models.market import classify_market_conditions


class LandlordProfile:
    """Enhanced landlord modeling"""
    
    def __init__(self, days_on_market, market_condition, price_sensitivity):
        self.days_on_market = days_on_market
        self.market_condition = market_condition
        self.price_sensitivity = price_sensitivity
        
        # Calculate behavioral parameters
        self.desperation_factor = self.calculate_desperation()
        self.acceptance_threshold = self.calculate_acceptance_threshold()
        self.rejection_threshold = self.calculate_rejection_threshold()
        self.negotiation_willingness = self.calculate_negotiation_willingness()
    
    def calculate_desperation(self):
        """Landlord becomes more desperate over time"""
        if self.days_on_market < 3:
            return 0.1
        elif self.days_on_market < 7:
            return 0.3
        elif self.days_on_market < 14:
            return 0.6
        elif self.days_on_market < 30:
            return 0.8
        else:
            return 0.95
    
    def calculate_acceptance_threshold(self):
        """Minimum bid ratio landlord will immediately accept"""
        base_threshold = {
            'very_hot': 1.05,
            'balanced': 1.00,
            'cooling': 0.98,
            'very_cool': 0.95
        }[self.market_condition]
        
        # Adjust for desperation and price sensitivity
        threshold = base_threshold * (1 - 0.1 * self.desperation_factor)
        threshold *= (1 - 0.05 * (self.price_sensitivity - 2))  # 1=firm, 3=flexible
        
        return max(0.90, threshold)  # Never accept below 90%
    
    def calculate_rejection_threshold(self):
        """Below this, landlord rejects all bids"""
        return self.acceptance_threshold - 0.10
    
    def calculate_negotiation_willingness(self):
        """Probability landlord will negotiate vs accept current best"""
        if self.market_condition == 'very_hot':
            base_willingness = 0.7  # More willing to push for higher
        else:
            base_willingness = 0.3
        
        # Less willing to negotiate if property has been listed long
        return base_willingness * (1 - 0.5 * self.desperation_factor)


def get_landlord_actions(state):
    """
    Generate possible landlord actions based on current bids
    
    Returns:
        list: Possible actions with their types and parameters
    """
    actions = []
    
    # Extract current bids
    tenant_bid = state.user_bid
    competitor_bid = state.highest_competitor_bid
    asking_price = state.listing_price
    
    # If no tenant bid yet, return empty actions (nothing for landlord to do)
    if tenant_bid is None:
        return []
    
    # Landlord profile based on market conditions
    landlord = LandlordProfile(
        days_on_market=state.days_on_market,
        market_condition=classify_market_conditions(state.market_params),
        price_sensitivity=state.rental_situation.get('price_sens_landlord', 2)  # Default moderate
    )
    
    # Always can accept highest bid if above threshold
    if competitor_bid is not None:
        highest_bid = max(tenant_bid, competitor_bid)
        if highest_bid >= asking_price * landlord.acceptance_threshold:
            if tenant_bid >= competitor_bid:
                actions.append({
                    'type': 'accept_tenant',
                    'bid': tenant_bid
                })
            else:
                actions.append({
                    'type': 'accept_competitor', 
                    'bid': competitor_bid
                })
    else:
        # No competitor bid (e.g., in final round)
        if tenant_bid >= asking_price * landlord.acceptance_threshold:
            actions.append({
                'type': 'accept_tenant',
                'bid': tenant_bid
            })
    
    # Can request best and final if bids are close
    if competitor_bid and tenant_bid:
        bid_spread = abs(tenant_bid - competitor_bid) / max(tenant_bid, competitor_bid)
        if bid_spread < 0.05 and not getattr(state, 'all_final_bids_submitted', False):
            actions.append({
                'type': 'request_best_final',
                'min_increase': asking_price * 0.02
            })
    
    # Calculate highest bid for counter/reject decisions
    if competitor_bid is not None:
        highest_bid = max(tenant_bid, competitor_bid)
    else:
        highest_bid = tenant_bid
    
    # Can counter if bids below asking but reasonable
    if highest_bid < asking_price and highest_bid > asking_price * 0.9:
        actions.append({
            'type': 'counter_offer',
            'counter_price': asking_price
        })
    
    # Can reject all if bids too low (but this is risky)
    if highest_bid < asking_price * landlord.rejection_threshold:
        actions.append({
            'type': 'reject_all'
        })
    
    # Filter actions based on landlord's risk profile
    return filter_landlord_actions(actions, landlord)


def filter_landlord_actions(actions, landlord):
    """Filter actions based on landlord's profile"""
    filtered = []
    
    for action in actions:
        # Desperate landlords avoid rejecting all
        if action['type'] == 'reject_all' and landlord.desperation_factor > 0.7:
            continue
        
        # Firm landlords (price_sensitivity=1) avoid immediate acceptance below asking
        if (action['type'] in ['accept_tenant', 'accept_competitor'] and 
            landlord.price_sensitivity == 1 and 
            action['bid'] < landlord.acceptance_threshold * 1.02):
            continue
        
        filtered.append(action)
    
    return filtered if filtered else actions  # Always return at least original actions
