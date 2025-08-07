#!/usr/bin/env python3
"""
Rental Bidding Strategy Tool
Main entry point for terminal-based rental bidding advisor
"""

from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from config.market_data import load_market_data
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT
from models.market import classify_market_conditions
from ui.terminal_ui import (
    select_market,
    collect_user_preferences,
    collect_rental_situation,
    prompt_continue_negotiation,
    handle_round_2
)
from ui.input_validator import InputValidator
from ui.output_formatter import display_recommendations, display_market_analysis


def create_game_state(user_prefs, rental_situation, market_data):
    """Create initial game state from inputs"""
    return GameState(
        user_preferences=user_prefs,
        rental_situation=rental_situation,
        market_params=market_data,
        property_value_weight=PROPERTY_VALUE_WEIGHT,
        overpayment_weight=OVERPAYMENT_WEIGHT,
        round=1,
        risk_tolerance=user_prefs['risk_tolerance'],
        user_bid=None,
        won_property=False
    )


def main():
    """Main terminal interaction loop"""
    print("=" * 60)
    print(" " * 10 + "RENTAL BIDDING STRATEGY TOOL")
    print(" " * 8 + "Expectiminimax Algorithm Advisor")
    print("=" * 60)
    print()
    
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
        except ValueError as e:
            print(f"\n✗ Validation Error: {e}")
            return
        
        # Create game state
        game_state = create_game_state(user_prefs, rental_situation, market_data)
        
        # Display market analysis
        display_market_analysis(market_data, rental_situation)
        
        # Generate recommendations
        print("\nAnalyzing optimal bidding strategy...")
        print(f"Market condition: {classify_market_conditions(market_data).replace('_', ' ').title()}")
        recommendations = generate_three_strategies(game_state)
        
        # Display recommendations
        display_recommendations(recommendations, round=1)
        
        # Optional Round 2
        if prompt_continue_negotiation():
            round2_outcome = handle_round_2(game_state, market_data)
            if round2_outcome:
                display_recommendations(round2_outcome, round=2)
        
        print("\n" + "=" * 60)
        print("Good luck with your rental application!")
        print("Remember: These are algorithmic suggestions based on")
        print("market models. Always consider your personal circumstances.")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nExiting... Good luck with your rental search!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check your inputs and try again.")


if __name__ == "__main__":
    main() 