from discourse_parser import DiscourseParser
from proposal_analyzer import ProposalAnalyzer
import json
from typing import Dict, Any
import os

def analyze_proposal(url: str, topic_id: str) -> Dict[str, Any]:
    """
    Analyze a proposal from any Discourse forum.
    
    Args:
        url: The base URL of the Discourse forum
        topic_id: The topic ID of the proposal
        
    Returns:
        dict: Analysis results
    """
    # Initialize parser and analyzer
    parser = DiscourseParser()
    analyzer = ProposalAnalyzer()
    
    print(f"\nFetching proposal {topic_id} from {url}...")
    
    # Fetch and parse the proposal
    topic_data = parser.fetch_topic(url, topic_id)
    proposal_details = parser.extract_proposal_details(topic_data)
    
    print("\nProposal Details:")
    print("=" * 50)
    print(f"Title: {proposal_details['title']}")
    print(f"Created at: {proposal_details['created_at']}")
    
    print("\nAnalyzing proposal...")
    
    # Analyze the proposal
    analysis = analyzer.analyze_proposal(proposal_details)
    
    print("\nAnalysis Results:")
    print("=" * 50)
    print(f"Primary Category: {analysis['primary_category']}")
    
    print("\nCategory Scores:")
    print(f"Protocol Parameters: {analysis['protocol_parameters']:.2f}")
    print(f"Treasury Management: {analysis['treasury_management']:.2f}")
    print(f"Tokenomics: {analysis['tokenomics']:.2f}")
    print(f"Protocol Upgrades: {analysis['protocol_upgrades']:.2f}")
    print(f"Governance Process: {analysis['governance_process']:.2f}")
    print(f"Partnerships Integrations: {analysis['partnerships_integrations']:.2f}")
    print(f"Risk Management: {analysis['risk_management']:.2f}")
    print(f"Community Initiatives: {analysis['community_initiatives']:.2f}")
    
    print(f"\nTotal Score: {analysis['sum']:.2f}")
    
    print("\nSummary:")
    print("-" * 40)
    print(analysis['summary'])
    
    # Save analysis results
    output_file = f"proposal_{topic_id}_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\nAnalysis saved to {output_file}")
    
    return analysis

def main():
    # Test with Uniswap proposal
    print("\n=== Testing with Uniswap Proposal ===")
    uniswap_analysis = analyze_proposal(
        "https://gov.uniswap.org",
        "25250"
    )
    
    # Test with Morpho proposal
    print("\n=== Testing with Morpho Proposal ===")
    morpho_analysis = analyze_proposal(
        "https://forum.morpho.org",
        "1177"
    )
    
    # Compare results
    print("\n=== Comparison of Results ===")
    print("\nUniswap Proposal:")
    print(f"Primary Category: {uniswap_analysis['primary_category']}")
    print(f"Total Score: {uniswap_analysis['sum']:.2f}")
    
    print("\nMorpho Proposal:")
    print(f"Primary Category: {morpho_analysis['primary_category']}")
    print(f"Total Score: {morpho_analysis['sum']:.2f}")

if __name__ == "__main__":
    main() 