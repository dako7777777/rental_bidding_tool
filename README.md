# Rental Bidding Strategy Tool - Three-Player Game Version

An advanced game-theoretic tool that models rental bidding as a **strategic three-player game** between you (tenant), competitors, and the landlord. Unlike simple "highest-bid-wins" models, this tool explicitly models how landlords make decisions based on market conditions, time pressure, and bid levels.

## Key Innovation: Three-Player Game Theory

Traditional rental bidding tools assume landlords always accept the highest bid. In reality, landlords strategically choose between:
- **Accepting** the highest bid immediately
- **Countering** with a higher price
- **Requesting** best and final offers
- **Rejecting** all bids if too low

This tool models these landlord behaviors using game theory, providing more realistic and actionable recommendations.

## How It Works

### Game Structure
```
Round 1: You → Competitors → Landlord evaluates all bids
Round 2: Landlord responds (accept/counter/request final)
Round 3: Final bidding (if needed) → Landlord decides
```

### Core Algorithm: Enhanced Expectiminimax
- **MAX nodes**: Your bidding decisions (maximize utility)
- **CHANCE nodes**: Competitor bid distributions
- **MIN nodes**: Landlord decisions (minimize tenant surplus)
- Uses alpha-beta pruning and smart move ordering for efficiency

### Landlord Modeling
The landlord's behavior depends on:
- **Days on market** (desperation factor: 0.1 for new → 0.95 for 30+ days)
- **Market conditions** (hot/balanced/cool)
- **Price sensitivity** (firm/moderate/flexible)

## Installation

```bash
# Clone the repository
git clone [repository-url]
cd rental_bidding_tool

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the tool:
```bash
python main.py
```

### Example Interaction
```
RENTAL BIDDING STRATEGY TOOL
Three-Player Game Theory Advisor
(Tenant vs Competitors vs Landlord)
================================

Would you like to see an example scenario? (y/n): y

Select your market:
1. Downtown Vancouver (Cooling market)
2. Burnaby (More pronounced cooling)
Enter choice (1-2): 1

User Preferences:
1. Maximum monthly budget ($): 2500
2. How much do you want this property? (1-5): 4
3. Risk tolerance (1=conservative, 5=aggressive): 3

Property Information:
1. Listed monthly rent ($): 2200
2. Neighborhood average for similar units ($): 2156
3. Days on market: 7
4. Landlord price sensitivity (1=firm, 2=moderate, 3=flexible): 2
5. Competition level (1=low, 2=medium, 3=high): 2
```

### Sample Output
```
ROUND 1 RECOMMENDATIONS:
================================

1. CONSERVATIVE STRATEGY
   Recommended Bid: $2,090
   Win Probability: 42%
   Likely Landlord Response: Likely counter at $2,200
   ⚠️ May require additional negotiation rounds
   Expected Savings: $66 below market
   Strategy: Bid at 95.0% of listing to leverage market conditions
   Algorithm Confidence: Low

2. BALANCED STRATEGY [RECOMMENDED - Best Expected Value]
   Recommended Bid: $2,156
   Win Probability: 71%
   Likely Landlord Response: May request best and final offers
   Expected Overpayment: $0 (at fair market value)
   Strategy: Market-aligned bid at 98.0% of listing
   Algorithm Confidence: High

3. AGGRESSIVE STRATEGY
   Recommended Bid: $2,244
   Win Probability: 89%
   Likely Landlord Response: Likely immediate acceptance
   Expected Overpayment: $88 above market
   Strategy: Above-market bid at 102.0% of listing
   Algorithm Confidence: Medium
```

## Why BALANCED is Usually Recommended

The algorithm recommends BALANCED because:
1. **Optimal win probability** (71%) without overpaying
2. **Hits landlord's acceptance threshold** in the current market
3. **Avoids negotiation rounds** that favor competitors
4. **Best expected value** considering all outcomes

## Technical Details

### Project Structure
```
rental_bidding_tool/
├── algorithm/           # Core game theory algorithms
│   ├── expectiminimax_landlord.py  # Three-player expectiminimax
│   ├── landlord_model.py           # Landlord behavior modeling
│   └── game_state.py               # Enhanced game state
├── models/             # Domain models
│   ├── distributions.py    # Competitor bid modeling
│   ├── payoff.py          # Three-player payoff calculation
│   └── market.py          # Market classification
├── analysis/           # Strategy generation
├── config/            # Market data and constants
└── ui/                # Terminal interface
```

### Key Parameters
- **Tree depth**: 4-6 levels (configurable)
- **Pruning threshold**: 0.01 probability
- **Budget flexibility**: 5% above stated max
- **Negotiation penalty**: 5-10% per round

## Market Data

Includes real-world calibrated data for:
- Downtown Vancouver (cooling market, ~98% median winning bid)
- Burnaby (more pronounced cooling, ~96% median)

## Limitations

1. **Simplified competitor model**: Uses statistical distributions
2. **Landlord rationality**: Assumes economically rational behavior
3. **Information assumptions**: Assumes you know days-on-market and competition level
4. **Market specificity**: Calibrated for Vancouver rental market

## Future Enhancements

- [ ] Machine learning for landlord behavior prediction
- [ ] Multi-round negotiation strategies
- [ ] Integration with rental listing APIs
- [ ] Portfolio optimization for multiple properties
- [ ] Behavioral economics factors

## Contributing

Pull requests welcome! Areas for contribution:
- Additional market data
- Improved landlord modeling
- UI enhancements
- Performance optimizations

## License

MIT License - See LICENSE file for details

## Acknowledgments

Based on game theory principles from:
- Expectiminimax algorithm (Stuart Russell & Peter Norvig)
- Mechanism design theory
- Behavioral economics research on housing markets
