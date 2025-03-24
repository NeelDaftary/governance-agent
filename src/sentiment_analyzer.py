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
        
    def analyze_comment_batch(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a batch of comments using Claude.
        
        Args:
            comments: List of comment dictionaries
            
        Returns:
            dict: Analysis results for the batch
        """
        # Format comments for Claude
        formatted_comments = "\n\n".join([
            f"Comment {i+1}:\n{comment['content']}"
            for i, comment in enumerate(comments)
        ])
        
        prompt = f"""Analyze the sentiment and key points of these comments on a DAO governance proposal.

Comments:
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
2. Identify key points and concerns
3. Note any suggestions for improvement
4. Provide a balanced summary
"""

        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract the response content
            response_text = message.content[0].text
            
            # Find the JSON block in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return {
                    'comments': comments,
                    'analysis': json.loads(response_text[json_start:json_end])
                }
            else:
                raise ValueError("No valid JSON found in response")
            
        except Exception as e:
            print(f"Error analyzing comment batch: {str(e)}")
            return {
                'comments': comments,
                'analysis': {
                    'sentiment_score': 0.0,
                    'summary': f"Error analyzing comments: {str(e)}",
                    'key_points': [],
                    'concerns': [],
                    'suggestions': []
                }
            }

    def analyze_all_comments(self, comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all comments in batches and aggregate results.
        
        Args:
            comments: List of comment dictionaries
            
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
            result = self.analyze_comment_batch(batch)
            batch_results.append(result)
        
        # Aggregate results
        total_sentiment = 0
        all_key_points = []
        all_concerns = []
        all_suggestions = []
        
        for result in batch_results:
            analysis = result['analysis']
            total_sentiment += analysis['sentiment_score']
            all_key_points.extend(analysis['key_points'])
            all_concerns.extend(analysis['concerns'])
            all_suggestions.extend(analysis['suggestions'])
        
        # Calculate average sentiment
        avg_sentiment = total_sentiment / len(batch_results)
        
        # Create final summary using Claude
        summary_prompt = f"""Create a concise summary of the community sentiment and key points from this proposal discussion.

Key Points:
{chr(10).join(f"- {point}" for point in all_key_points[:5])}

Concerns:
{chr(10).join(f"- {concern}" for concern in all_concerns[:5])}

Suggestions:
{chr(10).join(f"- {suggestion}" for suggestion in all_suggestions[:5])}

Overall Sentiment Score: {avg_sentiment:.2f}

Please provide a brief, balanced summary that captures the main sentiment and key takeaways."""

        try:
            message = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=500,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": summary_prompt
                    }
                ]
            )
            final_summary = message.content[0].text.strip()
        except Exception as e:
            final_summary = f"Error generating final summary: {str(e)}"
        
        return {
            'sentiment_score': avg_sentiment,
            'summary': final_summary,
            'key_points': all_key_points,
            'concerns': all_concerns,
            'suggestions': all_suggestions,
            'num_comments': len(comments)
        } 