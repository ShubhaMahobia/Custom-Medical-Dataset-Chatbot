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
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
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
            chain_type_kwargs={"prompt_template": system_prompt},
            return_source_documents=True
        )
        
        return qa_chain
    except Exception as e:
        st.error(f"Error initializing QA chain: {e}")
        return None

def format_response_with_sources(response):
    """Format response to include page references"""
    result = response.get('result', 'Sorry, I could not generate a response.')
    
    # Add source documents if available
    if 'source_documents' in response and response['source_documents']:
        sources = response['source_documents']
        page_refs = []
        
        for doc in sources:
            page = doc.metadata.get('page')
            source = doc.metadata.get('source', 'Unknown source')
            
            if page is not None:
                page_refs.append(f"{source} (page {page})")
            else:
                page_refs.append(source)
        
        if page_refs:
            # Remove duplicates while preserving order
            unique_refs = list(dict.fromkeys(page_refs))
            result += f"\n\n**📚 Sources:**\n" + ", ".join(unique_refs)
    
    return result

# Main application
def main():
    st.markdown('<h1 class="main-header">🏥 Medical Knowledge Chatbot</h1>', unsafe_allow_html=True)
    
    # Sidebar for index management
    with st.sidebar:
        st.header("🔧 Index Management")
        
        # Check API keys first
        if not PINECONE_API_KEY:
            st.markdown('<div class="status-box error-box">❌ Pinecone API Key: Missing</div>', unsafe_allow_html=True)
            st.info("Add your Pinecone API key to Streamlit secrets or .env file")
            return
        
        if not OPENAI_API_KEY:
            st.markdown('<div class="status-box error-box">❌ OpenAI API Key: Missing</div>', unsafe_allow_html=True)
            st.info("Add your OpenAI API key to Streamlit secrets or .env file")
            return
        
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
                        bot_response = format_response_with_sources(response)
                        
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
        st.markdown("""
        <div class="status-box info-box">
            <h3>Welcome to the Medical Knowledge Chatbot!</h3>
            <p>To get started:</p>
            <ol>
                <li>Make sure you have your Pinecone API key configured</li>
                <li>Make sure you have your OpenAI API key configured</li>
                <li>If the index doesn't exist, click "Create Index" in the sidebar</li>
                <li>Once the index is ready, click "Initialize Chatbot"</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
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
        
        # Instructions for Streamlit Cloud
        st.subheader("🌐 Streamlit Cloud Setup")
        st.markdown("""
        If you're hosting on Streamlit Cloud:
        1. Go to your app settings in Streamlit Cloud
        2. Add these secrets in the 'Secrets' section:
        ```
        PINECONE_API_KEY = "your_pinecone_api_key"
        OPENAI_API_KEY = "your_openai_api_key"
        ```
        3. Deploy your app
        """)

if __name__ == "__main__":
    main() 