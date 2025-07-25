#!/usr/bin/env python3
"""
Demo script showing ranking query improvements in action
"""

import json
import re
from typing import List, Dict, Any

class MockDocument:
    """Mock Document class to simulate LangChain Document"""
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata

def extract_ranking_metadata(content: str) -> Dict[str, Any]:
    """Extract ranking and score information from content"""
    metadata = {}
    
    # Taban/Tavan Başarı Sırası (Ranking ranges)
    taban_siralama_match = re.search(r'Taban Başarı Sırası:\s*(\d+)', content)
    tavan_siralama_match = re.search(r'Tavan Başarı Sırası:\s*(\d+)', content)
    
    if taban_siralama_match and tavan_siralama_match:
        metadata['taban_siralama'] = int(taban_siralama_match.group(1))
        metadata['tavan_siralama'] = int(tavan_siralama_match.group(1))
    
    # Taban/Tavan Puanı (Score ranges)
    taban_puan_match = re.search(r'Taban Puanı:\s*([\d.]+)', content)
    tavan_puan_match = re.search(r'Tavan Puanı:\s*([\d.]+)', content)
    
    if taban_puan_match and tavan_puan_match:
        metadata['taban_puan'] = float(taban_puan_match.group(1))
        metadata['tavan_puan'] = float(tavan_puan_match.group(1))
    
    # Program adı
    program_match = re.search(r'Program:\s*(.+?)(?:\n|$)', content)
    if program_match:
        metadata['program'] = program_match.group(1).strip()
    
    # Burs durumu
    burs_match = re.search(r'Burs Durumu:\s*(.+?)(?:\n|$)', content)
    if burs_match:
        metadata['burs_durumu'] = burs_match.group(1).strip()
    
    return metadata

def detect_ranking_query(query: str) -> tuple:
    """Detect if query is ranking-based and extract ranking number"""
    ranking_keywords = ['sıralama', 'ranking', 'siralama', 'yerleştirme', 'sıralam']
    has_ranking_keyword = any(keyword in query.lower() for keyword in ranking_keywords)
    
    extracted_ranking = None
    
    if has_ranking_keyword:
        # Normal numbers
        ranking_numbers = re.findall(r'\b(\d{1,6})\b', query)
        for num_str in ranking_numbers:
            num = int(num_str)
            if 1000 <= num <= 500000:
                extracted_ranking = num
                break
        
        # "bin" format (150bin, 85 bin)
        if not extracted_ranking:
            bin_matches = re.findall(r'(\d{1,3})\s*bin\b', query.lower())
            for match in bin_matches:
                num = int(match) * 1000
                if 1000 <= num <= 500000:
                    extracted_ranking = num
                    break
        
        # "k" format (150k)
        if not extracted_ranking:
            k_matches = re.findall(r'(\d{1,3})k\b', query.lower())
            for match in k_matches:
                num = int(match) * 1000
                if 1000 <= num <= 500000:
                    extracted_ranking = num
                    break
    
    return has_ranking_keyword, extracted_ranking

def filter_documents_by_ranking(docs: List[MockDocument], user_ranking: int) -> List[MockDocument]:
    """Filter documents to show only those applicable to user's ranking"""
    if not user_ranking:
        return docs
    
    applicable_docs = []
    for doc in docs:
        taban = doc.metadata.get('taban_siralama')
        tavan = doc.metadata.get('tavan_siralama')
        
        if taban and tavan:
            # Check if user's ranking falls within this program's range
            if tavan <= user_ranking <= taban:
                applicable_docs.append(doc)
        else:
            # Include non-ranking documents
            applicable_docs.append(doc)
    
    return applicable_docs

def load_sample_documents() -> List[MockDocument]:
    """Load sample documents from main_data.json"""
    docs = []
    
    try:
        with open("get_data/main_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Process a few ranking documents for demo
        for i, item in enumerate(data):
            if isinstance(item, dict) and 'type' in item:
                if 'Sıralamaları ve Puanları' in item.get('type', ''):
                    content = ''.join(item['context']) if isinstance(item.get('context'), list) else item.get('context', '')
                    metadata = extract_ranking_metadata(content)
                    metadata.update({
                        'type': item['type'],
                        'source': 'main_data.json',
                        'is_ranking_doc': True
                    })
                    
                    # Enhanced content with ranking explanation
                    enhanced_content = f"{item['type']}: {content}"
                    if 'taban_siralama' in metadata and 'tavan_siralama' in metadata:
                        enhanced_content += f"\n\nBu bölüme {metadata['tavan_siralama']} ile {metadata['taban_siralama']} arasındaki sıralamaya sahip öğrenciler girebilir."
                    
                    docs.append(MockDocument(enhanced_content, metadata))
                    
                    # Limit to first 10 for demo
                    if len(docs) >= 10:
                        break
    
    except Exception as e:
        print(f"Error loading documents: {e}")
    
    return docs

def demonstrate_ranking_query(query: str, docs: List[MockDocument]) -> None:
    """Demonstrate how the improved system handles a ranking query"""
    print(f"\n🔍 User Query: '{query}'")
    print("=" * 50)
    
    # Step 1: Detect ranking query
    is_ranking_query, user_ranking = detect_ranking_query(query)
    print(f"📊 Query Analysis:")
    print(f"   - Is ranking query: {is_ranking_query}")
    print(f"   - Extracted ranking: {user_ranking}")
    
    if not is_ranking_query:
        print("   → Using standard retrieval (no ranking-specific processing)")
        return
    
    # Step 2: Filter documents by ranking
    if user_ranking:
        applicable_docs = filter_documents_by_ranking(docs, user_ranking)
        print(f"\n✅ Filtering Results:")
        print(f"   - Total documents: {len(docs)}")
        print(f"   - Applicable documents: {len(applicable_docs)}")
        
        # Step 3: Show applicable programs
        if applicable_docs:
            print(f"\n🎯 Programs available for ranking {user_ranking}:")
            for i, doc in enumerate(applicable_docs[:5], 1):  # Show top 5
                program = doc.metadata.get('program', 'Unknown Program')
                burs = doc.metadata.get('burs_durumu', 'Unknown')
                tavan = doc.metadata.get('tavan_siralama', 'N/A')
                taban = doc.metadata.get('taban_siralama', 'N/A')
                
                print(f"   {i}. {program}")
                print(f"      Burs: {burs}")
                print(f"      Sıralama Aralığı: {tavan} - {taban}")
                print()
        else:
            print(f"\n❌ No programs found for ranking {user_ranking}")
            print("   → User should consider lower-ranking programs or different scholarship types")

def main():
    """Run ranking query demonstration"""
    print("🎓 Piri Reis University Ranking Query Demo")
    print("=" * 60)
    
    # Load sample documents
    print("📚 Loading ranking documents...")
    docs = load_sample_documents()
    print(f"✅ Loaded {len(docs)} ranking documents")
    
    # Test queries
    test_queries = [
        "Sıralamam 60000, hangi bölümlere girebilirim?",
        "150000 sıralama ile kabul olan bölümler",
        "Sıralamam 50000, bu sıralama ile hangi bölümler uygun?",
        "Üniversite hakkında genel bilgi"  # Non-ranking query
    ]
    
    for query in test_queries:
        demonstrate_ranking_query(query, docs)
    
    print("\n" + "=" * 60)
    print("✨ Demo completed! The improved system can now:")
    print("   • Detect ranking-based queries automatically")
    print("   • Extract numerical rankings from user questions")
    print("   • Filter documents to show only applicable programs")
    print("   • Provide detailed ranking ranges for each program")
    print("   • Handle different scholarship types (Tam Burslu, %50 Burslu, Ücretli)")

if __name__ == "__main__":
    main()