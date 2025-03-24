import requests
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
import json

class DiscourseParser:
    def __init__(self):
        """
        Initialize the Discourse parser.
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_topic(self, base_url: str, topic_id: str) -> Dict[str, Any]:
        """
        Fetch a topic from a Discourse forum.
        
        Args:
            base_url: The base URL of the Discourse forum
            topic_id: The topic ID to fetch
            
        Returns:
            dict: Topic data including title, content, and comments
        """
        # Clean the base URL
        base_url = base_url.rstrip('/')
        
        # Construct the API URL
        api_url = f"{base_url}/t/{topic_id}.json"
        
        try:
            response = self.session.get(api_url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching topic: {str(e)}")
            return {}

    def clean_html_content(self, html_content: str) -> str:
        """
        Clean HTML content by removing tags and formatting text.
        
        Args:
            html_content (str): Raw HTML content
            
        Returns:
            str: Cleaned text content
        """
        if not html_content:
            return ""
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Handle code blocks specially
        for code in soup.find_all(['pre', 'code']):
            # Preserve code block formatting
            code.replace_with(f"\nCODE:\n{code.get_text()}\n")
        
        # Handle links
        for link in soup.find_all('a'):
            text = link.get_text()
            href = link.get('href', '')
            if text != href:
                link.replace_with(f"{text} ({href})")
            else:
                link.replace_with(text)
        
        # Get text and clean up whitespace
        text = soup.get_text()
        text = re.sub(r'\n\s*\n', '\n\n', text)  # Remove multiple newlines
        text = re.sub(r' +', ' ', text)  # Remove multiple spaces
        return text.strip()

    def extract_proposal_details(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant details from a topic.
        
        Args:
            topic_data: Raw topic data from the API
            
        Returns:
            dict: Extracted proposal details
        """
        if not topic_data:
            return {}
            
        # Extract basic details
        details = {
            'title': topic_data.get('title', ''),
            'created_at': topic_data.get('created_at', ''),
            'content': '',
            'comments': []
        }
        
        # Extract the main post content
        if 'post_stream' in topic_data and 'posts' in topic_data['post_stream']:
            posts = topic_data['post_stream']['posts']
            if posts:
                # Get the first post (main proposal)
                main_post = posts[0]
                details['content'] = main_post.get('cooked', '')
                
                # Get comments (excluding the main post)
                for post in posts[1:]:
                    details['comments'].append({
                        'content': post.get('cooked', ''),
                        'created_at': post.get('created_at', '')
                    })
                    
        return details
        
    def parse_proposal(self, url: str) -> Dict[str, Any]:
        """
        Parse a proposal from its URL.
        
        Args:
            url: The full URL of the proposal
            
        Returns:
            dict: Parsed proposal details
        """
        # Extract base URL and topic ID from the URL
        match = re.match(r'(https?://[^/]+)/t/([^/]+)/(\d+)', url)
        if not match:
            raise ValueError(f"Invalid proposal URL format: {url}")
            
        base_url, _, topic_id = match.groups()
        
        # Fetch and parse the proposal
        topic_data = self.fetch_topic(base_url, topic_id)
        
        return self.extract_proposal_details(topic_data) 