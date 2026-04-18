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
            continue  # Skip system messages
        else:
            continue
        
        # Extract content from parts - handles both string and dict
        content_data = message_data.get('content', {})
        parts = content_data.get('parts', [])
        
        content = ''
        for part in parts:
            if isinstance(part, str):
                content += part
            elif isinstance(part, dict):
                # Some parts might have 'text' field or other structure
                content += part.get('text', str(part))
            else:
                content += str(part)
        
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
with open('conversations-gpt5.json', 'r', encoding='utf-8') as f:
    conversations = json.load(f)

print(f"✅ Loaded {len(conversations)} conversations")

# Flatten all
all_messages = []
for conv in conversations:
    msgs = flatten_chatgpt_conversation(conv)
    all_messages.extend(msgs)
    if len(msgs) > 0:
        print(f"   {conv.get('title', 'Untitled')[:40]}: {len(msgs)} msgs")

print(f"\n💬 Total messages extracted: {len(all_messages)}")
print(f"   User: {len([m for m in all_messages if m['role'] == 'user'])}")
print(f"   Assistant: {len([m for m in all_messages if m['role'] == 'assistant'])}")

# Sort by timestamp
all_messages.sort(key=lambda x: x.get('timestamp', ''))

# Save clean version
output_file = 'clean_chatgpt_messages6.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_messages, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved to {output_file}")

# Preview first few
print("\n📝 Sample messages:")
for msg in all_messages[:3]:
    print(f"\n[{msg['role']}] {msg['title']}")
    print(f"   {msg['content'][:150]}...")