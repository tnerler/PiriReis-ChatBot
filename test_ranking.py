#!/usr/bin/env python3
"""
Test script for ranking query improvements
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from load_docs import load_docs, extract_ranking_metadata

def test_load_docs():
    """Test the enhanced load_docs function"""
    print("Testing enhanced load_docs function...")
    
    try:
        docs = load_docs()
        print(f"✅ Successfully loaded {len(docs)} documents")
        
        # Count ranking documents
        ranking_docs = [doc for doc in docs if doc.metadata.get('is_ranking_doc', False)]
        print(f"✅ Found {len(ranking_docs)} ranking documents")
        
        # Count generated documents
        generated_docs = [doc for doc in docs if doc.metadata.get('source') == 'generated']
        print(f"✅ Found {len(generated_docs)} generated ranking query documents")
        
        # Test ranking metadata extraction
        if ranking_docs:
            sample_doc = ranking_docs[0]
            print(f"\n📋 Sample ranking document:")
            print(f"   Type: {sample_doc.metadata.get('type', 'N/A')}")
            print(f"   Program: {sample_doc.metadata.get('program', 'N/A')}")
            print(f"   Burs: {sample_doc.metadata.get('burs_durumu', 'N/A')}")
            print(f"   Sıralama: {sample_doc.metadata.get('tavan_siralama', 'N/A')} - {sample_doc.metadata.get('taban_siralama', 'N/A')}")
            print(f"   Puan: {sample_doc.metadata.get('tavan_puan', 'N/A')} - {sample_doc.metadata.get('taban_puan', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in load_docs: {e}")
        return False

def test_ranking_metadata():
    """Test ranking metadata extraction"""
    print("\nTesting ranking metadata extraction...")
    
    sample_content = """Üniversite Adı: Piri Reis Üniversitesi
Yıl: 2024-2025
Fakülte: DENİZCİLİK FAKÜLTESİ
Program: Deniz Ulaştırma İşletme Mühendisliği (İngilizce)
Puan Türü: SAY
Burs Durumu: Tam Burslu
Kontenjan: 16
Taban Puanı: 425.23214
Tavan Puanı: 433.38512
Taban Başarı Sırası: 58422
Tavan Başarı Sırası: 51496"""

    metadata = extract_ranking_metadata(sample_content)
    
    expected_fields = ['taban_siralama', 'tavan_siralama', 'taban_puan', 'tavan_puan', 'program', 'burs_durumu', 'fakulte']
    
    success = True
    for field in expected_fields:
        if field in metadata:
            print(f"✅ {field}: {metadata[field]}")
        else:
            print(f"❌ Missing field: {field}")
            success = False
    
    return success

def test_ranking_query_detection():
    """Test ranking query detection"""
    print("\nTesting ranking query detection...")
    
    # Import the function
    try:
        from retrieve_and_generate import detect_ranking_query
        
        test_queries = [
            ("Sıralamam 150000, bu bölüme girebilir miyim?", True, 150000),
            ("Hangi bölümlere girebilirim? Sıralamam 75000", True, 75000),
            ("Üniversite hakkında bilgi", False, None),
            ("150000 sıralama ile hangi bölümler uygun?", True, 150000),
            ("Bölümler listesi", False, None)
        ]
        
        success = True
        for query, expected_is_ranking, expected_ranking in test_queries:
            is_ranking, extracted_ranking = detect_ranking_query(query)
            
            if is_ranking == expected_is_ranking and extracted_ranking == expected_ranking:
                print(f"✅ '{query}' -> ranking: {is_ranking}, number: {extracted_ranking}")
            else:
                print(f"❌ '{query}' -> Expected: ({expected_is_ranking}, {expected_ranking}), Got: ({is_ranking}, {extracted_ranking})")
                success = False
        
        return success
    
    except ImportError as e:
        print(f"❌ Could not import detect_ranking_query: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Ranking Query Improvement Tests\n")
    
    results = []
    
    # Test 1: Load docs with ranking metadata
    results.append(test_load_docs())
    
    # Test 2: Ranking metadata extraction
    results.append(test_ranking_metadata())
    
    # Test 3: Ranking query detection
    results.append(test_ranking_query_detection())
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())