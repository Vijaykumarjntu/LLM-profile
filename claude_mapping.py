import json
from datetime import datetime

def extract_conversations_new_format(data):
    """Extract all messages from OpenWebUI format"""
    all_messages = []
    
    for conv in data:
        conv_id = conv.get('uuid')
        title = conv.get('name') or conv.get('summary') or "Untitled"
        created_at = conv.get('created_at')
        
        chat_messages = conv.get('chat_messages', [])
        
        for msg in chat_messages:
            # Extract text from content array
            content_text = ""
            content_list = msg.get('content', [])
            for content_item in content_list:
                if content_item.get('type') == 'text':
                    content_text += content_item.get('text', '')
            
            # Map sender to role
            sender = msg.get('sender')
            role = 'user' if sender == 'human' else 'assistant' if sender else 'unknown'
            
            all_messages.append({
                'conversation_id': conv_id,
                'title': title,
                'timestamp': msg.get('created_at') or created_at,
                'role': role,
                'content': content_text,
                'message_id': msg.get('uuid')
            })
    
    return all_messages

# Load the new file
print("📂 Loading new conversations file...")
with open('conversations_claude.json', 'r', encoding='utf-8') as f:
    # data = json.load(f)
    raw = f.read()
    data = json.loads(raw, strict=False)

print(f"✅ Loaded {len(data)} conversations")

# Extract messages
all_messages = extract_conversations_new_format(data)

print(f"💬 Extracted {len(all_messages)} total messages")
print(f"   User: {len([m for m in all_messages if m['role'] == 'user'])}")
print(f"   Assistant: {len([m for m in all_messages if m['role'] == 'assistant'])}")

# Sort by timestamp
all_messages.sort(key=lambda x: x.get('timestamp', ''))

# Save as clean JSON
output_file = 'clean_conversations_new.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_messages, f, indent=2, ensure_ascii=False)

print(f"✅ Saved to {output_file}")

# Preview
print("\n📝 Sample messages:")
for msg in all_messages[:3]:
    print(f"\n[{msg['role']}] {msg['title']}")
    print(f"   {msg['content'][:150]}...")