import os
from dotenv import load_dotenv
from discourse_parser import DiscourseParser
from evaluator_agents import EvaluatorAgent
import json
from datetime import datetime

def analyze_proposal(url: str) -> dict:
    """
    Analyze a governance proposal using specialized evaluator agents.
    
    Args:
        url: The URL of the proposal to analyze
        
    Returns:
        dict: Analysis results including category scores and detailed evaluations
    """
    # Initialize parser and evaluator
    parser = DiscourseParser()
    evaluator = EvaluatorAgent()
    
    # Parse the proposal
    proposal_details = parser.parse_proposal(url)
    
    # First, get the primary category using the general analyzer
    from proposal_analyzer import ProposalAnalyzer
    analyzer = ProposalAnalyzer()
    analysis_results = analyzer.analyze_proposal(proposal_details)
    
    # Extract category scores and remove non-category fields
    category_scores = {
        k: v for k, v in analysis_results.items() 
        if k not in ['sum', 'primary_category', 'summary']
    }
    
    # Get the primary category (highest score)
    primary_category = analysis_results.get('primary_category')
    if not primary_category:  # Fallback to calculating it if not provided
        primary_category = max(category_scores.items(), key=lambda x: float(x[1]))[0]
    
    # Get detailed evaluation from the specialized agent
    detailed_evaluation = evaluator.evaluate_proposal(primary_category, proposal_details)
    
    # Combine results
    results = {
        "proposal_url": url,
        "analysis_timestamp": datetime.now().isoformat(),
        "category_scores": category_scores,
        "primary_category": primary_category,
        "detailed_evaluation": detailed_evaluation,
        "summary": analysis_results.get('summary', '')
    }
    
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
            
            # Analyze the proposal
            results = analyze_proposal(proposal['url'])
            
            # Save results to a JSON file
            output_file = f"analysis_results_{proposal['name'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"\nAnalysis complete! Results saved to {output_file}")
            
            # Print summary
            print("\nAnalysis Summary:")
            print(f"Primary Category: {results['primary_category']}")
            print(f"Category Score: {results['category_scores'][results['primary_category']]}")
            print(f"Detailed Evaluation Score: {results['detailed_evaluation']['score']:.2f}")
            
            # Compare with expected category
            if results['primary_category'] == proposal['expected_category']:
                print("\n✓ Category matches expected category")
            else:
                print(f"\n⚠ Category mismatch: Expected {proposal['expected_category']}, got {results['primary_category']}")
            
            print("\nDetailed Analysis Preview:")
            print("-" * 40)
            print(results['detailed_evaluation']['analysis'][:500] + "...")
            
        except Exception as e:
            print(f"\nError analyzing proposal: {str(e)}")
            continue

if __name__ == "__main__":
    main() 