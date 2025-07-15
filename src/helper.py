
from langchain_community.document_loaders import PyPDFLoader,DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EMBEDDING_MODEL_NAME, CHUNK_SIZE, CHUNK_OVERLAP, PDF_DATA_PATH


def load_pdf_file(data=PDF_DATA_PATH):
    """Load PDF files from the specified directory"""
    loader = DirectoryLoader(data, glob="*.pdf", loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents


def text_split(extracted_data):
    """Split documents into chunks for processing"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, 
        chunk_overlap=CHUNK_OVERLAP
    )
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks


def download_hugging_face_model():
    """Download and return the HuggingFace embedding model"""
    embeddings = HuggingFaceBgeEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    return embeddings