import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from openai_clients import embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os 
def build_store(docs, persist_path='vector_db') : 
    """
    ### Aciklama:

    Belgeleri alır, eğer vektör veritabanı kayıtlıysa onu yükler.
    Kayıtlı değilse yeni FAISS index oluşturur, embedding hesaplar ve kaydeder.

    ### Degiskenler:

    **embedding_dim**: Bu değişken, embedding modelimizin vektör boyutunu öğrenmek için kullanılır. 
    İçine yazılan metin önemli değildir; sadece vektörün kaç boyutlu olduğunu tespit etmek amacıyla kullanılır. 
    **Suan ki embed modelimizin dimension'i 1536 ---> embedding_dim == 1536**

    **index**: Burada FAISS indexi oluşturuluyor.
    IndexFlatIP yapısı, vektörler arasında benzerliği inner product (yani dot product veya cosine similarity) kullanarak hesaplar.
    Indexin boyutu ise embedding vektörünün dimension sayısına eşittir.

    **vector_store**:   [

    *embedding_function*: Vektörleri hesaplamak için kullanılacak embedding modeli.

    *index*: FAISS’in IndexFlatIP tipi indexi burada kullanılıyor.

    *docstore*: Vektörlerle ilişkilendirilen gerçek doküman içerikleri bellekte (RAM) saklanacak.

    *index_to_docstore_id*: Her vektörün hangi dokümana ait olduğunu gösteren bir eşleme (başlangıçta boş olacak).

    ]
    """
    if os.path.exists(persist_path):
        print(f"[i] Kayıtlı FAISS veritabanı bulundu, yükleniyor: {persist_path}")
        vector_store = FAISS.load_local(persist_path, embeddings, allow_dangerous_deserialization=True)
    else: 

        # Yeni FAISS index oluşturuluyor
        print("[i] FAISS veritabanı bulunamadı, yeni oluşturuluyor...")
        embedding_dim = len(embeddings.embed_query("deneme 123"))
        index = faiss.IndexFlatIP(embedding_dim)

        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )
    
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)
        
        vector_store.add_documents(all_splits)
        vector_store.save_local(persist_path)
    return vector_store