#!/usr/bin/env python3
"""
Enhanced Rental Bidding Strategy Tool with Three-Player Game
Main entry point for terminal-based rental bidding advisor
"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT, BUDGET_FLEXIBILITY
from models.market import classify_market_conditions
from ui.terminal_ui import (
    select_market,
    collect_user_preferences,
    collect_rental_situation,
    prompt_continue_negotiation,
    handle_round_3,
    display_example_scenario
)
from ui.input_validator import InputValidator
from ui.output_formatter import (
    display_recommendations_with_landlord, 
    display_market_analysis,
    display_detailed_explanation
)


def create_game_state(user_prefs, rental_situation, market_data):
    """Create initial game state from inputs"""
    return GameState(
        user_preferences=user_prefs,
        rental_situation=rental_situation,
        market_params=market_data,
        property_value_weight=PROPERTY_VALUE_WEIGHT,
        overpayment_weight=OVERPAYMENT_WEIGHT,
        round=1,
        risk_tolerance=user_prefs['risk_tolerance']
    )


def main():
    """Main terminal interaction loop"""
    print("=" * 60)
    print(" " * 10 + "RENTAL BIDDING STRATEGY TOOL")
    print(" " * 5 + "Three-Player Game Theory Advisor")
    print(" " * 8 + "(Tenant vs Competitors vs Landlord)")
    print("=" * 60)
    print()
    
    # Show example scenario
    show_example = input("Would you like to see an example scenario? (y/n): ").lower()
    if show_example == 'y':
        display_example_scenario()
        input("\nPress Enter to continue...")
    
    try:
        # Select market (Downtown Vancouver or Burnaby)
        market_choice = select_market()
        market_data = load_market_data(market_choice)
        
        # Round 1: Initial Bidding
        print("\n" + "=" * 40)
        print("ROUND 1: Initial Bidding")
        print("=" * 40)
        
        # Collect user inputs with validation
        user_prefs = collect_user_preferences()
        rental_situation = collect_rental_situation()
        
        # Validate budget vs listing
        validator = InputValidator()
        print("\nValidating inputs... ", end="")
        try:
            validator.validate_budget(user_prefs['max_budget'], rental_situation['listing_price'])
            validator.validate_user_preferences(user_prefs)
            validator.validate_rental_situation(rental_situation)
            print("✓")
            
            # Display budget flexibility
            flexible_budget = user_prefs['max_budget'] * (1 + BUDGET_FLEXIBILITY)
            if user_prefs['max_budget'] < rental_situation['listing_price']:
                print(f"\nNote: Your budget is below listing price.")
                print(f"      With {BUDGET_FLEXIBILITY:.0%} flexibility, you can bid up to ${flexible_budget:.0f}")
            else:
                print(f"\nNote: Algorithm may use up to ${flexible_budget:.0f} ({BUDGET_FLEXIBILITY:.0%} flexibility) if needed")
        except ValueError as e:
            print(f"\n✗ Validation Error: {e}")
            return
        
        # Create game state
        game_state = create_game_state(user_prefs, rental_situation, market_data)
        
        # Display market analysis
        display_market_analysis(market_data, rental_situation)
        
        # Generate recommendations
        print("\nAnalyzing optimal bidding strategy...")
        print("Modeling tenant-competitor-landlord interactions...")
        recommendations = generate_three_strategies(game_state)
        
        # Display recommendations with landlord predictions
        display_recommendations_with_landlord(recommendations, round=1)
        
        # Show detailed explanation if desired
        show_details = input("\nWould you like a detailed explanation? (y/n): ").lower()
        if show_details == 'y':
            display_detailed_explanation(recommendations, market_data, rental_situation)
        
        # Optional Round 3 (after landlord response)
        if prompt_continue_negotiation():
            round3_outcome = handle_round_3(game_state, market_data)
            if round3_outcome:
                display_recommendations_with_landlord(round3_outcome, round=3)
        
        print("\n" + "=" * 60)
        print("Good luck with your rental application!")
        print("Remember: These are algorithmic suggestions based on")
        print("game theory and market models. The landlord's actual")
        print("behavior may vary. Always consider your circumstances.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nExiting... Good luck with your rental search!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("Please check your inputs and try again.")


if __name__ == "__main__":
    main()
