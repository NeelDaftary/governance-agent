# Governance Agent

An AI-powered agent for analyzing DAO governance proposals across different forums. The agent uses Claude to evaluate proposals across multiple categories and provide structured analysis.

## Features

- Parses proposals from any Discourse-based governance forum
- Analyzes proposals across 8 key categories:
  - Protocol Parameters
  - Treasury Management
  - Tokenomics
  - Protocol Upgrades
  - Governance Process
  - Partnerships & Integrations
  - Risk Management
  - Community Initiatives
- Provides detailed scoring and analysis in JSON format
- Handles proposal comments and metadata
- Works with multiple forum platforms (currently supports Uniswap, Morpho)

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/governance-agent.git
cd governance-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file and add your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

Run the analysis script:
```bash
PYTHONPATH=. python src/analyze_proposal.py
```

This will analyze sample proposals from Uniswap and Morpho forums and save the results to JSON files.

## Project Structure

```
governance-agent/
├── src/
│   ├── discourse_parser.py    # Forum parsing functionality
│   ├── proposal_analyzer.py   # Proposal analysis using Claude
│   └── analyze_proposal.py    # Main script
├── requirements.txt           # Project dependencies
└── README.md                 # This file
```

## Output Format

The analysis output is saved in JSON format with the following structure:
```json
{
    "protocol_parameters": 0.00,
    "treasury_management": 0.60,
    "tokenomics": 0.00,
    "protocol_upgrades": 0.20,
    "governance_process": 0.00,
    "partnerships_integrations": 0.20,
    "risk_management": 0.00,
    "community_initiatives": 0.00,
    "sum": 1.00,
    "primary_category": "treasury_management",
    "summary": "Detailed analysis of the proposal..."
}
```

## License

MIT License 