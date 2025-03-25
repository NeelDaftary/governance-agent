from src.discourse_parser import DiscourseParser
from src.sentiment_analyzer import SentimentAnalyzer
from src.proposal_analyzer import ProposalAnalyzer
from src.evaluator_agent import EvaluatorAgent
import json
from datetime import datetime

def test_proposal_analysis(url: str, analyze_sentiment: bool = True) -> None:
    """
    Test both proposal analysis and sentiment analysis on a proposal.
    
    Args:
        url: The URL of the proposal to analyze
        analyze_sentiment: Whether to perform sentiment analysis on comments
    """
    print("\n" + "="*50)
    print("Testing Proposal Analysis")
    print(f"URL: {url}")
    print("="*50 + "\n")
    
    # Parse proposal data
    parser = DiscourseParser()
    proposal_data = parser.parse_proposal(url)
    
    # Analyze proposal content
    analyzer = ProposalAnalyzer()
    analysis_result = analyzer.analyze_proposal(proposal_data)
    
    # Get detailed evaluation
    evaluator = EvaluatorAgent()
    detailed_eval = evaluator.evaluate_proposal(proposal_data)
    
    # Analyze comments if requested
    sentiment_result = None
    if analyze_sentiment and proposal_data.get('comments'):
        sentiment_analyzer = SentimentAnalyzer()
        sentiment_result = sentiment_analyzer.analyze_all_comments(proposal_data['comments'])
    
    # Combine results
    results = {
        'proposal_details': {
            'title': proposal_data['title'],
            'created_at': proposal_data['created_at'],
            'url': url
        },
        'analysis': analysis_result,
        'evaluation': detailed_eval,
        'sentiment_analysis': sentiment_result
    }
    
    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    proposal_title = proposal_data['title'].lower().replace(' ', '_')[:50]
    filename = f"analysis_results_{proposal_title}_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\nAnalysis Summary:")
    print(f"Primary Category: {analysis_result['primary_category']}")
    print(f"Category Score: {analysis_result[analysis_result['primary_category']]:.2f}")
    print(f"Detailed Evaluation Score: {detailed_eval['overall_score']:.2f}")
    
    if sentiment_result:
        print(f"\nComment Analysis:")
        print(f"Overall Sentiment Score: {sentiment_result['sentiment_score']:.2f}")
        print(f"Number of Comments Analyzed: {sentiment_result['num_comments']}")
    
    print(f"\nFull results saved to: {filename}")

def main():
    """Main function to test proposal analysis"""
    # Test URL - Compound proposal
    test_url = "https://www.comp.xyz/t/compound-morpho-polygon-collaboration/6306"
    test_proposal_analysis(test_url)

if __name__ == "__main__":
    main() 