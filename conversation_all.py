import json

def extract_full_conversation(conversation):
    """Extract both user and assistant messages in order"""
    messages = []
    mapping = conversation.get('mapping', {})
    
    # Build a tree of messages in order
    # First find the root and traverse
    root = mapping.get('root')
    if not root:
        return messages
    
    current_id = root.get('children', [None])[0]
    
    while current_id and current_id in mapping:
        node = mapping[current_id]
        message_data = node.get('message')
        
        if message_data and 'fragments' in message_data:
            for fragment in message_data.get('fragments', []):
                msg_type = fragment.get('type')
                content = fragment.get('content', '')
                
                if msg_type == 'REQUEST':
                    role = 'user'
                elif msg_type == 'RESPONSE':
                    role = 'assistant'
                else:
                    continue
                
                messages.append({
                    'conversation_id': conversation.get('id'),
                    'title': conversation.get('title'),
                    'timestamp': message_data.get('inserted_at'),
                    'role': role,
                    'content': content,
                })
        
        # Move to next message
        children = node.get('children', [])
        current_id = children[0] if children else None
    
    return messages

# Load and extract everything
with open('conversations.json', 'r', encoding='utf-8') as f:
    conversations = json.load(f)

all_messages = []
for conv in conversations:
    all_messages.extend(extract_full_conversation(conv))

print(f"✅ Extracted {len(all_messages)} messages total")
print(f"   User: {len([m for m in all_messages if m['role'] == 'user'])}")
print(f"   Assistant: {len([m for m in all_messages if m['role'] == 'assistant'])}")

# Save full conversations
with open('full_conversations.json', 'w', encoding='utf-8') as f:
    json.dump(all_messages, f, indent=2, ensure_ascii=False)

print("✅ Saved to full_conversations.json")