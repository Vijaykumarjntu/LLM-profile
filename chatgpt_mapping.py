import json
from datetime import datetime

def flatten_chatgpt_conversation(conv):
    """Extract all messages from ChatGPT export format"""
    messages = []
    mapping = conv.get('mapping', {})
    
    for node_id, node in mapping.items():
        if node_id == 'root':
            continue
            
        message_data = node.get('message')
        if not message_data:
            continue
        
        # Get role from author
        author = message_data.get('author', {})
        role = author.get('role', '')
        
        # Map ChatGPT roles to our standard
        if role == 'user':
            role_std = 'user'
        elif role == 'assistant':
            role_std = 'assistant'
        elif role == 'system':
            role_std = 'system'
        else:
            continue  # Skip system messages
        
        # Extract content from parts
        content_data = message_data.get('content', {})
        parts = content_data.get('parts', [])
        content = ' '.join(parts) if parts else ''
        
        # Skip empty messages
        if not content.strip():
            continue
        
        # Convert timestamp (Unix timestamp to ISO)
        create_time = message_data.get('create_time')
        if create_time:
            timestamp = datetime.fromtimestamp(create_time).isoformat()
        else:
            timestamp = None
        
        messages.append({
            'conversation_id': conv.get('id'),
            'title': conv.get('title', 'Untitled'),
            'timestamp': timestamp,
            'role': role_std,
            'content': content,
            'node_id': node_id
        })
    
    return messages

# Load ChatGPT export
print("📂 Loading ChatGPT conversations...")
with open('conversations_gpt0.json', 'r', encoding='utf-8') as f:
    conversations = json.load(f)

print(f"✅ Loaded {len(conversations)} conversations")

# Flatten all
all_messages = []
for conv in conversations:
    msgs = flatten_chatgpt_conversation(conv)
    all_messages.extend(msgs)

print(f"💬 Extracted {len(all_messages)} messages")
print(f"   User: {len([m for m in all_messages if m['role'] == 'user'])}")
print(f"   Assistant: {len([m for m in all_messages if m['role'] == 'assistant'])}")

# Sort by timestamp
all_messages.sort(key=lambda x: x.get('timestamp', ''))

# Save clean version
output_file = 'clean_chatgpt_messages.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_messages, f, indent=2, ensure_ascii=False)

print(f"✅ Saved to {output_file}")

# Preview
print("\n📝 Sample messages:")
for msg in all_messages[:3]:
    print(f"\n[{msg['role']}] {msg['title']}")
    print(f"   Time: {msg['timestamp']}")
    print(f"   Content: {msg['content'][:150]}...")