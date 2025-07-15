from pinecone import Pinecone, ServerlessSpec
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, PDF_DATA_PATH
from src.helper import load_pdf_file, text_split, download_hugging_face_model
from langchain_pinecone import PineconeVectorStore

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

def check_index_exists(index_name):
    """Check if Pinecone index exists"""
    try:
        indexes = pc.list_indexes()
        return index_name in [index.name for index in indexes.indexes]
    except Exception as e:
        print(f"Error checking index: {e}")
        return False

def check_index_has_vectors(index_name):
    """Check if the index has any vectors"""
    try:
        index = pc.Index(index_name)
        stats = index.describe_index_stats()
        total_vectors = stats.get("total_vector_count", 0)
        return total_vectors > 0
    except Exception as e:
        print(f"Error checking vector presence: {e}")
        return False

def create_index_if_not_exists():
    """Only create index and upload if not already present or empty"""
    if check_index_exists(PINECONE_INDEX_NAME):
        print(f"✅ Index '{PINECONE_INDEX_NAME}' already exists!")
        if check_index_has_vectors(PINECONE_INDEX_NAME):
            print(f"✅ Index '{PINECONE_INDEX_NAME}' already has vector data.")
            return True
        else:
            print(f"⚠️ Index exists but has no vectors. Proceeding to add data...")
    else:
        print("📚 Creating new index...")

    try:
        # Load and process documents
        print("Loading PDF documents...")
        extracted_data = load_pdf_file(data=PDF_DATA_PATH)

        print("Splitting text into chunks...")
        text_chunks = text_split(extracted_data=extracted_data)

        print("Downloading embedding model...")
        embeddings = download_hugging_face_model()

        print("Uploading documents to Pinecone index...")
        PineconeVectorStore.from_documents(
            index_name=PINECONE_INDEX_NAME,
            documents=text_chunks,
            embedding=embeddings
        )

        print(f"✅ Index '{PINECONE_INDEX_NAME}' is now populated!")
        return True

    except Exception as e:
        print(f"❌ Error creating index or uploading documents: {e}")
        return False

def get_vector_store():
    """Get the vector store for querying"""
    try:
        embeddings = download_hugging_face_model()

        docsearch = PineconeVectorStore.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings
        )
        return docsearch
    except Exception as e:
        print(f"❌ Error getting vector store: {e}")
        return None

if __name__ == "__main__":
    # Create and verify index
    if create_index_if_not_exists():
        print("🎉 Vector store is ready to use!")
    else:
        print("❌ Index setup failed.")
