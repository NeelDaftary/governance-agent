import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import anthropic
from datetime import datetime
from .claude_client import ClaudeClient
import json

class SentimentAnalyzer:
    def __init__(self, batch_size: int = 10):
        """Initialize the sentiment analyzer with Claude API setup"""
        load_dotenv()
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        self.client = ClaudeClient.get_instance().client
        self.batch_size = batch_size
        
    def analyze_comment_batch(self, comments: List[Dict[str, Any]], proposal_summary: str) -> Dict[str, Any]:
        """
        Analyze a batch of comments using Claude.
        
        Args:
            comments: List of comment dictionaries
            proposal_summary: Summary of the proposal for context
            
        Returns:
            dict: Analysis results for the batch
        """
        # Format comments for Claude
        formatted_comments = "\n\n".join([
            f"Comment {i+1}:\n{comment['content']}"
            for i, comment in enumerate(comments)
        ])
        
        prompt = f"""You are analyzing comments on a DAO governance proposal. Here is the proposal summary for context:

{proposal_summary}

Now, analyze the sentiment and key points of these comments:

{formatted_comments}

Please provide your analysis in the following JSON format:
{{
    "sentiment_score": <score between -1 and 1>,
    "summary": "<brief summary of the comments>",
    "key_points": ["<point 1>", "<point 2>", ...],
    "concerns": ["<concern 1>", "<concern 2>", ...],
    "suggestions": ["<suggestion 1>", "<suggestion 2>", ...]
}}

Make sure to:
1. Consider both positive and negative sentiment
2. Relate comments to the proposal context
3. Identify key points that support or oppose the proposal
4. Highlight specific concerns about the proposal
5. Note any constructive suggestions for improvement
6. Consider the overall sentiment in relation to the proposal's goals
"""

        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            response_text = message.content[0].text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                return json.loads(response_text[json_start:json_end])
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"Error analyzing comment batch: {str(e)}")
            return {
                'sentiment_score': 0.0,
                'summary': f"Error analyzing comments: {str(e)}",
                'key_points': [],
                'concerns': [],
                'suggestions': []
            }

    def analyze_all_comments(self, comments: List[Dict[str, Any]], proposal_summary: str) -> Dict[str, Any]:
        """
        Analyze all comments in batches and aggregate results.
        
        Args:
            comments: List of comment dictionaries
            proposal_summary: Summary of the proposal for context
            
        Returns:
            dict: Aggregated analysis results
        """
        if not comments:
            return {
                'sentiment_score': 0.0,
                'summary': "No comments to analyze",
                'key_points': [],
                'concerns': [],
                'suggestions': [],
                'num_comments': 0
            }
        
        # Process comments in batches
        batch_results = []
        for i in range(0, len(comments), self.batch_size):
            batch = comments[i:i + self.batch_size]
            result = self.analyze_comment_batch(batch, proposal_summary)
            batch_results.append(result)
        
        # Aggregate results
        if not batch_results:
            return {
                'sentiment_score': 0.0,
                'summary': "No valid analysis results",
                'key_points': [],
                'concerns': [],
                'suggestions': []
            }
        
        # Calculate average sentiment score
        sentiment_scores = [r.get('sentiment_score', 0.0) for r in batch_results]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Combine summaries
        combined_summary = " ".join([r.get('summary', '') for r in batch_results])
        
        # Combine all lists
        all_key_points = []
        all_concerns = []
        all_suggestions = []
        
        for result in batch_results:
            all_key_points.extend(result.get('key_points', []))
            all_concerns.extend(result.get('concerns', []))
            all_suggestions.extend(result.get('suggestions', []))
        
        # Remove duplicates while preserving order
        all_key_points = list(dict.fromkeys(all_key_points))
        all_concerns = list(dict.fromkeys(all_concerns))
        all_suggestions = list(dict.fromkeys(all_suggestions))
        
        return {
            'sentiment_score': avg_sentiment,
            'summary': combined_summary,
            'key_points': all_key_points,
            'concerns': all_concerns,
            'suggestions': all_suggestions,
            'num_comments': len(comments)
        } 