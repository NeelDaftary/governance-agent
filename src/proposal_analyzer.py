import json
from typing import Dict, Any, Optional
from .claude_client import ClaudeClient
from .text_utils import prepare_proposal_text

class ProposalAnalyzer:
    def __init__(self):
        """Initialize the proposal analyzer with Claude API setup"""
        self.client = ClaudeClient.get_instance().client
        
        # Load the scoring system prompt
        self.base_prompt = """You are an expert DAO governance delegate that has been tasked with analyzing a proposal. Analyze this proposal and:
1. Provide a insightful summary addressing: main problem/opportunity, changes suggested
2. Explain the potential outcomes if the proposal passes or fails
3. Assign weights to 8 categories (total must equal 1.0)

Categories:
1. Protocol Parameters: Specific numerical adjustments to existing protocol variables (interest rates, transaction fees, voting thresholds, time locks) without changing core functionality.
2. Treasury Management: Explicit movement, allocation or utilization of protocol-owned funds for defined purposes including investments, grants, or operational expenses.
3. Tokenomics: Changes affecting token supply, distribution, inflation/deflation mechanisms, vesting schedules, or fundamental token utility/governance rights.
4. Protocol Upgrades: Implementation of new technical features, smart contract deployments, security improvements, or modifications to the underlying protocol logic.
5. Governance Process: Alterations to decision-making mechanisms, voting systems, proposal frameworks, or the roles/powers of governance participants.
6. Partnerships & Integrations: Formal collaborations with external protocols, projects, or entities that create technical connections or business relationships.
7. Risk Management: Measures specifically designed to address protocol vulnerabilities, market exposures, or operational threats through defined safeguards.
8. Community Initiatives: Programs directly targeting ecosystem participants through education, outreach, incentives, or support structures with clear community benefit.

Scoring Guidelines:
- Primary category identified should receive highest score (>0.35)
- Secondary aspects: 0.1-0.25
- Minor aspects: 0.0-0.1
- Total must equal 1.0

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
                category_weights = {
                    k: v for k, v in result.items() 
                    if k not in ['sum', 'primary_category', 'summary']
                }
                
                # Calculate total score
                total_score = sum(category_weights.values())
                
                # Normalize scores if total is not 1.0
                if abs(total_score - 1.0) > 0.0001:  # Allow for small floating point differences
                    print(f"Warning: Category scores sum to {total_score:.2f}, normalizing to 1.0")
                    for category in category_weights:
                        category_weights[category] = category_weights[category] / total_score
                    
                    # Update result with normalized scores
                    result.update(category_weights)
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