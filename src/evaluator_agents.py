import anthropic
from typing import Dict, Any
import os
from dotenv import load_dotenv

class EvaluatorAgent:
    def __init__(self):
        """Initialize the evaluator agent with Claude API setup"""
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Category-specific prompts
        self.prompts = {
            "protocol_parameters": {
                "system": """You are a protocol engineering analyst specializing in blockchain parameter optimization. Analyze this DAO governance proposal for protocol parameter changes, recognizing that proposals may not explicitly address all relevant aspects.""",
                "key_points": [
                    "Parameter Identification: Identify protocol parameters mentioned (explicit or implicit)",
                    "Change Assessment: For identified parameters",
                    "Parameter Relationships: Note interdependencies between parameters"
                ],
                "output_instructions": [
                    "Provide a score (0.00-1.00) reflecting how central protocol parameter changes are to this proposal",
                    "List of parameters being modified",
                    "Brief analysis of potential impacts",
                    "Information gaps: What additional parameter details would strengthen this proposal?"
                ]
            },
            "treasury_management": {
                "system": """You are a financial strategist specializing in DAO treasury management. Analyze this governance proposal for treasury implications, understanding that financial details may be partial or implicit.""",
                "key_points": [
                    "Resource Allocation: Quantify assets being allocated",
                    "Financial Strategy: Purpose categorization and risk profile",
                    "Accountability: Success metrics and reporting requirements"
                ],
                "output_instructions": [
                    "Provide a score (0.00-1.00) reflecting how central treasury management is to this proposal",
                    "Summary of financial allocations proposed",
                    "Risk/reward analysis based on available information",
                    "Information gaps: What additional treasury details would strengthen this proposal?"
                ]
            },
            "tokenomics": {
                "system": """You are a tokenomic architect specializing in incentive design. Analyze this DAO governance proposal for tokenomic implications, recognizing that token-related specifications may be incomplete.""",
                "key_points": [
                    "Token Mechanism Changes: Identify token-related mechanisms being modified",
                    "Supply Dynamics: Note changes to emission, burning, or locking mechanisms",
                    "Incentive Structure: Identify behavioral incentives created or modified"
                ],
                "output_instructions": [
                    "Provide a score (0.00-1.00) reflecting how central tokenomics is to this proposal",
                    "Summary of token-related changes",
                    "Brief analysis of potential economic impacts",
                    "Information gaps: What additional tokenomic details would strengthen this proposal?"
                ]
            },
            "protocol_upgrades": {
                "system": """You are a blockchain protocol architect specializing in technical implementation. Analyze this DAO governance proposal for technical upgrades, understanding that technical specifications may vary in detail.""",
                "key_points": [
                    "Technical Changes: Identify components being modified",
                    "Architecture Impact: Note changes to protocol architecture",
                    "Performance Implications: Potential efficiency impacts"
                ],
                "output_instructions": [
                    "Provide a score (0.00-1.00) reflecting how central protocol upgrades are to this proposal",
                    "Summary of technical changes proposed",
                    "Brief risk assessment",
                    "Information gaps: What additional technical details would strengthen this proposal?"
                ]
            },
            "governance_process": {
                "system": """You are a governance architect specializing in decentralized decision-making. Analyze this DAO proposal for governance process implications, recognizing that governance details may be implicit or partial.""",
                "key_points": [
                    "Governance Mechanisms: Identify governance procedures being modified",
                    "Decision Rights: Note changes to authority distribution",
                    "Participation Changes: Changes to participation incentives or accessibility"
                ],
                "output_instructions": [
                    "Provide a score (0.00-1.00) reflecting how central governance process changes are to this proposal",
                    "Summary of governance mechanisms being modified",
                    "Brief analysis of power distribution impacts",
                    "Information gaps: What additional governance details would strengthen this proposal?"
                ]
            },
            "partnerships_integrations": {
                "system": """You are an ecosystem strategist specializing in protocol interoperability. Analyze this DAO governance proposal for partnership implications, understanding that relationship details may be incomplete.""",
                "key_points": [
                    "Relationship Identification: Identify external entities involved",
                    "Technical Integration: API or data sharing specifications",
                    "Strategic Alignment: Alignment with DAO's objectives"
                ],
                "output_instructions": [
                    "Provide a score (0.00-1.00) reflecting how central partnerships are to this proposal",
                    "Summary of external relationships proposed",
                    "Brief analysis of strategic implications",
                    "Information gaps: What additional partnership details would strengthen this proposal?"
                ]
            },
            "risk_management": {
                "system": """You are a risk engineer specializing in blockchain security and resilience. Analyze this DAO governance proposal for risk management implications, recognizing that risk analysis may be partial.""",
                "key_points": [
                    "Risk Vectors: Identify risk categories addressed",
                    "Mitigation Mechanisms: Technical safeguards proposed",
                    "Resilience Improvements: Recovery capability enhancements"
                ],
                "output_instructions": [
                    "Provide a score (0.00-1.00) reflecting how central risk management is to this proposal",
                    "Summary of risk vectors being addressed",
                    "Brief analysis of mitigation effectiveness",
                    "Information gaps: What additional risk management details would strengthen this proposal?"
                ]
            },
            "community_initiatives": {
                "system": """You are a community architect specializing in ecosystem development. Analyze this DAO governance proposal for community implications, understanding that community initiatives may have varying levels of detail.""",
                "key_points": [
                    "Initiative Identification: Identify community-focused activities",
                    "User Journey: Onboarding/retention pathway improvements",
                    "Resource Allocation: Resources dedicated to community building"
                ],
                "output_instructions": [
                    "Provide a score (0.00-1.00) reflecting how central community initiatives are to this proposal",
                    "Summary of community activities proposed",
                    "Brief analysis of potential ecosystem impact",
                    "Information gaps: What additional community details would strengthen this proposal?"
                ]
            }
        }

    def evaluate_proposal(self, category: str, proposal_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a proposal using the appropriate category-specific evaluator.
        
        Args:
            category: The primary category of the proposal
            proposal_details: Dictionary containing proposal details
            
        Returns:
            dict: Evaluation results including score and analysis
        """
        if category not in self.prompts:
            raise ValueError(f"Unknown category: {category}")
            
        # Prepare the prompt
        prompt = self.prompts[category]
        
        # Format the proposal text
        proposal_text = f"""
Title: {proposal_details['title']}
Created at: {proposal_details['created_at']}

Content:
{proposal_details['content']}

Key Comments:
"""
        for comment in proposal_details.get('comments', [])[:3]:
            proposal_text += f"\n- {comment['content'][:500]}...\n"
            
        # Create the full prompt
        full_prompt = f"""{prompt['system']}

Key Analysis Points:
{chr(10).join(f"- {point}" for point in prompt['key_points'])}

Output Instructions:
{chr(10).join(f"- {instruction}" for instruction in prompt['output_instructions'])}

Please analyze the following proposal:

{proposal_text}"""
        
        try:
            # Get Claude's analysis
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
            
            # Parse the response to extract score and analysis
            # This is a simple implementation - you might want to make it more robust
            score = 0.0
            analysis = {
                "score": score,
                "analysis": response_text,
                "category": category
            }
            
            # Try to extract score from response
            import re
            score_match = re.search(r"score\s*\(?0?\.?\d+\)?\s*:", response_text, re.IGNORECASE)
            if score_match:
                try:
                    score = float(re.search(r"0?\.?\d+", score_match.group()).group())
                    analysis["score"] = score
                except:
                    pass
            
            return analysis
            
        except Exception as e:
            print(f"Error evaluating proposal: {str(e)}")
            return {
                "score": 0.0,
                "analysis": f"Error evaluating proposal: {str(e)}",
                "category": category
            } 