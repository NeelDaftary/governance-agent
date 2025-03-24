import json
from typing import Dict, Any, Optional
from .claude_client import ClaudeClient
from .text_utils import prepare_proposal_text

class ProposalAnalyzer:
    def __init__(self):
        """Initialize the proposal analyzer with Claude API setup"""
        self.client = ClaudeClient.get_instance().client
        
        # Load the scoring system prompt
        self.base_prompt = """You are an expert at analyzing DAO governance proposals. Your task is to analyze the proposal and assign scores across 8 categories, ensuring the total equals 1.0.

Primary Purpose Analysis:
1. What is the main problem or opportunity this proposal addresses?
2. What is the core change or action being proposed?
3. What are the expected outcomes and who benefits?

Category Definitions and Examples:

1. Protocol Parameters (Primary Purpose: Adjusting core protocol settings)
   - Interest rates, fees, rewards rates
   - Risk parameters, collateral ratios
   - Example: "Adjusting lending rates for better capital efficiency"
   - Example: "Updating fee tiers for different pool types"
   - Example: "Modifying rewards distribution rates"

2. Treasury Management (Primary Purpose: Managing protocol funds and resources)
   - Liquidity incentives and mining programs
   - Grant allocations and funding
   - Example: "Launching $24M liquidity mining campaign"
   - Example: "Allocating funds for ecosystem growth"
   - Example: "Setting up treasury management framework"

3. Tokenomics (Primary Purpose: Changes to token economics or distribution)
   - Token emission rates, vesting schedules
   - Token utility changes
   - Example: "Adjusting token emission schedule"
   - Example: "Modifying token vesting terms"
   - Example: "Changing token utility or governance rights"

4. Protocol Upgrades (Primary Purpose: Technical improvements or new features)
   - Smart contract upgrades
   - New protocol features
   - Example: "Deploying new protocol version"
   - Example: "Adding new protocol functionality"
   - Example: "Implementing technical improvements"

5. Governance Process (Primary Purpose: Changes to governance mechanisms)
   - Voting power changes
   - Proposal requirements
   - Example: "Modifying governance thresholds"
   - Example: "Updating proposal requirements"
   - Example: "Changing voting power calculation"

6. Partnerships & Integrations (Primary Purpose: External collaborations)
   - Strategic partnerships
   - Protocol integrations
   - Example: "Forming strategic partnership"
   - Example: "Integrating with external protocol"
   - Example: "Launching cross-protocol initiative"

7. Risk Management (Primary Purpose: Managing protocol risks)
   - Security measures
   - Risk mitigation strategies
   - Example: "Implementing new security measures"
   - Example: "Adding risk management controls"
   - Example: "Updating emergency procedures"

8. Community Initiatives (Primary Purpose: Community engagement and growth)
   - Community programs
   - Educational initiatives
   - Example: "Launching community program"
   - Example: "Starting educational initiative"
   - Example: "Creating community incentives"

Scoring Guidelines:
1. The primary purpose should receive the highest score (0.4-0.6)
2. Secondary aspects should receive lower scores (0.1-0.3)
3. Minor or tangential aspects should receive minimal scores (0.0-0.1)
4. Total of all scores must equal 1.0

Important Notes:
- Focus on the primary purpose first, then secondary aspects
- Implementation details should not overshadow the main goal
- Consider both immediate and long-term impacts
- Look for clear indicators of the proposal's main objective
- Consider the proposal's title and introduction for primary purpose clues

Proposal to analyze:
"""

    def analyze_proposal(self, proposal_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a proposal using Claude and return the categorized scores.
        
        Args:
            proposal_details: Dictionary containing proposal details
            
        Returns:
            dict: Analysis results with scores and summary
        """
        # Prepare the proposal text using shared utility
        proposal_text = prepare_proposal_text(proposal_details)
        
        # Create the full prompt
        full_prompt = f"{self.base_prompt}{proposal_text}\n\nPlease provide the analysis in the following JSON format:\n{{\n    \"protocol_parameters\": <score>,\n    \"treasury_management\": <score>,\n    \"tokenomics\": <score>,\n    \"protocol_upgrades\": <score>,\n    \"governance_process\": <score>,\n    \"partnerships_integrations\": <score>,\n    \"risk_management\": <score>,\n    \"community_initiatives\": <score>,\n    \"sum\": <total of all scores>,\n    \"primary_category\": \"<category with highest score>\",\n    \"summary\": \"<brief summary of the proposal>\"\n}}\n\nMake sure all scores are between 0 and 1, and the sum equals exactly 1.0."
        
        try:
            # Get Claude's analysis using the latest API
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": full_prompt
                    }
                ]
            )
            
            # Extract the response content
            response_text = message.content[0].text
            
            # Find the JSON block in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                result = json.loads(response_text[json_start:json_end])
                
                # Extract category scores
                category_scores = {
                    k: v for k, v in result.items() 
                    if k not in ['sum', 'primary_category', 'summary']
                }
                
                # Calculate total score
                total_score = sum(category_scores.values())
                
                # Normalize scores if total is not 1.0
                if abs(total_score - 1.0) > 0.0001:  # Allow for small floating point differences
                    print(f"Warning: Category scores sum to {total_score:.2f}, normalizing to 1.0")
                    for category in category_scores:
                        category_scores[category] = category_scores[category] / total_score
                    
                    # Update result with normalized scores
                    result.update(category_scores)
                    result['sum'] = 1.0
                
                return result
            else:
                raise ValueError("No valid JSON found in response")
            
        except Exception as e:
            print(f"Error analyzing proposal: {str(e)}")
            return {
                "protocol_parameters": 0.00,
                "treasury_management": 0.00,
                "tokenomics": 0.00,
                "protocol_upgrades": 0.00,
                "governance_process": 0.00,
                "partnerships_integrations": 0.00,
                "risk_management": 0.00,
                "community_initiatives": 0.00,
                "sum": 0.00,
                "primary_category": "error",
                "summary": f"Error analyzing proposal: {str(e)}"
            } 