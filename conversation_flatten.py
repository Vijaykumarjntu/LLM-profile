import json
from datetime import datetime

def extract_user_messages(conversation):
    """Extract all user messages from the conversation mapping"""
    messages = []
    mapping = conversation.get('mapping', {})
    
    for node_id, node in mapping.items():
        if node_id == 'root':
            continue
            
        message_data = node.get('message')
        if message_data and 'fragments' in message_data:
            # Check all fragments in the message
            for fragment in message_data.get('fragments', []):
                if fragment.get('type') == 'REQUEST':  # User message
                    content = fragment.get('content', '')
                    inserted_at = message_data.get('inserted_at', '')
                    
                    messages.append({
                        'conversation_id': conversation.get('id'),
                        'title': conversation.get('title'),
                        'timestamp': inserted_at,
                        'content': content,
                        'model': message_data.get('model'),
                        'node_id': node_id
                    })
    
    return messages

# Load the original file
print("📂 Loading conversations.json...")
with open('conversations.json', 'r', encoding='utf-8') as f:
    conversations = json.load(f)

print(f"✅ Loaded {len(conversations)} conversations")

# Extract all user messages
all_messages = []
for conv in conversations:
    user_msgs = extract_user_messages(conv)
    all_messages.extend(user_msgs)
    print(f"📝 '{conv.get('title', 'Untitled')[:40]}...' → {len(user_msgs)} user messages")

print(f"\n💬 Total user messages extracted: {len(all_messages)}")

# Sort by timestamp
all_messages.sort(key=lambda x: x.get('timestamp', ''))

# Save as clean JSON
output_file = 'clean_messages.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_messages, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved to {output_file}")
print(f"📏 File size: {len(json.dumps(all_messages, ensure_ascii=False)) / 1024 / 1024:.2f} MB")

# Show samples
print("\n📝 Sample messages:")
for i, msg in enumerate(all_messages[:3]):
    print(f"\n{i+1}. [{msg['title']}]")
    print(f"   Time: {msg['timestamp']}")
    print(f"   Content: {msg['content'][:150]}...")