import json
from datetime import datetime
from collections import defaultdict, Counter
import re

def load_and_prepare_data():
    with open('clean_messages.json', 'r', encoding='utf-8') as f:
        messages = json.load(f)
    
    # Parse timestamps
    for msg in messages:
        if msg.get('timestamp'):
            try:
                ts = msg['timestamp'].replace('+08:00', '')
                msg['datetime'] = datetime.fromisoformat(ts)
            except:
                msg['datetime'] = None
        else:
            msg['datetime'] = None
    
    # Filter out None timestamps
    messages = [m for m in messages if m['datetime']]
    messages.sort(key=lambda x: x['datetime'])
    
    return messages

# Define skill domains and their keywords (fixed regex patterns)
SKILLS = {
    "Rust Programming": {
        "keywords": [r'rust', r'cargo', r'rustc', r'cargo\.toml', r'src/'],
        "subskills": {
            "Basics": [r'cargo new', r'main\(\)', r'println', r'let\s+\w+', r'fn\s+\w+'],
            "Ownership": [r'borrow', r'ownership', r'reference', r'&mut', r'clone'],
            "Error Handling": [r'result', r'option', r'unwrap', r'expect', r'\? operator'],
            "Async": [r'async', r'await', r'futures', r'tokio', r'embassy', r'executor'],
            "Embedded": [r'no_std', r'embassy', r'cortex-m', r'pac', r'peripheral'],
        }
    },
    "Web3 & Blockchain": {
        "keywords": [r'web3', r'ethereum', r'solidity', r'smart contract', r'blockchain', r'crypto'],
        "subskills": {
            "Basics": [r'wallet', r'transaction', r'gas', r'address'],
            "Smart Contracts": [r'solidity', r'contract', r'deploy', r'remix', r'hardhat'],
            "Security": [r'reentrancy', r'access control', r'audit', r'vulnerability', r'hack'],
            "Infrastructure": [r'node', r'rpc', r'infura', r'alchemy', r'mev'],
        }
    },
    "RAG & AI": {
        "keywords": [r'rag', r'llm', r'embedding', r'vector', r'retrieval', r'generation'],
        "subskills": {
            "Basics": [r'chunk', r'context', r'prompt', r'query'],
            "Vector DB": [r'faiss', r'pinecone', r'vector database', r'index'],
            "Models": [r'gpt', r'llama', r'sentence transformer', r'embedding model'],
            "PDF Processing": [r'pdfplumber', r'pypdf', r'extract', r'parse'],
        }
    },
    "System Architecture": {
        "keywords": [r'architect', r'design', r'system', r'scale', r'tradeoff', r'workflow'],
        "subskills": {
            "Multi-agent": [r'agent', r'orchestrat', r'coordinator', r'workflow'],
            "Database": [r'database', r'schema', r'query', r'transaction', r'ac'],
            "API": [r'api', r'endpoint', r'rest', r'graphql', r'webhook'],
            "Event-driven": [r'event', r'message queue', r'kafka', r'rabbitmq'],
        }
    },
    "DevOps & Tools": {
        "keywords": [r'git', r'docker', r'ci/cd', r'deploy', r'aws', r'cloud'],
        "subskills": {
            "Version Control": [r'git', r'commit', r'branch', r'merge', r'github'],
            "Containers": [r'docker', r'container', r'image', r'compose'],
            "CI/CD": [r'github actions', r'pipeline', r'deploy', r'test'],
        }
    },
    "Security": {
        "keywords": [r'security', r'vulnerability', r'threat', r'attack', r'audit'],
        "subskills": {
            "Web Security": [r'xss', r'sql injection', r'csrf', r'sanitize'],
            "Firmware": [r'firmware', r'bootloader', r'tpm', r'secure boot'],
            "Identity": [r'identity', r'auth', r'oauth', r'jwt', r'signature'],
        }
    }
}

def detect_skills(message):
    """Detect which skills and subskills appear in a message"""
    content = message['content'].lower()
    detected = {}
    
    for skill_name, skill_info in SKILLS.items():
        # Check main skill keywords
        skill_match = False
        for kw in skill_info['keywords']:
            try:
                if re.search(kw, content, re.IGNORECASE):
                    skill_match = True
                    break
            except:
                continue
        
        if not skill_match:
            continue
        
        # Check subskills
        subskills_matched = []
        for subskill_name, patterns in skill_info['subskills'].items():
            for pattern in patterns:
                try:
                    if re.search(pattern, content, re.IGNORECASE):
                        subskills_matched.append(subskill_name)
                        break
                except:
                    continue
        
        if skill_match or subskills_matched:
            detected[skill_name] = subskills_matched
    
    return detected

def classify_question_depth(content):
    """Classify if question shows learning, mastery, or struggle"""
    content_lower = content.lower()
    
    # Mastery signals (explaining, teaching, making decisions)
    mastery_words = ['i think', 'we should', 'recommend', 'better to', 'tradeoff', 'strategy']
    if any(word in content_lower for word in mastery_words):
        return "mastery"
    
    # Struggle signals
    struggle_words = ['error', 'not working', 'fail', 'stuck', 'why', 'doesn\'t work', 'not recognized']
    if any(word in content_lower for word in struggle_words):
        return "struggle"
    
    # Learning signals
    learning_words = ['how to', 'what is', 'example', 'tutorial', 'learn', 'guide']
    if any(word in content_lower for word in learning_words):
        return "learning"
    
    # Application (using skill without apparent struggle)
    return "applying"

def build_skill_graph(messages):
    """Build timeline of skill development"""
    skill_timeline = defaultdict(list)
    skill_progress = defaultdict(lambda: {
        'first_seen': None,
        'last_seen': None,
        'message_count': 0,
        'struggle_count': 0,
        'mastery_count': 0,
        'learning_count': 0,
        'subskills': defaultdict(int),
        'questions': []
    })
    
    for msg in messages:
        detected = detect_skills(msg)
        depth = classify_question_depth(msg['content'])
        
        for skill, subskills in detected.items():
            progress = skill_progress[skill]
            progress['message_count'] += 1
            progress['questions'].append({
                'time': msg['datetime'],
                'content': msg['content'][:200],
                'depth': depth
            })
            
            if depth == 'struggle':
                progress['struggle_count'] += 1
            elif depth == 'mastery':
                progress['mastery_count'] += 1
            elif depth == 'learning':
                progress['learning_count'] += 1
            
            for sub in subskills:
                progress['subskills'][sub] += 1
            
            if not progress['first_seen']:
                progress['first_seen'] = msg['datetime']
            progress['last_seen'] = msg['datetime']
            
            skill_timeline[skill].append((msg['datetime'], depth, subskills))
    
    return skill_progress, skill_timeline

def calculate_learning_velocity(skill_progress):
    """Calculate how fast you're learning each skill"""
    velocities = {}
    for skill, data in skill_progress.items():
        if data['first_seen'] and data['last_seen']:
            days = (data['last_seen'] - data['first_seen']).days
            if days > 0:
                msg_per_day = data['message_count'] / days
                mastery_ratio = data['mastery_count'] / max(data['message_count'], 1)
                struggle_ratio = data['struggle_count'] / max(data['message_count'], 1)
                
                velocities[skill] = {
                    'days_active': days,
                    'messages_per_day': msg_per_day,
                    'mastery_ratio': mastery_ratio,
                    'struggle_ratio': struggle_ratio,
                    'velocity_score': (msg_per_day * 5) + (mastery_ratio * 100) - (struggle_ratio * 50)
                }
    return velocities

def suggest_next_topic(skill):
    """Suggest next learning topic based on skill"""
    suggestions = {
        "Rust Programming": "async/await, embedded Rust with embassy",
        "Web3 & Blockchain": "smart contract auditing, MEV strategies",
        "RAG & AI": "hybrid search, reranking, production RAG",
        "System Architecture": "event-driven patterns, CQRS, microservices",
        "DevOps & Tools": "Kubernetes, infrastructure as code",
        "Security": "formal verification, zero-knowledge proofs"
    }
    return suggestions.get(skill, "advanced patterns and real-world projects")

def generate_skill_report(messages):
    """Generate the full skill graph report"""
    print("=" * 70)
    print("YOUR SKILL GRAPH & LEARNING PATHS")
    print("=" * 70)
    
    print(f"\n📊 Analyzing {len(messages)} messages...")
    skill_progress, skill_timeline = build_skill_graph(messages)
    velocities = calculate_learning_velocity(skill_progress)
    
    if not skill_progress:
        print("\n❌ No skills detected! The keyword patterns might need adjustment.")
        print("   Let me show you what's in your data instead...")
        
        # Show sample messages to debug
        print("\n📝 Sample messages from your data:")
        for i, msg in enumerate(messages[:5]):
            print(f"\n{i+1}. {msg['content'][:150]}...")
        return {}, {}
    
    # 1. Current skill levels
    print("\n📊 YOUR CURRENT SKILL LANDSCAPE")
    print("-" * 70)
    
    sorted_skills = sorted(skill_progress.items(), 
                          key=lambda x: x[1]['message_count'], 
                          reverse=True)
    
    for skill, data in sorted_skills:
        mastery_pct = (data['mastery_count'] / max(data['message_count'], 1)) * 100
        struggle_pct = (data['struggle_count'] / max(data['message_count'], 1)) * 100
        learning_pct = (data['learning_count'] / max(data['message_count'], 1)) * 100
        
        # Level indicator
        if mastery_pct > 30:
            level = "🟢 ADVANCED"
        elif mastery_pct > 15:
            level = "🟡 INTERMEDIATE"
        elif data['message_count'] > 5:
            level = "🟠 LEARNING"
        else:
            level = "🔵 BEGINNER"
        
        print(f"\n{level} - {skill}")
        print(f"   Messages: {data['message_count']} | Mastery: {mastery_pct:.0f}% | Struggle: {struggle_pct:.0f}% | Learning: {learning_pct:.0f}%")
        
        # Top subskills
        if data['subskills']:
            top_sub = sorted(data['subskills'].items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"   Focus areas: {', '.join([f'{s}({c})' for s,c in top_sub])}")
    
    # 2. Learning velocity
    if velocities:
        print("\n\n🚀 LEARNING VELOCITY (Fastest to Slowest)")
        print("-" * 70)
        
        sorted_velocity = sorted(velocities.items(), key=lambda x: x[1]['velocity_score'], reverse=True)
        for skill, vel in sorted_velocity[:5]:
            print(f"\n{skill}")
            print(f"   {vel['days_active']} days active | {vel['messages_per_day']:.1f} msgs/day")
            print(f"   Mastery rate: {vel['mastery_ratio']*100:.0f}% | Struggle: {vel['struggle_ratio']*100:.0f}%")
            
            if vel['mastery_ratio'] > 0.3:
                print(f"   ⚡ You're mastering this quickly!")
            elif vel['struggle_ratio'] > 0.4:
                print(f"   🐢 Slower progress - consider revisiting fundamentals")
    
    # 3. Learning path recommendations
    print("\n\n🎯 YOUR LEARNING PATHS")
    print("-" * 70)
    
    # Find skills with high struggle
    struggling = [(s, d) for s, d in skill_progress.items() 
                  if d['struggle_count'] / max(d['message_count'], 1) > 0.4 
                  and d['message_count'] > 3]
    
    if struggling:
        print("\n🔴 SKILLS NEEDING ATTENTION:")
        for skill, data in struggling[:3]:
            print(f"   • {skill}: {data['struggle_count']}/{data['message_count']} messages show struggle")
            print(f"     → Review fundamentals, try smaller steps")
    
    # Find skills ready to advance
    ready = [(s, d) for s, d in skill_progress.items() 
             if d['mastery_count'] / max(d['message_count'], 1) > 0.2
             and d['message_count'] > 5]
    
    if ready:
        print("\n🟢 READY TO LEVEL UP:")
        for skill, data in ready[:3]:
            print(f"   • {skill}: {data['mastery_count']}/{data['message_count']} mastery moments")
            print(f"     → Next: {suggest_next_topic(skill)}")
    
    # 4. Timeline visualization
    print("\n\n📈 SKILL EVOLUTION TIMELINE")
    print("-" * 70)
    
    # Show when you started each skill
    skill_starts = [(skill, data['first_seen']) for skill, data in skill_progress.items() if data['first_seen']]
    skill_starts.sort(key=lambda x: x[1])
    
    print("\nWhen you discovered each skill:")
    for skill, start_date in skill_starts[:10]:
        date_str = start_date.strftime('%b %d')
        print(f"   {date_str}: Started {skill}")
    
    return skill_progress, velocities

# Run it
if __name__ == "__main__":
    messages = load_and_prepare_data()
    skill_progress, velocities = generate_skill_report(messages)