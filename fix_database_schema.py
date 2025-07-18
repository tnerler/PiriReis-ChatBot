import sqlite3

def fix_database_schema():
    """Veritabanı şemasını düzelt ve mevcut veriyi koru"""
    
    # Önce mevcut veriyi yedekle
    conn = sqlite3.connect('chatbot_feedback.db')
    cursor = conn.cursor()
    
    print("Mevcut veritabanı durumu kontrol ediliyor...")
    
    # Tablo yapısını kontrol et
    cursor.execute("PRAGMA table_info(feedback)")
    table_info = cursor.fetchall()
    print("Mevcut tablo yapısı:", table_info)
    
    # Mevcut verileri yedekle
    cursor.execute("SELECT * FROM feedback")
    existing_data = cursor.fetchall()
    print(f"Mevcut kayıt sayısı: {len(existing_data)}")
    
    try:
        # Yeni tabloyu oluştur
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                feedback_type TEXT DEFAULT 'pending',  -- Varsayılan değer ekle
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_ip TEXT
            )
        ''')
        
        # Mevcut verileri yeni tabloya aktar
        if existing_data:
            print("Mevcut veriler yeni tabloya aktarılıyor...")
            for row in existing_data:
                # feedback_type NULL ise 'pending' yap
                row_list = list(row)
                if row_list[4] is None:  # feedback_type index 4
                    row_list[4] = 'pending'
                
                cursor.execute('''
                    INSERT INTO feedback_new (id, session_id, question, answer, feedback_type, timestamp, user_ip)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', row_list)
        
        # Eski tabloyu sil, yeni tabloyu rename et
        cursor.execute("DROP TABLE feedback")
        cursor.execute("ALTER TABLE feedback_new RENAME TO feedback")
        
        conn.commit()
        print("✅ Veritabanı başarıyla güncellendi!")
        
        # Sonucu doğrula
        cursor.execute("SELECT COUNT(*) FROM feedback")
        final_count = cursor.fetchone()[0]
        print(f"Final kayıt sayısı: {final_count}")
        
    except Exception as e:
        print(f"❌ Hata: {e}")
        conn.rollback()
        raise
    
    finally:
        conn.close()

def update_init_db_function():
    """init_db fonksiyonunu güncelle"""
    print("\n📝 init_db fonksiyonunu şu şekilde güncelleyin:")
    print("""
def init_db():
    conn = sqlite3.connect('chatbot_feedback.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            feedback_type TEXT DEFAULT 'pending',  -- Varsayılan değer eklendi
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            user_ip TEXT
        )
    ''')

    conn.commit()
    conn.close()
    """)

if __name__ == "__main__":
    print("🔧 Veritabanı şeması düzeltiliyor...")
    fix_database_schema()
    update_init_db_function()
    print("\n✅ Tüm işlemler tamamlandı!")