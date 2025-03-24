from typing import Dict, Any, List

def prepare_proposal_text(proposal_details: Dict[str, Any], include_comments: bool = True, max_comments: int = 3) -> str:
    """
    Prepare the proposal text for analysis by combining relevant fields.
    
    Args:
        proposal_details: Dictionary containing proposal details
        include_comments: Whether to include comments in the text
        max_comments: Maximum number of comments to include
        
    Returns:
        str: Formatted proposal text
    """
    text_parts = [
        f"Title: {proposal_details['title']}",
        f"\nProposal Content:\n{proposal_details['content']}"
    ]
    
    # Add comments if requested and available
    if include_comments and proposal_details.get('comments'):
        text_parts.append("\nKey Comments:")
        for comment in proposal_details['comments'][:max_comments]:
            text_parts.append(f"\n- {comment['content'][:500]}...")
    
    return "\n".join(text_parts)

def clean_html_content(html_content: str) -> str:
    """
    Clean HTML content by removing tags and formatting text.
    
    Args:
        html_content: HTML content to clean
        
    Returns:
        str: Cleaned text content
    """
    # Basic HTML cleaning - can be enhanced with a proper HTML parser if needed
    text = html_content.replace('<br>', '\n')
    text = text.replace('</p>', '\n')
    text = text.replace('</div>', '\n')
    text = text.replace('</li>', '\n')
    text = text.replace('</h1>', '\n')
    text = text.replace('</h2>', '\n')
    text = text.replace('</h3>', '\n')
    text = text.replace('</h4>', '\n')
    text = text.replace('</h5>', '\n')
    text = text.replace('</h6>', '\n')
    
    # Remove HTML tags
    while '<' in text and '>' in text:
        start = text.find('<')
        end = text.find('>', start)
        if end == -1:
            break
        text = text[:start] + text[end + 1:]
    
    # Clean up whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    return '\n'.join(lines) 