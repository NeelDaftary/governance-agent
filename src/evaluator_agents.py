import anthropic
from typing import Dict, Any
import os
from dotenv import load_dotenv
import json

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
                "system": "You are a protocol engineering analyst specializing in blockchain parameter optimization with expertise in evaluating technical and economic impacts of parameter changes.",
                "key_points": [
                    "Identify exact parameters being modified with current and proposed values",
                    "Assess direct impacts on protocol operations, incentives, and security",
                    "Analyze parameter interdependencies and potential second-order effects"
                ],
                "output_instructions": [
                    "Provide a technical feasibility score (0.00-1.00) with explicit reasoning",
                    "List all parameters modified with before/after values when available",
                    "Analyze short and long-term operational impacts with specific scenarios",
                    "Identify critical information gaps that prevent complete assessment"
                ]
            },
            "treasury_management": {
                "system": "You are a financial strategist specializing in DAO treasury management with expertise in crypto-native asset allocation and financial sustainability.",
                "key_points": [
                    "Quantify precise assets allocated (amounts, percentages, timeframes)",
                    "Evaluate alignment with treasury diversification principles",
                    "Assess specific measurable success metrics and accountability mechanisms"
                ],
                "output_instructions": [
                    "Provide a financial prudence score (0.00-1.00) with explicit reasoning",
                    "Summarize exact allocations with amounts, durations, and expected returns",
                    "Analyze specific risk/reward tradeoffs with quantitative estimates",
                    "Identify critical information gaps that prevent complete assessment"
                ]
            },
            "tokenomics": {
                "system": "You are a tokenomic architect specializing in crypto-economic incentive design with expertise in supply/demand dynamics and value accrual mechanisms.",
                "key_points": [
                    "Identify specific token mechanism changes with technical implementation details",
                    "Analyze impacts on token supply, velocity, and distribution curves",
                    "Evaluate alignment of incentive structures with protocol objectives"
                ],
                "output_instructions": [
                    "Provide an economic alignment score (0.00-1.00) with explicit reasoning",
                    "Summarize token mechanism changes with quantitative projections",
                    "Analyze market impacts across different stakeholder groups",
                    "Identify critical information gaps that prevent complete assessment"
                ]
            },
            "protocol_upgrades": {
                "system": "You are a blockchain protocol architect specializing in technical implementation with expertise in smart contract security and system design.",
                "key_points": [
                    "Identify specific technical changes with implementation methods",
                    "Assess architectural impacts on security, composability, and maintenance",
                    "Evaluate performance implications with projected metrics"
                ],
                "output_instructions": [
                    "Provide a technical robustness score (0.00-1.00) with explicit reasoning",
                    "Summarize technical changes with specific code/architecture impacts",
                    "Assess implementation risks with migration considerations",
                    "Identify critical information gaps that prevent complete assessment"
                ]
            },
            "governance_process": {
                "system": "You are a governance architect specializing in decentralized decision-making with expertise in voting mechanisms and power distribution.",
                "key_points": [
                    "Identify specific governance mechanisms being modified",
                    "Analyze changes to authority distribution and delegation structures",
                    "Evaluate impacts on participation rates and decision quality"
                ],
                "output_instructions": [
                    "Provide a governance effectiveness score (0.00-1.00) with explicit reasoning",
                    "Summarize governance changes with before/after comparisons",
                    "Analyze power distribution impacts across stakeholder groups",
                    "Identify critical information gaps that prevent complete assessment"
                ]
            },
            "partnerships_integrations": {
                "system": "You are an ecosystem strategist specializing in protocol interoperability with expertise in cross-chain integration and strategic alliances.",
                "key_points": [
                    "Identify specific external entities with their relevant capabilities",
                    "Evaluate technical integration requirements and implementation paths",
                    "Assess strategic alignment with protocol growth objectives"
                ],
                "output_instructions": [
                    "Provide a strategic value score (0.00-1.00) with explicit reasoning",
                    "Summarize partnership terms and integration specifications",
                    "Analyze specific value creation pathways for the protocol",
                    "Identify critical information gaps that prevent complete assessment"
                ]
            },
            "risk_management": {
                "system": "You are a risk engineer specializing in blockchain security and resilience with expertise in threat modeling and mitigation design.",
                "key_points": [
                    "Identify specific risk vectors with severity and likelihood estimates",
                    "Evaluate proposed mitigation mechanisms with implementation details",
                    "Assess overall resilience improvements against defined threats"
                ],
                "output_instructions": [
                    "Provide a risk reduction score (0.00-1.00) with explicit reasoning",
                    "Summarize risk vectors with quantified impact scenarios",
                    "Analyze mitigation effectiveness with residual risk assessment",
                    "Identify critical information gaps that prevent complete assessment"
                ]
            },
            "community_initiatives": {
                "system": "You are a community strategist specializing in DAO engagement and growth with expertise in incentive design and ecosystem development.",
                "key_points": [
                    "Identify specific engagement methods with target audiences",
                    "Evaluate resource allocation efficiency for community development",
                    "Assess inclusivity measures and onboarding friction reduction"
                ],
                "output_instructions": [
                    "Provide a community impact score (0.00-1.00) with explicit reasoning",
                    "Summarize initiative structures with participation mechanics",
                    "Analyze engagement potential with measurable success metrics",
                    "Identify critical information gaps that prevent complete assessment"
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
            dict: Evaluation results including score, analysis, and structured findings
        """
        if category not in self.prompts:
            raise ValueError(f"Unknown category: {category}")
            
        # Get the category-specific prompt
        prompt = self.prompts[category]
        
        # Format the proposal text
        proposal_text = f"""
Title: {proposal_details['title']}

Content:
{proposal_details['content']}"""
            
        # Create the full prompt with structured output format
        full_prompt = f"""{prompt['system']}

Key Analysis Points:
{chr(10).join(f"- {point}" for point in prompt['key_points'])}

Output Instructions:
{chr(10).join(f"- {instruction}" for instruction in prompt['output_instructions'])}

Please analyze the following proposal:

{proposal_text}

Provide your analysis in the following JSON format:
{{
    "score": <float between 0.00 and 1.00>,
    "reasoning": "<detailed explanation of the score>",
    "key_findings": [
        {{
            "aspect": "<specific aspect analyzed>",
            "analysis": "<detailed analysis of this aspect>",
            "impact": "<impact assessment>"
        }}
    ],
    "information_gaps": [
        "<list of critical information gaps>"
    ],
    "recommendations": [
        "<list of specific recommendations>"
    ]
}}"""
        
        try:
            # Get Claude's analysis
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0.1,
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
                
                # Add category information to the result
                result['category'] = category
                
                return result
            else:
                raise ValueError("No valid JSON found in response")
            
        except Exception as e:
            print(f"Error evaluating proposal: {str(e)}")
            return {
                "score": 0.0,
                "reasoning": f"Error evaluating proposal: {str(e)}",
                "key_findings": [],
                "information_gaps": [],
                "recommendations": []
            } 