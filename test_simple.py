#!/usr/bin/env python3
"""
Simple test without external dependencies
"""

import json
import re

def extract_ranking_metadata(content):
    """
    İçerikten sıralama ve puan bilgilerini çıkarır.
    """
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
    
    # Fakülte
    fakulte_match = re.search(r'Fakülte:\s*(.+?)(?:\n|$)', content)
    if fakulte_match:
        metadata['fakulte'] = fakulte_match.group(1).strip()
    
    return metadata

def detect_ranking_query(query):
    """
    Sorgunun sıralama tabanlı olup olmadığını tespit eder ve sıralamayı çıkarır.
    """
    ranking_keywords = ['sıralama', 'sıralama', 'ranking', 'siralama', 'yerleştirme']
    has_ranking_keyword = any(keyword in query.lower() for keyword in ranking_keywords)
    
    # Sayısal sıralama değeri çıkar
    ranking_numbers = re.findall(r'\b(\d{1,6})\b', query)
    extracted_ranking = None
    
    if ranking_numbers and has_ranking_keyword:
        # En makul sıralama değerini seç (genellikle en büyük sayı)
        for num_str in ranking_numbers:
            num = int(num_str)
            if 1000 <= num <= 500000:  # Makul sıralama aralığı
                extracted_ranking = num
                break
    
    return has_ranking_keyword, extracted_ranking

def test_metadata_extraction():
    """Test ranking metadata extraction"""
    print("Testing ranking metadata extraction...")
    
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
    
    print("Extracted metadata:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")
    
    # Verify expected fields
    expected = {
        'taban_siralama': 58422,
        'tavan_siralama': 51496,
        'taban_puan': 425.23214,
        'tavan_puan': 433.38512,
        'program': 'Deniz Ulaştırma İşletme Mühendisliği (İngilizce)',
        'burs_durumu': 'Tam Burslu',
        'fakulte': 'DENİZCİLİK FAKÜLTESİ'
    }
    
    success = True
    for key, expected_value in expected.items():
        if key in metadata and metadata[key] == expected_value:
            print(f"✅ {key}: {metadata[key]}")
        else:
            print(f"❌ {key}: expected {expected_value}, got {metadata.get(key, 'N/A')}")
            success = False
    
    return success

def test_query_detection():
    """Test ranking query detection"""
    print("\nTesting ranking query detection...")
    
    test_queries = [
        ("Sıralamam 150000, bu bölüme girebilir miyim?", True, 150000),
        ("Hangi bölümlere girebilirim? Sıralamam 75000", True, 75000),
        ("Üniversite hakkında bilgi", False, None),
        ("150000 sıralama ile hangi bölümler uygun?", True, 150000),
        ("Bölümler listesi", False, None),
        ("sıralaması 25000 olan öğrenci", True, 25000)
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

def test_data_analysis():
    """Analyze the main_data.json for ranking documents"""
    print("\nAnalyzing main_data.json for ranking documents...")
    
    try:
        with open("get_data/main_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        ranking_docs = 0
        sample_extracted = []
        
        for i, item in enumerate(data):
            if isinstance(item, dict) and 'type' in item:
                if 'Sıralamaları ve Puanları' in item['type']:
                    ranking_docs += 1
                    
                    if 'context' in item and len(sample_extracted) < 3:
                        content = ''.join(item['context']) if isinstance(item['context'], list) else item['context']
                        metadata = extract_ranking_metadata(content)
                        sample_extracted.append({
                            'type': item['type'],
                            'metadata': metadata
                        })
        
        print(f"✅ Found {ranking_docs} ranking documents in main_data.json")
        
        print("\nSample extracted metadata:")
        for i, sample in enumerate(sample_extracted):
            print(f"  Sample {i+1}: {sample['type']}")
            for key, value in sample['metadata'].items():
                print(f"    {key}: {value}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing data: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Simple Ranking Improvement Tests\n")
    
    results = []
    
    # Test 1: Metadata extraction
    results.append(test_metadata_extraction())
    
    # Test 2: Query detection
    results.append(test_query_detection())
    
    # Test 3: Data analysis
    results.append(test_data_analysis())
    
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