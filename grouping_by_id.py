import json
from collections import defaultdict

# Load full conversations (both user + assistant)
with open('full_conversations.json', 'r', encoding='utf-8') as f:
    all_messages = json.load(f)

# Group by conversation_id
conversations = defaultdict(list)
for msg in all_messages:
    conversations[msg['conversation_id']].append(msg)

# Create a summary for each conversation
summaries = []
for conv_id, msgs in conversations.items():
    # Get title and first few messages
    title = msgs[0]['title']
    user_msgs = [m['content'] for m in msgs if m['role'] == 'user'][:5]
    
    summaries.append({
        'id': conv_id,
        'title': title,
        'sample': user_msgs[:3],  # First 3 user messages
        'msg_count': len(msgs),
        'timestamp': msgs[0]['timestamp']
    })

# Save summaries
with open('conv_summaries.json', 'w') as f:
    json.dump(summaries, f, indent=2)

print(f"✅ Created summaries for {len(summaries)} conversations")