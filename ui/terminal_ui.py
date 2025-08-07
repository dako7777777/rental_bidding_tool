"""Terminal user interface for rental bidding tool"""

from ui.input_validator import InputValidator
from ui.output_formatter import display_recommendations, display_market_analysis


def select_market():
    """Select between Downtown Vancouver and Burnaby"""
    print("Select your market:")
    print("1. Downtown Vancouver (Cooling market)")
    print("2. Burnaby (More pronounced cooling)")
    
    while True:
        choice = input("Enter choice (1-2): ")
        if choice == "1":
            return "downtown"
        elif choice == "2":
            return "burnaby"
        else:
            print("Please enter 1 or 2")


def collect_user_preferences():
    """Collect user preference inputs with validation"""
    print("\nUser Preferences:")
    
    validator = InputValidator()
    user_prefs = {}
    
    # Rent type (fixed for now)
    user_prefs['rent_type'] = '1b1b'
    
    # Maximum budget
    while True:
        try:
            max_budget = float(input("1. Maximum monthly budget ($): "))
            validator.validate_positive_number(max_budget, "Maximum budget")
            user_prefs['max_budget'] = max_budget
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    # Property value
    while True:
        try:
            property_value = int(input("2. How much do you want this property? (1-5): "))
            validator.validate_integer_range(property_value, 1, 5, "Property value")
            user_prefs['property_value'] = property_value
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    # Risk tolerance
    while True:
        try:
            risk_tolerance = int(input("3. Risk tolerance (1=conservative, 5=aggressive): "))
            validator.validate_integer_range(risk_tolerance, 1, 5, "Risk tolerance")
            user_prefs['risk_tolerance'] = risk_tolerance
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    return user_prefs


def collect_rental_situation():
    """Collect rental situation inputs with validation"""
    print("\nProperty Information:")
    
    validator = InputValidator()
    rental_situation = {}
    
    # Listing price
    while True:
        try:
            listing_price = float(input("1. Listed monthly rent ($): "))
            validator.validate_positive_number(listing_price, "Listing price")
            rental_situation['listing_price'] = listing_price
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    # Neighborhood average
    while True:
        try:
            neighborhood_avg = float(input("2. Neighborhood average for similar units ($): "))
            validator.validate_positive_number(neighborhood_avg, "Neighborhood average")
            rental_situation['neighborhood_avg'] = neighborhood_avg
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    # Days on market
    while True:
        try:
            days_on_market = int(input("3. Days on market: "))
            validator.validate_integer_range(days_on_market, 0, 365, "Days on market")
            rental_situation['days_on_market'] = days_on_market
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    # Landlord price sensitivity
    while True:
        try:
            price_sens = int(input("4. Landlord price sensitivity (1=firm, 3=flexible): "))
            validator.validate_integer_range(price_sens, 1, 3, "Landlord price sensitivity")
            rental_situation['price_sens_landlord'] = price_sens
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    # Competition level
    while True:
        try:
            comp_level = int(input("5. Competition level (1=low, 3=high): "))
            validator.validate_integer_range(comp_level, 1, 3, "Competition level")
            rental_situation['competitive_level'] = comp_level
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    return rental_situation


def prompt_continue_negotiation():
    """Ask if user wants to continue to round 2"""
    while True:
        choice = input("\nContinue to Round 2 negotiation? (y/n): ").lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")


def handle_round_2(game_state, market_data):
    """Handle round 2 negotiation logic"""
    from analysis.strategy import generate_three_strategies
    
    print("\nROUND 2: Final Bidding")
    print("-" * 30)
    
    # Get user's round 1 bid directly
    while True:
        try:
            round1_bid = float(input("Your Round 1 bid amount: $"))
            if round1_bid <= 0:
                print("Bid must be positive")
                continue
            break
        except ValueError:
            print("Please enter a valid number")
    
    # Get days since round 1
    while True:
        try:
            days_since = int(input("Days since Round 1: "))
            if days_since < 0:
                print("Days must be non-negative")
                continue
            break
        except ValueError:
            print("Please enter a valid integer")
    
    print("\nAssuming: Final round with fewer competitors")
    
    # Update game state for round 2
    game_state.round = 2
    game_state.previous_bid = round1_bid
    game_state.rental_situation['competitive_level'] = max(1, game_state.competitive_level - 1)
    game_state.rental_situation['days_on_market'] += days_since
    
    # Generate new recommendations
    return generate_three_strategies(game_state) 