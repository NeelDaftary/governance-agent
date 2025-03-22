from discourse_parser import DiscourseParser

def main():
    # Using Uniswap's governance forum with the specific proposal
    forum_url = "https://gov.uniswap.org"
    parser = DiscourseParser(forum_url)
    
    # The topic ID from the URL: .../25250
    topic_id = 25250
    
    print(f"Fetching Uniswap proposal {topic_id} from {forum_url}...")
    
    # Fetch the topic data
    topic_data = parser.get_topic(topic_id)
    
    if topic_data:
        # Extract and print proposal details
        details = parser.extract_proposal_details(topic_data)
        print("\nProposal Details:")
        print("=" * 50)
        print(f"Title: {details['title']}")
        print(f"Created at: {details['created_at']}")
        print(f"Posts: {details['post_count']} | Participants: {details['participant_count']}")
        print(f"Likes: {details['like_count']} | Views: {details['views']}")
        if details['tags']:
            print(f"Tags: {', '.join(details['tags'])}")
        
        print("\nProposal Content (first 500 characters):")
        print("=" * 50)
        print(details['content'][:500] + "..." if len(details['content']) > 500 else details['content'])
        
        print("\nFirst 3 Comments:")
        print("=" * 50)
        for i, comment in enumerate(details['comments'][:3], 1):
            print(f"\nComment #{i} (by {comment['username']} at {comment['created_at']}):")
            print(f"Likes: {comment['like_count']} | Replies: {comment['reply_count']} | Score: {comment['score']}")
            if comment['is_solution']:
                print("✓ Marked as solution")
            if comment['reactions']:
                print(f"Reactions: {comment['reactions']}")
            print("-" * 40)
            # Print first 300 characters of each comment
            content_preview = comment['content'][:300] + "..." if len(comment['content']) > 300 else comment['content']
            print(content_preview)
    else:
        print("Failed to fetch the proposal.")

if __name__ == "__main__":
    main() 