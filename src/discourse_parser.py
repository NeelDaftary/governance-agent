import requests
from typing import Dict, Any, List
from datetime import datetime
from .text_utils import clean_html_content

class DiscourseParser:
    def __init__(self):
        """Initialize the discourse parser with session setup"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_topic(self, base_url: str, topic_id: str) -> Dict[str, Any]:
        """
        Fetch topic data from the Discourse API.
        
        Args:
            base_url: Base URL of the Discourse forum
            topic_id: Topic ID to fetch
            
        Returns:
            dict: Topic data
        """
        api_url = f"{base_url}/t/{topic_id}.json"
        response = self.session.get(api_url)
        response.raise_for_status()
        return response.json()

    def extract_proposal_details(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant details from the topic data.
        
        Args:
            topic_data: Raw topic data from the API
            
        Returns:
            dict: Extracted proposal details
        """
        # Extract basic details
        title = topic_data.get('title', '')
        created_at = topic_data.get('created_at', '')
        
        # Extract and clean the main content
        post_stream = topic_data.get('post_stream', {})
        posts = post_stream.get('posts', [])
        main_content = ''
        if posts:
            main_content = clean_html_content(posts[0].get('cooked', ''))
        
        # Extract and clean comments
        comments = []
        for post in posts[1:]:  # Skip the first post (main content)
            comment = {
                'content': clean_html_content(post.get('cooked', '')),
                'created_at': post.get('created_at', ''),
                'username': post.get('username', '')
            }
            comments.append(comment)
        
        return {
            'title': title,
            'created_at': created_at,
            'content': main_content,
            'comments': comments
        }

    def parse_proposal(self, url: str) -> Dict[str, Any]:
        """
        Parse a proposal from a Discourse forum URL.
        
        Args:
            url: URL of the proposal
            
        Returns:
            dict: Parsed proposal details
        """
        # Extract base URL and topic ID from the URL
        parts = url.split('/t/')
        if len(parts) != 2:
            raise ValueError("Invalid proposal URL format")
            
        base_url = parts[0]
        topic_id = parts[1].split('/')[0]
        
        # Fetch and parse the proposal
        topic_data = self.fetch_topic(base_url, topic_id)
        return self.extract_proposal_details(topic_data) 