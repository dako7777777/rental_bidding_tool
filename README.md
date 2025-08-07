# Rental Bidding Strategy Tool

An intelligent rental bidding advisor that uses the **Expectiminimax algorithm with alpha-beta pruning** to help users make optimal bidding decisions in competitive Vancouver rental markets.

## Features

- **Advanced Algorithm**: Expectiminimax with probabilistic pruning for efficient computation
- **Market-Specific Data**: Pre-analyzed parameters for Downtown Vancouver and Burnaby markets
- **Three Strategy Options**: Conservative, Balanced, and Aggressive recommendations
- **Two-Round Negotiation**: Support for initial and final bidding rounds
- **Risk-Adjusted Recommendations**: Personalized based on user's risk tolerance

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. Clone or download the project files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install numpy scipy
```

## Project Structure

```
rental_bidding_tool/
├── main.py                    # Main entry point
├── requirements.txt           # Dependencies
├── README.md                  # This file
├── algorithm/
│   ├── __init__.py
│   ├── expectiminimax.py     # Core algorithm
│   └── game_state.py         # Game state management
├── models/
│   ├── __init__.py
│   ├── distributions.py      # Competitor bid modeling
│   ├── payoff.py            # Payoff calculations
│   ├── market.py            # Market classification
│   └── mixture.py           # Mixture distribution
├── analysis/
│   ├── __init__.py
│   └── strategy.py          # Strategy generation
├── ui/
│   ├── __init__.py
│   ├── terminal_ui.py       # Terminal interface
│   ├── input_validator.py   # Input validation
│   └── output_formatter.py  # Output formatting
└── config/
    ├── __init__.py
    ├── constants.py         # Configuration constants
    └── market_data.py       # Market parameters
```

## Usage

Run the tool from the command line:

```bash
python main.py
```

### Step-by-Step Guide

1. **Select Market**: Choose between Downtown Vancouver or Burnaby

2. **Enter Preferences**:
   - Maximum monthly budget
   - How much you want the property (1-5 scale)
   - Risk tolerance (1=conservative, 5=aggressive)

3. **Property Information**:
   - Listed monthly rent
   - Neighborhood average for similar units
   - Days the property has been on market
   - Landlord price sensitivity (1=firm, 3=flexible)
   - Competition level (1=low, 3=high)

4. **Review Recommendations**: The tool provides three strategies:
   - **Conservative**: Lower bid, prioritizes value
   - **Balanced**: Optimal expected value (recommended)
   - **Aggressive**: Higher bid, maximizes win probability

5. **Optional Round 2**: Continue to final bidding round with updated parameters

## Example Session

```
============================================================
          RENTAL BIDDING STRATEGY TOOL
        Expectiminimax Algorithm Advisor
============================================================

Select your market:
1. Downtown Vancouver (Cooling market)
2. Burnaby (More pronounced cooling)
Enter choice (1-2): 1

========================================
ROUND 1: Initial Bidding
========================================

User Preferences:
1. Maximum monthly budget ($): 2500
2. How much do you want this property? (1-5): 4
3. Risk tolerance (1=conservative, 5=aggressive): 3

Property Information:
1. Listed monthly rent ($): 2200
2. Neighborhood average for similar units ($): 2100
3. Days on market: 7
4. Landlord price sensitivity (1=firm, 3=flexible): 2
5. Competition level (1=low, 3=high): 2

Validating inputs... ✓

MARKET ANALYSIS:
----------------------------------------
Market Condition: Cooling
Typical Winning Bid: 98% of listing price
Property Freshness: Fresh listing (high interest expected)

Analyzing optimal bidding strategy...
Market condition: Cooling

ROUND 1 RECOMMENDATIONS:
============================================================

1. CONSERVATIVE STRATEGY
   Recommended Bid: $2,090
   Win Probability: 42%
   Expected Savings: $66 below market
   Strategy: Bid at 95.0% of listing to leverage market conditions while showing interest.
   Algorithm Confidence: Medium

2. BALANCED STRATEGY [RECOMMENDED - Best Expected Value]
   Recommended Bid: $2,156
   Win Probability: 71%
   Expected Overpayment: $0 above market
   Strategy: Market-aligned bid at 98.0% of listing, balancing value and success rate.
   Algorithm Confidence: High

3. AGGRESSIVE STRATEGY
   Recommended Bid: $2,244
   Win Probability: 89%
   Expected Overpayment: $88 above market
   Strategy: Above-market bid at 102.0% of listing for 89% win probability.
   Algorithm Confidence: Medium
```

## Algorithm Details

The tool uses an **Expectiminimax algorithm** that:

1. **Models Competition**: Uses order statistics to model the highest competing bid
2. **Considers Market Conditions**: Adjusts strategies based on cooling/hot markets
3. **Applies Pruning**: Alpha-beta and probabilistic pruning for efficiency
4. **Risk Adjustment**: Personalizes recommendations based on user risk tolerance

## Market Data

The tool includes pre-analyzed market parameters for:

- **Downtown Vancouver**: Cooling market (median bid: 98% of listing)
- **Burnaby**: More pronounced cooling (median bid: 96% of listing)

## Notes

- Recommendations are algorithmic suggestions based on market models
- Always consider your personal circumstances and financial situation
- The tool assumes rational bidding behavior from competitors
- Market conditions can change; use current market knowledge

## Troubleshooting

If you encounter issues:

1. Ensure Python 3.7+ is installed: `python --version`
2. Verify dependencies are installed: `pip list | grep -E "numpy|scipy"`
3. Check all project files are in correct directories
4. Ensure input values are within valid ranges

## License

This tool is provided as-is for educational and personal use.

## Support

For questions or issues, please refer to the Technical Design Document V2.5