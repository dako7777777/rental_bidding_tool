"""Enhanced game state management for three-player rental bidding"""

import copy
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class GameState:
    """Enhanced game state for three-player game"""
    
    # User inputs
    user_preferences: Dict[str, Any]
    rental_situation: Dict[str, Any]
    market_params: Dict[str, Any]
    
    # Game parameters
    round: int = 1  # 1 or 3 (no round 2 - that's landlord's turn)
    property_value_weight: float = 1.0
    overpayment_weight: float = 1.0
    
    # Current state
    user_bid: Optional[float] = None
    highest_competitor_bid: Optional[float] = None
    all_competitor_bids: List[float] = field(default_factory=list)
    
    # Landlord state
    landlord_feedback: Optional[str] = None  # 'request_best_final', 'counter_offer'
    landlord_final_decision: Optional[str] = None  # 'accept_tenant', 'accept_competitor', 'reject_all'
    counter_price: Optional[float] = None
    
    # Round 3 specific
    previous_bid: Optional[float] = None
    all_final_bids_submitted: bool = False
    competitor_increase_forced: bool = False
    min_increase: Optional[float] = None
    
    # Outcome tracking
    won_property: bool = False
    outcome_determined: bool = False
    
    # Strategy modifiers
    risk_tolerance: Optional[float] = field(default=None)
    negotiation_cost: float = 0.05  # Default penalty for multiple rounds
    
    def __post_init__(self):
        """Initialize risk tolerance from user preferences if not set"""
        if self.risk_tolerance is None:
            self.risk_tolerance = self.user_preferences['risk_tolerance']
    
    # Derived properties
    @property
    def max_budget(self):
        return self.user_preferences['max_budget']
    
    @property 
    def listing_price(self):
        return self.rental_situation['listing_price']
    
    @property
    def neighborhood_avg(self):
        return self.rental_situation['neighborhood_avg']
    
    @property
    def days_on_market(self):
        base_days = self.rental_situation['days_on_market']
        if self.round == 3:
            return base_days + 3  # Assume 3 days between rounds
        return base_days
    
    @property
    def competitive_level(self):
        return self.rental_situation['competitive_level']
    
    @property
    def property_value(self):
        return self.user_preferences['property_value']
    
    def copy(self):
        """Create a deep copy of the game state"""
        return copy.deepcopy(self)
    
    def make_move(self, bid):
        """Apply a bid to create new state"""
        new_state = self.copy()
        new_state.user_bid = bid
        return new_state
    
    def is_terminal(self):
        """Check if this is a terminal state"""
        # Terminal if landlord made final decision
        return self.landlord_final_decision is not None
