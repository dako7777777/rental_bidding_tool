#!/usr/bin/env python3
# rental_bidding_tool/main.py
"""Main terminal interface and application loop"""

import sys
from typing import Dict, Optional

from config.market_data import MARKET_DATA
from algorithm.game_state import GameState
from analysis.strategy import generate_three_strategies
from analysis.market_classifier import classify_market_conditions
from ui.terminal_ui import (
    collect_user_preferences,
    collect_rental_situation,
    prompt_continue_negotiation,
    get_user_bid_choice,
    collect_negotiation_update,
    select_market
)
from ui.output_formatter import display_recommendations, display_market_analysis
from ui.input_validator import InputValidator
from config.constants import PROPERTY_VALUE_WEIGHT, OVERPAYMENT_WEIGHT


def load_market_data(market_name: str = None) -> tuple:
    """Load market data for selected market
    
    Returns:
        tuple: (market_data_dict, market_display_name)
    """
    if market_name is None:
        # Let user select market
        market_name = select_market(MARKET_DATA)
    
    if market_name not in MARKET_DATA:
        print(f"Warning: Market '{market_name}' not found. Using Downtown Vancouver.")
        market_name = 'downtown_vancouver'
    
    # Format display name
    display_name = market_name.replace('_', ' ').title()
    
    return MARKET_DATA[market_name], display_name


def create_game_state(user_prefs: Dict, rental_situation: Dict, 
                     market_data: Dict) -> GameState:
    """Create initial game state from inputs"""
    return GameState(
        # Property info
        listing_price=rental_situation['listing_price'],
        neighborhood_avg=rental_situation['neighborhood_avg'],
        days_on_market=rental_situation['days_on_market'],
        price_sens_landlord=rental_situation['price_sens_landlord'],
        competitive_level=rental_situation['competitive_level'],
        
        # User preferences
        max_budget=user_prefs['max_budget'],
        property_value=user_prefs['property_value'],
        risk_tolerance=user_prefs['risk_tolerance'],
        
        # Market parameters
        market_params=market_data,
        
        # Weights
        property_value_weight=PROPERTY_VALUE_WEIGHT,
        overpayment_weight=OVERPAYMENT_WEIGHT,
        
        # Initial state
        round=1
    )


def handle_round_2(game_state: GameState, recommendations: Dict) -> Optional[Dict]:
    """Handle round 2 negotiation logic"""
    print("\nROUND 2: Final Bidding")
    print("-" * 30)
    
    # Get user's round 1 choice
    round1_choice = get_user_bid_choice(recommendations)
    round1_choice['listing_price'] = game_state.listing_price
    
    # Collect negotiation update
    negotiation_update = collect_negotiation_update(round1_choice)
    
    # Update game state for round 2
    game_state.round = 2
    game_state.previous_bid = round1_choice['bid']
    game_state.landlord_feedback = negotiation_update['landlord_feedback']
    
    # Adjust competitive level based on feedback
    if negotiation_update['landlord_feedback'] == 'final':
        # Final round typically has fewer competitors
        game_state.competitive_level = max(1, game_state.competitive_level - 1)
    
    # Update days on market
    game_state.days_on_market += negotiation_update['additional_days_on_market']
    
    # Update listing price if changed
    if negotiation_update['renewed_listing_price'] and negotiation_update['renewed_listing_price'] > 0:
        game_state.listing_price = negotiation_update['renewed_listing_price']
    
    # Generate new recommendations
    return generate_three_strategies(game_state)


def main():
    """Main terminal interaction loop"""
    print("=" * 60)
    print(" " * 15 + "RENTAL BIDDING STRATEGY TOOL")
    print(" " * 10 + "Optimize Your Vancouver Rental Offers")
    print("=" * 60 + "\n")
    
    try:
        # Load market data
        print("Select your target market:")
        market_data, market_name = load_market_data()
        print(f"\n✓ Market selected: {market_name}")
        
        # Round 1: Initial Bidding
        print("\n" + "="*40)
        print("ROUND 1: Initial Bidding")
        print("="*40)
        
        # Collect user inputs with validation
        user_prefs = collect_user_preferences()
        rental_situation = collect_rental_situation()
        
        # Validate budget vs listing
        print("\nValidating inputs... ", end="")
        validator = InputValidator()
        validator.validate_budget(user_prefs['max_budget'], rental_situation['listing_price'])
        print("✓")
        
        # Create game state
        game_state = create_game_state(user_prefs, rental_situation, market_data)
        
        # Generate recommendations
        print("\nAnalyzing optimal bidding strategy...")
        market_condition = classify_market_conditions(market_data)
        print(f"Market condition: {market_condition.replace('_', ' ').title()}")
        
        # Show market analysis
        display_market_analysis(market_data, rental_situation)
        
        recommendations = generate_three_strategies(game_state)
        
        # Display recommendations
        display_recommendations(recommendations, round=1)
        
        # Optional Round 2
        if prompt_continue_negotiation():
            round2_outcome = handle_round_2(game_state, recommendations)
            if round2_outcome:
                display_recommendations(round2_outcome, round=2)
        
        print("\n" + "="*60)
        print("Good luck with your rental application!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nExiting... Good luck with your rental search!")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        print("Please try again with valid inputs.")
        sys.exit(1)


if __name__ == "__main__":
    main()


# ==============================================================================
# rental_bidding_tool/__init__.py
"""Rental Bidding Strategy Tool - Main Package"""

__version__ = "1.0.0"
__author__ = "Chen Zhuge, Deng Pan, Qi Wei"
__description__ = "Expectiminimax-based rental bidding strategy optimizer for Vancouver markets"


# ==============================================================================
# rental_bidding_tool/algorithm/__init__.py
"""Algorithm module for expectiminimax implementation"""

from .expectiminimax import expectiminimax
from .game_state import GameState, is_terminal, get_possible_bids

__all__ = ['expectiminimax', 'GameState', 'is_terminal', 'get_possible_bids']


# ==============================================================================
# rental_bidding_tool/models/__init__.py
"""Models for bid distributions and payoff calculations"""

from .distributions import (
    get_competitor_bid_distribution,
    create_skewed_lognormal,
    get_dynamic_bid_range
)
from .payoff import evaluate, calculate_fair_market_value

__all__ = [
    'get_competitor_bid_distribution',
    'create_skewed_lognormal', 
    'get_dynamic_bid_range',
    'evaluate',
    'calculate_fair_market_value'
]


# ==============================================================================
# rental_bidding_tool/analysis/__init__.py
"""Analysis module for market classification and strategy generation"""

from .market_classifier import classify_market_conditions
from .strategy import generate_three_strategies

__all__ = ['classify_market_conditions', 'generate_three_strategies']


# ==============================================================================
# rental_bidding_tool/ui/__init__.py
"""User interface module for terminal interaction"""

from .terminal_ui import (
    collect_user_preferences,
    collect_rental_situation,
    prompt_continue_negotiation
)
from .output_formatter import display_recommendations, display_market_analysis
from .input_validator import InputValidator

__all__ = [
    'collect_user_preferences',
    'collect_rental_situation',
    'prompt_continue_negotiation',
    'display_recommendations',
    'display_market_analysis',
    'InputValidator'
]


# ==============================================================================
# rental_bidding_tool/config/__init__.py
"""Configuration module for constants and market data"""

from .constants import (
    TREE_DEPTH,
    NUM_BID_SAMPLES,
    PROBABILITY_THRESHOLD,
    PROPERTY_VALUE_WEIGHT,
    OVERPAYMENT_WEIGHT,
    MAX_POSSIBLE_SCORE,
    MIN_POSSIBLE_SCORE
)
from .market_data import MARKET_DATA

__all__ = [
    'TREE_DEPTH',
    'NUM_BID_SAMPLES', 
    'PROBABILITY_THRESHOLD',
    'PROPERTY_VALUE_WEIGHT',
    'OVERPAYMENT_WEIGHT',
    'MAX_POSSIBLE_SCORE',
    'MIN_POSSIBLE_SCORE',
    'MARKET_DATA'
]


# ==============================================================================
# Updated rental_bidding_tool/ui/terminal_ui.py addition
# Add this function to the terminal_ui.py file:

def select_market(market_data: Dict) -> str:
    """Allow user to select a market from available options"""
    markets = list(market_data.keys())
    
    print("\nAvailable Markets:")
    for i, market in enumerate(markets, 1):
        display_name = market.replace('_', ' ').title()
        
        # Show market characteristics
        params = market_data[market]['parameters']
        if params['median'] < 0.98:
            condition = "(Buyer's Market)"
        elif params['median'] > 1.02:
            condition = "(Seller's Market)"
        else:
            condition = "(Balanced Market)"
            
        print(f"{i}. {display_name} {condition}")
    
    while True:
        try:
            choice = int(input(f"\nSelect market (1-{len(markets)}): "))
            if 1 <= choice <= len(markets):
                return markets[choice - 1]
            else:
                print(f"Please enter a number between 1 and {len(markets)}")
        except ValueError:
            print("Please enter a valid number")


# ==============================================================================
# requirements.txt
numpy>=1.21.0
scipy>=1.7.0


# ==============================================================================
# setup.py
"""Setup script for the Rental Bidding Strategy Tool"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rental-bidding-tool",
    version="1.0.0",
    author="Chen Zhuge, Deng Pan, Qi Wei",
    author_email="",
    description="Expectiminimax-based rental bidding strategy optimizer for Vancouver markets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/rental-bidding-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "rental-bidding=rental_bidding_tool.main:main",
        ],
    },
)


# ==============================================================================
# .gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
.pybuilder/
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# pytype static type analyzer
.pytype/

# Cython debug symbols
cython_debug/

# IDE settings
.vscode/
.idea/
*.swp
*.swo
*~

# OS files
.DS_Store
Thumbs.db

# Project specific
*.csv
*.xlsx
data/
output/
temp/


# ==============================================================================
# README.md
# Rental Bidding Strategy Tool

An algorithmic approach to optimize rental bidding strategies in competitive Vancouver housing markets using expectiminimax with alpha-beta pruning.

## 🎯 Overview

This tool helps tenants make optimal bidding decisions when competing for rental properties in Vancouver's challenging housing market. It uses advanced game theory algorithms to balance the risk of losing a property against potential overpayment.

### Key Features

- **Expectiminimax Algorithm**: Models uncertainty in competitor bids using probability distributions
- **Alpha-Beta Pruning**: Ensures computational efficiency even with complex decision trees
- **Market-Aware Strategies**: Adapts recommendations based on current market conditions
- **Three Strategy Options**: Conservative, Balanced, and Aggressive approaches
- **Two-Round Negotiation**: Supports initial bidding and counter-offer scenarios
- **Real Vancouver Data**: Pre-analyzed market parameters for major Vancouver neighborhoods

## 📋 Requirements

- Python 3.7 or higher
- numpy >= 1.21.0
- scipy >= 1.7.0

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rental-bidding-tool.git
cd rental-bidding-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the tool:
```bash
python main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

### Alternative: Install as Package

```bash
pip install -e .
rental-bidding
```

## 💡 How to Use

### Step 1: Select Your Market
Choose from available Vancouver markets:
- Downtown Vancouver
- Kitsilano
- Burnaby
- Richmond
- UBC Campus

### Step 2: Enter Your Preferences
- **Maximum Budget**: Your absolute maximum monthly rent
- **Property Value** (1-5): How much you want this specific property
- **Risk Tolerance** (1-5): Your willingness to bid aggressively

### Step 3: Input Property Details
- Listed monthly rent
- Neighborhood average for similar units
- Days on market
- Landlord flexibility (1=firm, 3=flexible)
- Competition level (1=low, 3=high)

### Step 4: Review Recommendations
The tool provides three strategies:

**Conservative Strategy**
- Lower bid with reduced win probability
- Minimizes overpayment risk
- Best for: Multiple property options available

**Balanced Strategy** ⭐ (Recommended)
- Optimizes expected value
- Balances win probability and fair pricing
- Best for: Most situations

**Aggressive Strategy**
- Higher bid with increased win probability
- Accepts overpayment for certainty
- Best for: Must-have properties

### Step 5: Optional Round 2
If the landlord counters or requests final offers, continue to Round 2 for updated recommendations.

## 📊 Example Output

```
ROUND 1 RECOMMENDATIONS:
============================================================

1. CONSERVATIVE STRATEGY
   Recommended Bid: $2,090
   Win Probability: 42%
   Expected Savings: $66 below market
   Strategy: Bid at 95.0% of listing to leverage market conditions.
   Algorithm Confidence: Medium

2. BALANCED STRATEGY [RECOMMENDED - Best Expected Value]
   Recommended Bid: $2,156
   Win Probability: 71%
   Expected Overpayment: $0 above market
   Strategy: Market-aligned bid at 98.0% of listing.
   Algorithm Confidence: High

3. AGGRESSIVE STRATEGY
   Recommended Bid: $2,244
   Win Probability: 89%
   Expected Overpayment: $88 above market
   Strategy: Above-market bid at 102.0% of listing.
   Algorithm Confidence: Medium
```

## 🔬 Technical Details

### Algorithm Components

1. **Expectiminimax with Alpha-Beta Pruning**
   - Models multi-player competition
   - Handles incomplete information
   - Efficient tree pruning for fast computation

2. **Order Statistics**
   - Models highest competing bid among N competitors
   - Uses skewed log-normal distributions
   - Accounts for market-specific bid patterns

3. **Market Classification**
   - Very Cool / Cooling / Balanced / Very Hot markets
   - Dynamic bid ranges based on conditions
   - Time-on-market adjustments

4. **Payoff Optimization**
   - Balances winning probability vs overpayment
   - Risk-adjusted recommendations
   - Fair market value estimation

## 📁 Project Structure

```
rental_bidding_tool/
├── main.py                 # Entry point
├── algorithm/             # Core expectiminimax implementation
├── models/               # Bid distributions and payoff functions
├── analysis/            # Market analysis and strategy generation
├── ui/                 # Terminal interface components
└── config/            # Constants and market data
```

## 👥 Authors

- Chen Zhuge (Lucas)
- Deng Pan (Dylan)
- Qi Wei (Dako)

*CS 5008 Final Project - University of British Columbia*

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ⚠️ Disclaimer

This tool provides algorithmic recommendations based on market analysis and game theory. Actual rental negotiations involve many factors beyond price. Users should consider this tool as one input among many in their decision-making process.

## 📞 Support

For questions or issues, please open an issue on GitHub or contact the authors.


# ==============================================================================
# LICENSE
MIT License

Copyright (c) 2024 Chen Zhuge, Deng Pan, Qi Wei

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.