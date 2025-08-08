"""Enhanced terminal user interface for three-player rental bidding tool"""

from ui.input_validator import InputValidator
from ui.output_formatter import display_recommendations_with_landlord, display_market_analysis, display_detailed_explanation


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
            price_sens = int(input("4. Landlord price sensitivity (1=firm, 2=moderate, 3=flexible): "))
            validator.validate_integer_range(price_sens, 1, 3, "Landlord price sensitivity")
            rental_situation['price_sens_landlord'] = price_sens
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    # Competition level
    while True:
        try:
            comp_level = int(input("5. Competition level (1=low, 2=medium, 3=high): "))
            validator.validate_integer_range(comp_level, 1, 3, "Competition level")
            rental_situation['competitive_level'] = comp_level
            break
        except ValueError as e:
            print(f"Invalid input: {e}")
    
    return rental_situation


def prompt_continue_negotiation():
    """Ask if user wants to continue to round 3 after landlord feedback"""
    print("\nLandlord has responded to initial bids.")
    print("Possible responses:")
    print("1. Request for best and final offers")
    print("2. Counter-offer at asking price")
    print("3. Accept highest bid")
    
    while True:
        choice = input("\nDid landlord request final bids or counter? (y/n): ").lower()
        if choice == 'y':
            return True
        elif choice == 'n':
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")


def handle_round_3(game_state, market_data):
    """Handle round 3 final bidding after landlord feedback"""
    from analysis.strategy import generate_three_strategies
    
    print("\nROUND 3: Final Bidding")
    print("-" * 30)
    
    # Get landlord's response type
    print("\nWhat was the landlord's response?")
    print("1. Request for best and final offers")
    print("2. Counter-offer at specific price")
    
    while True:
        response = input("Enter choice (1-2): ")
        if response == "1":
            game_state.landlord_feedback = 'request_best_final'
            break
        elif response == "2":
            game_state.landlord_feedback = 'counter_offer'
            # Get counter price
            while True:
                try:
                    counter = float(input("Counter-offer amount: $"))
                    if counter <= 0:
                        print("Amount must be positive")
                        continue
                    game_state.counter_price = counter
                    break
                except ValueError:
                    print("Please enter a valid number")
            break
        else:
            print("Please enter 1 or 2")
    
    # Get user's round 1 bid
    while True:
        try:
            round1_bid = float(input("Your Round 1 bid amount: $"))
            if round1_bid <= 0:
                print("Bid must be positive")
                continue
            game_state.previous_bid = round1_bid
            game_state.user_bid = round1_bid  # Set for algorithm
            break
        except ValueError:
            print("Please enter a valid number")
    
    # Update game state for round 3
    game_state.round = 3
    
    # Generate new recommendations
    return generate_three_strategies(game_state)


def display_example_scenario():
    """Display an example scenario to help users understand the tool"""
    print("\nEXAMPLE SCENARIO:")
    print("-" * 40)
    print("Listing: $2,200/month, 7 days on market")
    print("Market: Cooling (typical win at 98% of asking)")
    print("Your budget: $2,500, property value: 4/5")
    print("\nThe tool would recommend:")
    print("CONSERVATIVE: $2,090 (42% win, may save $66)")
    print("BALANCED: $2,156 (71% win, at market value) ✓")
    print("AGGRESSIVE: $2,244 (89% win, overpay $88)")
    print("\nBALANCED wins because it hits the landlord's")
    print("acceptance threshold while avoiding overpayment.")
