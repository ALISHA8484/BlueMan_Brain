import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from config import (CHROMA_DB_PATH, DOCUMENT_DIR)

PERSIAN_EMBEDDING_MODEL = "heydariAI/persian-embeddings"
VECTOR_STORE_PATH = CHROMA_DB_PATH
DOC_DIRECTORY = DOCUMENT_DIR

def load_documents(directory_path):
    print(f"Loading documents from: {directory_path}")

    loader = DirectoryLoader(
        directory_path, 
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={'encoding': 'utf-8'}
    )
    documents = loader.load()
    print(f"Loaded {len(documents)} document(s).")
    return documents

def chunk_documents(documents):
    print("Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  
        chunk_overlap=20
    )
    chunked_docs = text_splitter.split_documents(documents)
    print(f"Created {len(chunked_docs)} chunks.")
    return chunked_docs

def get_embedding_model():

    print(f"Initializing embedding model: {PERSIAN_EMBEDDING_MODEL}")
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    
    embeddings = HuggingFaceEmbeddings(
        model_name=PERSIAN_EMBEDDING_MODEL,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    print("Embedding model initialized.")
    return embeddings

def create_and_store_embeddings(chunks, embeddings):

    print("Creating and storing embeddings in ChromaDB...")
    
    if not os.path.exists(VECTOR_STORE_PATH):
        os.makedirs(VECTOR_STORE_PATH)

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_STORE_PATH
    )
    print(f"Embeddings stored successfully in: {VECTOR_STORE_PATH}")
    return vector_store

def query_vector_store(query: str, embeddings):
    print(f"Querying vector store with: '{query}'")
    
    if not os.path.exists(VECTOR_STORE_PATH):
        print(f"Error: Vector store not found at {VECTOR_STORE_PATH}")
        print("Please run the ingestion process first by calling run_ingestion()")
        return None

    db = Chroma(
        persist_directory=VECTOR_STORE_PATH,
        embedding_function=embeddings
    )
    
    results = db.similarity_search(query, k=3)
    
    if not results:
        print("No relevant context found.")
        return None
        
    print(f"Found {len(results)} relevant chunks.")
    
    context = "\n\n---\n\n".join([doc.page_content for doc in results])
    return context

def run_ingestion():
    """
    این تابع کل فرآیند خواندن فایل‌ها، خرد کردن و ذخیره در دیتابیس را اجرا می‌کند.
    شما فقط یک بار به اجرای این تابع نیاز دارید.
    """
    print("--- 1. Starting Data Ingestion Process ---")
    docs = load_documents(DOC_DIRECTORY)
    if not docs:
        print("No documents found in directory. Exiting.")
        return
        
    chunks = chunk_documents(docs)
    embeddings = get_embedding_model()
    create_and_store_embeddings(chunks, embeddings)
    print("--- Data Ingestion Complete ---")

def run_query_test():
    """
    این تابع یک نمونه پرسش را برای تست بازیابی اطلاعات (Retrieval) اجرا می‌کند.
    """
    print("\n--- 2. Starting Query Test Process ---")
    
    embeddings = get_embedding_model()
    
    test_query = "جوایز لیگ چالش صنعتی پیشرفته چقدر است؟"
    
    context = query_vector_store(test_query, embeddings)
    
    if context:
        print("\n--- Retrieved Context ---")
        print(context)
        print("-------------------------")

if __name__ == "__main__":
    run_ingestion() 
    run_query_test()
