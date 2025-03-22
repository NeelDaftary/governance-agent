import pytest
from src.discourse_parser import DiscourseParser

def test_discourse_parser_initialization():
    base_url = "https://forum.example.com"
    parser = DiscourseParser(base_url)
    assert parser.base_url == base_url
    
def test_discourse_parser_url_cleaning():
    base_url = "https://forum.example.com/"
    parser = DiscourseParser(base_url)
    assert parser.base_url == "https://forum.example.com"
    
def test_extract_proposal_details_empty_data():
    parser = DiscourseParser("https://forum.example.com")
    details = parser.extract_proposal_details({})
    assert details == {}

def test_uniswap_proposal_fetch():
    """Test fetching a specific Uniswap governance proposal"""
    parser = DiscourseParser("https://gov.uniswap.org")
    topic_id = 25250
    
    # Fetch the proposal
    topic_data = parser.get_topic(topic_id)
    assert topic_data is not None, "Failed to fetch the proposal"
    
    # Extract details
    details = parser.extract_proposal_details(topic_data)
    
    # Verify we got the expected proposal
    assert "Uniswap Unleashed" in details['title'], "Unexpected proposal title"
    assert details['post_count'] > 0, "No posts found"
    assert details['participant_count'] > 0, "No participants found"
    assert len(details['content']) > 0, "No content found"
    
    # Verify comments
    assert 'comments' in details, "Comments field missing"
    assert isinstance(details['comments'], list), "Comments should be a list"
    assert len(details['comments']) > 0, "No comments found"
    
    # Verify structure of first comment
    first_comment = details['comments'][0]
    assert 'username' in first_comment, "Comment username missing"
    assert 'created_at' in first_comment, "Comment creation date missing"
    assert 'content' in first_comment, "Comment content missing"
    assert 'post_number' in first_comment, "Comment post number missing"
    assert len(first_comment['content']) > 0, "Comment content empty" 