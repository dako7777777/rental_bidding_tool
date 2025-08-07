"""Input validation for terminal UI"""


class InputValidator:
    """Validates user inputs for the rental bidding tool"""
    
    def validate_budget(self, max_budget, listing_price):
        """
        Validate budget vs listing price
        
        Raises:
            ValueError: If budget is too low
        """
        if max_budget < listing_price * 0.85:
            raise ValueError(
                f"Budget ${max_budget} is too low for listing price ${listing_price}. "
                f"Minimum recommended budget is ${listing_price * 0.85:.0f}"
            )
        return True
    
    def validate_integer_range(self, value, min_val, max_val, field_name):
        """
        Validate integer is within range
        
        Raises:
            ValueError: If value is out of range
        """
        if not min_val <= value <= max_val:
            raise ValueError(
                f"{field_name} must be between {min_val} and {max_val}, got {value}"
            )
        return True
    
    def validate_positive_number(self, value, field_name):
        """
        Validate number is positive
        
        Raises:
            ValueError: If value is not positive
        """
        if value <= 0:
            raise ValueError(f"{field_name} must be positive, got {value}")
        return True
    
    def validate_rental_situation(self, rental_situation):
        """
        Validate all rental situation inputs
        """
        self.validate_positive_number(rental_situation['listing_price'], 'Listing price')
        self.validate_positive_number(rental_situation['neighborhood_avg'], 'Neighborhood average')
        self.validate_integer_range(rental_situation['days_on_market'], 0, 365, 'Days on market')
        self.validate_integer_range(rental_situation['price_sens_landlord'], 1, 3, 'Landlord price sensitivity')
        self.validate_integer_range(rental_situation['competitive_level'], 1, 3, 'Competition level')
        return True
    
    def validate_user_preferences(self, user_prefs):
        """
        Validate all user preference inputs
        """
        self.validate_positive_number(user_prefs['max_budget'], 'Maximum budget')
        self.validate_integer_range(user_prefs['property_value'], 1, 5, 'Property value')
        self.validate_integer_range(user_prefs['risk_tolerance'], 1, 5, 'Risk tolerance')
        return True 