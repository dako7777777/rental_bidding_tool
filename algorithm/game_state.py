"""Game state management for rental bidding"""

import copy
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class GameState:
    """Represents the complete game state for rental bidding"""
    
    # User inputs
    user_preferences: Dict[str, Any]
    rental_situation: Dict[str, Any]
    market_params: Dict[str, Any]
    
    # Derived values
    property_value_weight: float
    overpayment_weight: float
    round: int = 1
    
    # Strategy modifiers (can be adjusted for different recommendations)
    risk_tolerance: float = field(default=None)
    
    # Decision variables
    user_bid: float = None
    won_property: bool = False
    
    # For round 2
    previous_bid: float = None
    
    def __post_init__(self):
        """Initialize risk tolerance from user preferences if not set"""
        if self.risk_tolerance is None:
            self.risk_tolerance = self.user_preferences['risk_tolerance']
    
    @property
    def listing_price(self):
        return self.rental_situation['listing_price']
    
    @property
    def neighborhood_avg(self):
        return self.rental_situation['neighborhood_avg']
    
    @property
    def days_on_market(self):
        return self.rental_situation['days_on_market']
    
    @property
    def competitive_level(self):
        return self.rental_situation['competitive_level']
    
    @property
    def property_value(self):
        return self.user_preferences['property_value']
    
    @property
    def max_budget(self):
        return self.user_preferences['max_budget']
    
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
        # Terminal if bid has been made and evaluated
        return self.user_bid is not None 