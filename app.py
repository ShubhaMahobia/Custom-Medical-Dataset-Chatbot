import streamlit as st
import os
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from src.helper import load_pdf_file, text_split, download_hugging_face_model
from src.prompt import system_prompt
from config import (
    PINECONE_API_KEY, OPENAI_API_KEY, PINECONE_INDEX_NAME,
    LLM_MODEL, LLM_TEMPERATURE, RETRIEVER_K, PDF_DATA_PATH,
    PAGE_TITLE, PAGE_ICON, LAYOUT
)
import time

# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'index_created' not in st.session_state:
    st.session_state.index_created = False
if 'qa_chain' not in st.session_state:
    st.session_state.qa_chain = None

def check_index_exists(index_name):
    """Check if Pinecone index exists"""
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        indexes = pc.list_indexes()
        return index_name in [index.name for index in indexes.indexes]
    except Exception as e:
        st.error(f"Error checking index: {e}")
        return False

def create_index():
    """Create the Pinecone index with documents"""
    try:
        with st.spinner("Creating index... This may take a few minutes."):
            # Load and process documents
            st.info("Loading PDF documents...")
            extracted_data = load_pdf_file(data=PDF_DATA_PATH)
            
            st.info("Splitting text into chunks...")
            text_chunks = text_split(extracted_data=extracted_data)
            
            st.info("Downloading embedding model...")
            embeddings = download_hugging_face_model()
            
            st.info("Creating Pinecone index...")
            
            PineconeVectorStore.from_documents(
                index_name=PINECONE_INDEX_NAME,
                documents=text_chunks,
                embedding=embeddings
            )
            
            st.success("Index created successfully!")
            return True
    except Exception as e:
        st.error(f"Error creating index: {e}")
        return False

def initialize_qa_chain():
    """Initialize the QA chain"""
    try:
        embeddings = download_hugging_face_model()
        
        docsearch = PineconeVectorStore.from_existing_index(
            index_name=PINECONE_INDEX_NAME,
            embedding=embeddings
        )
        
        llm = ChatOpenAI(
            model=LLM_MODEL,
            openai_api_key=OPENAI_API_KEY,
            temperature=LLM_TEMPERATURE
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=docsearch.as_retriever(search_kwargs={'k': RETRIEVER_K}),
            chain_type_kwargs={"prompt": system_prompt}
        )
        
        return qa_chain
    except Exception as e:
        st.error(f"Error initializing QA chain: {e}")
        return None

# Main application
def main():
    st.markdown('<h1 class="main-header">🏥 Medical Knowledge Chatbot</h1>', unsafe_allow_html=True)
    
    # Sidebar for index management
    with st.sidebar:
        st.header("🔧 Index Management")
        
        # Check if index exists
        index_exists = check_index_exists(PINECONE_INDEX_NAME)
        
        if index_exists:
            st.markdown('<div class="status-box success-box">✅ Index already exists</div>', unsafe_allow_html=True)
            
            if not st.session_state.index_created:
                if st.button("🔄 Initialize Chatbot"):
                    with st.spinner("Initializing chatbot..."):
                        qa_chain = initialize_qa_chain()
                        if qa_chain:
                            st.session_state.qa_chain = qa_chain
                            st.session_state.index_created = True
                            st.success("Chatbot initialized successfully!")
                            st.rerun()
        else:
            st.markdown('<div class="status-box warning-box">⚠️ Index not found</div>', unsafe_allow_html=True)
            
            if st.button("📚 Create Index"):
                if create_index():
                    st.session_state.index_created = True
                    st.rerun()
    
    # Main chat interface
    if st.session_state.index_created and st.session_state.qa_chain:
        st.markdown("### 💬 Chat with Medical Knowledge Base")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a medical question..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get bot response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = st.session_state.qa_chain.invoke({"query": prompt})
                        bot_response = response.get('result', 'Sorry, I could not generate a response.')
                        
                        st.markdown(bot_response)
                        
                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": bot_response})
                    except Exception as e:
                        error_msg = f"Error generating response: {e}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
    
    else:
        st.image("RAG.png", caption="RAG Application Architecture", use_column_width=True)
        st.info("To get started, click 'Create Index' on the left menu to begin indexing your documents.")
        # Display environment status
        st.subheader("🔑 Environment Status")
        col1, col2 = st.columns(2)
        
        with col1:
            if PINECONE_API_KEY:
                st.success("✅ Pinecone API Key: Configured")
            else:
                st.error("❌ Pinecone API Key: Missing")
        
        with col2:
            if OPENAI_API_KEY:
                st.success("✅ OpenAI API Key: Configured")
            else:
                st.error("❌ OpenAI API Key: Missing")

if __name__ == "__main__":
    main() 
