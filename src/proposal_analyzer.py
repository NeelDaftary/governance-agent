import json
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import anthropic

class ProposalAnalyzer:
    def __init__(self):
        """Initialize the proposal analyzer with Claude API setup"""
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Load the scoring system prompt
        self.base_prompt = """# DAO Proposal Analysis System

## Task
Analyze the provided DAO governance proposal and assign proportional scores across eight standard categories. The sum of all scores must equal exactly 1.0 (or 0 if the proposal doesn't fit any category).

## Categories
Assess the proposal against these eight standard categories:

1. **Protocol Parameters** - Modifications to core operational variables of the protocol
2. **Treasury Management** - Decisions regarding the DAO's financial resources
3. **Tokenomics** - Changes related to the DAO's token system
4. **Protocol Upgrades** - Technical improvements to the underlying system
5. **Governance Process** - Changes to how the DAO's governance functions
6. **Partnerships & Integrations** - Formal collaborations with external entities
7. **Risk Management** - Measures addressing security and stability
8. **Community Initiatives** - Programs focused on ecosystem growth

## Scoring Guidelines
- Each proposal receives scores across these eight categories.
- Scores must be proportional to the proposal's focus on each category.
- The sum of all scores must equal exactly 1.0.
- If a proposal has elements spanning multiple categories, divide the score proportionally.
- If a proposal doesn't fit any category, all scores should be 0.
- Use a precision of two decimal places (e.g., 0.25, not 0.253).

Please analyze the following proposal and provide scores in JSON format with a brief summary:

PROPOSAL TEXT:
"""

    def prepare_proposal_text(self, proposal_details: Dict[str, Any]) -> str:
        """
        Prepare the proposal text for analysis by combining relevant fields.
        
        Args:
            proposal_details: Dictionary containing proposal details
            
        Returns:
            str: Formatted proposal text
        """
        text_parts = [
            f"Title: {proposal_details['title']}",
            f"\nProposal Content:\n{proposal_details['content']}"
        ]
        
        # Add first few comments if they provide context
        if proposal_details.get('comments'):
            text_parts.append("\nKey Comments:")
            for comment in proposal_details['comments'][:3]:
                text_parts.append(f"\n- {comment['content'][:500]}...")
        
        return "\n".join(text_parts)

    def analyze_proposal(self, proposal_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a proposal using Claude and return the categorized scores.
        
        Args:
            proposal_details: Dictionary containing proposal details
            
        Returns:
            dict: Analysis results with scores and summary
        """
        # Prepare the proposal text
        proposal_text = self.prepare_proposal_text(proposal_details)
        
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
            else:
                raise ValueError("No valid JSON found in response")
            
            return result
            
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