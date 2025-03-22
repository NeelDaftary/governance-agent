import requests
from typing import Dict, Any, Optional, List
from bs4 import BeautifulSoup
import re

class DiscourseParser:
    def __init__(self):
        """
        Initialize the Discourse parser.
        """
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

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

    def fetch_topic(self, base_url: str, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch a specific topic (proposal) by its ID from any Discourse forum.
        
        Args:
            base_url (str): The base URL of the Discourse forum
            topic_id (str): The ID of the topic to fetch
            
        Returns:
            dict: Topic data including title, content, and metadata
            None: If the topic cannot be fetched
        """
        try:
            # Clean the base URL
            base_url = base_url.rstrip('/')
            
            # Try both .json and regular URL formats
            urls_to_try = [
                f"{base_url}/t/{topic_id}.json",
                f"{base_url}/t/{topic_id}"
            ]
            
            for url in urls_to_try:
                try:
                    response = self.session.get(url)
                    response.raise_for_status()
                    return response.json()
                except requests.RequestException:
                    continue
            
            raise requests.RequestException(f"Failed to fetch topic {topic_id} from {base_url}")
            
        except requests.RequestException as e:
            print(f"Error fetching topic {topic_id}: {str(e)}")
            return None

    def extract_proposal_details(self, topic_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract relevant proposal details from the topic data.
        
        Args:
            topic_data (dict): Raw topic data from the Discourse API
            
        Returns:
            dict: Extracted proposal details including title, content, and comments
        """
        if not topic_data:
            return {}
        
        # Extract posts from the post stream
        posts = topic_data.get('post_stream', {}).get('posts', [])
        
        # First post is the proposal content, rest are comments
        comments = []
        if len(posts) > 1:  # If there are comments
            for post in posts[1:]:  # Skip the first post (proposal content)
                comments.append({
                    'username': post.get('username', ''),
                    'created_at': post.get('created_at', ''),
                    'content': self.clean_html_content(post.get('cooked', '')),
                    'post_number': post.get('post_number', 0),
                    'like_count': post.get('like_count', 0),
                    'reply_count': len(post.get('replies', [])),
                    'score': post.get('score', 0),
                    'reactions': post.get('reactions', []),
                    'is_solution': post.get('accepted_answer', False)
                })
        
        return {
            'title': topic_data.get('title', ''),
            'content': self.clean_html_content(posts[0].get('cooked', '') if posts else ''),
            'created_at': topic_data.get('created_at', ''),
            'post_count': topic_data.get('posts_count', 0),
            'participant_count': topic_data.get('participant_count', 0),
            'like_count': topic_data.get('like_count', 0),
            'views': topic_data.get('views', 0),
            'category': topic_data.get('category_id', None),
            'tags': topic_data.get('tags', []),
            'comments': comments
        } 