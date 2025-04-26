import os
from dotenv import load_dotenv
from src.discourse_parser import DiscourseParser
from src.evaluator_agents import EvaluatorAgent
from src.proposal_analyzer import ProposalAnalyzer
from src.sentiment_analyzer import SentimentAnalyzer
import json
from datetime import datetime
from typing import Dict, Any, Optional

def analyze_proposal(url: str, analyze_sentiment: bool = False) -> dict:
    """
    Analyze a governance proposal using specialized evaluator agents.
    
    Args:
        url: The URL of the proposal to analyze
        analyze_sentiment: Whether to perform sentiment analysis on comments
        
    Returns:
        dict: Analysis results including category scores and detailed evaluations
    """
    # Initialize components
    parser = DiscourseParser()
    analyzer = ProposalAnalyzer()
    evaluator = EvaluatorAgent()
    
    # Step 1: Parse and store proposal data
    proposal_data = parser.parse_proposal(url)
    
    # Step 2: Analyze proposal content and determine category
    analysis_results = analyzer.analyze_proposal({
        'title': proposal_data['title'],
        'content': proposal_data['content']
    })
    
    # Extract category scores and get primary category
    category_weights = {
        k: v for k, v in analysis_results.items() 
        if k not in ['sum', 'primary_category', 'summary']
    }
    primary_category = analysis_results.get('primary_category')
    
    # Get detailed evaluation from specialized agent
    detailed_evaluation = evaluator.evaluate_proposal(primary_category, proposal_data)
    
    # Step 3: Analyze comments if requested
    comment_analysis = None
    if analyze_sentiment and proposal_data.get('comments'):
        sentiment_analyzer = SentimentAnalyzer()
        comment_analysis = sentiment_analyzer.analyze_all_comments(
            proposal_data['comments'],
            analysis_results['summary']
        )
    
    # Combine results
    results = {
        "proposal": {
            "url": url,
            "title": proposal_data['title'],
            "created_at": proposal_data['created_at']
        },
        "analysis": {
            "category_weights": category_weights,
            "primary_category": primary_category,
            "summary": analysis_results.get('summary', ''),
            "detailed_evaluation": {
                "score": detailed_evaluation.get('score', 0.0),
                "reasoning": detailed_evaluation.get('reasoning', ''),
                "key_findings": detailed_evaluation.get('key_findings', []),
                "information_gaps": detailed_evaluation.get('information_gaps', []),
                "recommendations": detailed_evaluation.get('recommendations', []),
            }
        }
    }
    
    if comment_analysis:
        results["comment_analysis"] = comment_analysis
    
    return results

def main():
    """Main function to analyze multiple proposals"""
    # Test proposals
    proposals = [
        {
            "name": "Uniswap V4 and Unichain Incentives",
            "url": "https://gov.uniswap.org/t/governance-proposal-uniswap-unleashed-unichain-and-uniswap-v4-liquidity-incentives/25250",
            "expected_category": "treasury_management"
        }
    ]
    
    for proposal in proposals:
        try:
            print(f"\n{'='*50}")
            print(f"Analyzing: {proposal['name']}")
            print(f"URL: {proposal['url']}")
            print(f"{'='*50}")
            
            # Analyze the proposal with sentiment analysis disabled
            results = analyze_proposal(proposal['url'], analyze_sentiment=False)
            
            # Save results to a JSON file
            output_file = f"analysis_results_{proposal['name'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"\nAnalysis complete! Results saved to {output_file}")
            
            # Print summary
            print("\nAnalysis Summary:")
            print(f"Primary Category: {results['analysis']['primary_category']}")
            print(f"Category Weights: {results['analysis']['category_weights'][results['analysis']['primary_category']]}")
            print(f"Detailed Evaluation Score: {results['analysis']['detailed_evaluation']['score']:.2f}")
            
        except Exception as e:
            print(f"\nError analyzing proposal: {str(e)}")
            continue

if __name__ == "__main__":
    main() 