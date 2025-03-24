import json
from typing import Dict, Any
from .claude_client import ClaudeClient
from .text_utils import prepare_proposal_text

class EvaluatorAgent:
    def __init__(self):
        """Initialize the evaluator agent with Claude API setup"""
        self.client = ClaudeClient.get_instance().client
        
        # Load the evaluation prompt
        self.base_prompt = """You are an expert at evaluating DAO governance proposals. Your task is to analyze the proposal and provide a detailed evaluation.

Evaluation Criteria:
1. Clarity and Completeness
   - Is the proposal well-written and clear?
   - Does it provide all necessary information?
   - Are the goals and objectives clearly stated?

2. Technical Feasibility
   - Is the proposed solution technically sound?
   - Are there any potential technical challenges?
   - Is the implementation plan realistic?

3. Impact and Benefits
   - What are the potential benefits?
   - Who are the stakeholders affected?
   - What are the expected outcomes?

4. Risks and Mitigation
   - What are the potential risks?
   - Are there adequate mitigation strategies?
   - What are the worst-case scenarios?

5. Resource Requirements
   - What resources are needed?
   - Are the resource estimates reasonable?
   - Is there a clear timeline?

6. Alignment with Protocol Goals
   - How well does it align with protocol objectives?
   - Does it support long-term growth?
   - Are there any conflicts with existing initiatives?

7. Community Impact
   - How will it affect the community?
   - Are there any concerns from stakeholders?
   - Is there community support?

8. Implementation Plan
   - Is there a clear implementation strategy?
   - Are the steps well-defined?
   - Is there a realistic timeline?

Proposal to evaluate:
"""

    def evaluate_proposal(self, proposal_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a proposal using Claude and return detailed analysis.
        
        Args:
            proposal_details: Dictionary containing proposal details
            
        Returns:
            dict: Evaluation results with scores and analysis
        """
        # Prepare the proposal text using shared utility
        proposal_text = prepare_proposal_text(proposal_details)
        
        # Create the full prompt
        full_prompt = f"{self.base_prompt}{proposal_text}\n\nPlease provide your evaluation in the following JSON format:\n{{\n    \"clarity_score\": <score between 0 and 1>,\n    \"technical_score\": <score between 0 and 1>,\n    \"impact_score\": <score between 0 and 1>,\n    \"risk_score\": <score between 0 and 1>,\n    \"resource_score\": <score between 0 and 1>,\n    \"alignment_score\": <score between 0 and 1>,\n    \"community_score\": <score between 0 and 1>,\n    \"implementation_score\": <score between 0 and 1>,\n    \"overall_score\": <average of all scores>,\n    \"strengths\": [\"<strength 1>\", \"<strength 2>\", ...],\n    \"weaknesses\": [\"<weakness 1>\", \"<weakness 2>\", ...],\n    \"recommendations\": [\"<recommendation 1>\", \"<recommendation 2>\", ...],\n    \"summary\": \"<brief summary of the evaluation>\"\n}}\n\nMake sure to:\n1. Provide balanced and objective analysis\n2. Support scores with specific observations\n3. Include actionable recommendations\n4. Consider both immediate and long-term impacts"
        
        try:
            # Get Claude's evaluation using the latest API
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
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
                return json.loads(response_text[json_start:json_end])
            else:
                raise ValueError("No valid JSON found in response")
            
        except Exception as e:
            print(f"Error evaluating proposal: {str(e)}")
            return {
                "clarity_score": 0.0,
                "technical_score": 0.0,
                "impact_score": 0.0,
                "risk_score": 0.0,
                "resource_score": 0.0,
                "alignment_score": 0.0,
                "community_score": 0.0,
                "implementation_score": 0.0,
                "overall_score": 0.0,
                "strengths": [],
                "weaknesses": [],
                "recommendations": [],
                "summary": f"Error evaluating proposal: {str(e)}"
            } 