from src.discourse_parser import DiscourseParser
from src.sentiment_analyzer import SentimentAnalyzer
from src.proposal_analyzer import ProposalAnalyzer
import json
from datetime import datetime

def test_sentiment_analysis(url: str) -> None:
    """
    Test sentiment analysis on a proposal's comments.
    
    Args:
        url: The URL of the proposal to analyze
    """
    print(f"\n{'='*50}")
    print(f"Testing Sentiment Analysis")
    print(f"URL: {url}")
    print(f"{'='*50}")
    
    # Step 1: Parse proposal data
    parser = DiscourseParser()
    proposal_data = parser.parse_proposal(url)
    
    if not proposal_data.get('comments'):
        print("\nNo comments found for analysis")
        return
    
    # Step 2: Get proposal summary from proposal analyzer
    analyzer = ProposalAnalyzer()
    analysis_results = analyzer.analyze_proposal({
        'title': proposal_data['title'],
        'content': proposal_data['content']
    })
    
    # Step 3: Analyze comments
    sentiment_analyzer = SentimentAnalyzer()
    comment_analysis = sentiment_analyzer.analyze_all_comments(
        proposal_data['comments'],
        analysis_results['summary']
    )
    
    # Save results
    results = {
        "proposal": {
            "url": url,
            "title": proposal_data['title'],
            "created_at": proposal_data['created_at']
        },
        "proposal_summary": analysis_results['summary'],
        "comment_analysis": comment_analysis
    }
    
    output_file = f"sentiment_analysis_{proposal_data['title'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSentiment Analysis Results:")
    print(f"Overall Sentiment Score: {comment_analysis['overall_sentiment']:.2f}")
    print(f"Number of Comments Analyzed: {len(proposal_data['comments'])}")
    print(f"\nResults saved to: {output_file}")

def main():
    """Main function to test sentiment analysis"""
    # Test proposal
    test_url = "https://forum.morpho.org/t/mip65-new-scalable-rewards-model/617"
    
    try:
        test_sentiment_analysis(test_url)
    except Exception as e:
        print(f"\nError in sentiment analysis: {str(e)}")

if __name__ == "__main__":
    main() 