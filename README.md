# 🏥 Medical Knowledge Chatbot

A Streamlit-based medical chatbot that uses Pinecone vector database and OpenAI's GPT models to provide intelligent responses based on medical knowledge from PDF documents with page number references.

## ✨ Features

- **Smart Index Management**: Automatically checks if the knowledge base index exists and creates it only when needed
- **Fast Startup**: Once the index is created, the chatbot starts quickly on subsequent runs
- **Beautiful UI**: Modern Streamlit interface with real-time chat
- **PDF Processing**: Automatically processes medical PDF documents
- **Vector Search**: Uses Pinecone for efficient document retrieval
- **AI-Powered**: Leverages OpenAI's GPT models for intelligent responses
- **Page References**: Shows page numbers and source documents for transparency
- **Configuration Management**: Centralized settings for easy customization

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8 or higher
- Pinecone API key
- OpenAI API key
- Medical PDF documents

### 2. Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   
   **For Local Development:**
   Create a `.env` file in the project root with:
   ```
   PINECONE_API_KEY=your_pinecone_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```
   
   **For Streamlit Cloud:**
   Create a `.streamlit/secrets.toml` file with:
   ```toml
   PINECONE_API_KEY = "your_pinecone_api_key_here"
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```

4. **Add your medical PDF files**:
   Place your medical PDF documents in the project root directory.

### 3. Setup and Run

#### Option A: Automatic Setup (Recommended)
```bash
# Run the Streamlit app - it will handle index creation automatically
streamlit run streamlit_app.py
```

#### Option B: Manual Setup
```bash
# First, create the index
python create_index.py

# Then run the Streamlit app
streamlit run streamlit_app.py
```

#### Option C: Using Scripts (Windows/Linux)
```bash
# Windows
run_chatbot.bat

# Linux/Mac
./run_chatbot.sh
```

## 📁 Project Structure

```
Medical-Chatbot/
├── streamlit_app.py          # Main Streamlit application
├── create_index.py           # Standalone index creation script
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (local development)
├── .streamlit/
│   └── secrets.toml          # Streamlit secrets (local development)
├── run_chatbot.bat           # Windows batch script
├── run_chatbot.sh            # Linux/Mac shell script
├── book.pdf                  # Your medical PDF files
├── src/
│   ├── __init__.py
│   ├── helper.py             # PDF processing and embedding functions
│   ├── prompt.py             # System prompt for the chatbot
│   └── store_index.py        # Pinecone index management
└── templates/                # (if using Flask version)
```

## 🔧 How It Works

### Index Management
- **First Run**: The system checks if a Pinecone index exists
- **Index Creation**: If no index exists, it processes PDFs and creates the index (takes a few minutes)
- **Subsequent Runs**: Uses existing index for fast startup

### Chat Process
1. User asks a medical question
2. System searches the vector database for relevant information
3. Retrieves the most relevant document chunks with page numbers
4. Sends question + context to OpenAI GPT
5. Returns intelligent, context-aware response with page references

## 🎯 Usage

### Local Development
1. **Start the application**: `streamlit run streamlit_app.py`
2. **Check sidebar**: Verify index status and API keys
3. **Create index** (if needed): Click "Create Index" in sidebar
4. **Initialize chatbot**: Click "Initialize Chatbot" when ready
5. **Start chatting**: Ask medical questions in the chat interface
6. **View references**: Each answer includes page numbers and source documents

### Streamlit Cloud Deployment
1. **Push your code** to GitHub
2. **Connect to Streamlit Cloud** and deploy your app
3. **Add secrets** in Streamlit Cloud dashboard:
   - Go to your app settings
   - Add `PINECONE_API_KEY` and `OPENAI_API_KEY`
4. **Deploy and use** the same way as local development

### First-Time Setup
- The first run will take a few minutes to create the index
- Subsequent runs will be much faster
- You can monitor progress in the sidebar

## 🔑 API Keys Setup

### Pinecone API Key
1. Go to [Pinecone Console](https://app.pinecone.io/)
2. Create a new project or use existing
3. Create an index with:
   - Name: `medical-knowledge-base`
   - Dimensions: `384` (for the embedding model used)
   - Metric: `cosine`
4. Copy your API key to `.env` file

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Copy the key to your `.env` file

## 🛠️ Customization

### Configuration Settings
Edit `config.py` to modify:
- **LLM Model**: Change from `gpt-3.5-turbo` to `gpt-4` or other OpenAI models
- **Embedding Model**: Modify `EMBEDDING_MODEL_NAME`
- **Chunk Settings**: Adjust `CHUNK_SIZE` and `CHUNK_OVERLAP`
- **Retrieval Settings**: Change `RETRIEVER_K` for number of chunks retrieved
- **UI Settings**: Customize page title, icon, and layout

### Adding New Documents
1. Add new PDF files to the project root
2. Delete the existing index (if you want to recreate it)
3. Run the index creation process again

### Modifying the System Prompt
Edit `src/prompt.py` to change how the AI responds to questions.

### Changing Embedding Model
Modify the `EMBEDDING_MODEL_NAME` in `config.py`.

### Page Reference Format
The system automatically includes page numbers and source documents in responses. You can customize this by modifying the prompt template in `src/prompt.py`.

## 🐛 Troubleshooting

### Common Issues

1. **"Index not found" error**:
   - Check your Pinecone API key
   - Ensure the index name matches exactly: `medical-knowledge-base`
   - Verify your Pinecone index has 384 dimensions

2. **"No PDF files found"**:
   - Add PDF files to the project root directory
   - Ensure files have `.pdf` extension
   - Check the `PDF_DATA_PATH` in `config.py`

3. **"API key not configured"**:
   - **Local**: Check your `.env` file exists
   - **Streamlit Cloud**: Check your secrets in the dashboard
   - Verify API keys are correct
   - Ensure keys are named `PINECONE_API_KEY` and `OPENAI_API_KEY`

4. **"Prompt template error"**:
   - Ensure you have the latest version of LangChain
   - Check that `src/prompt.py` exports a `PromptTemplate`

5. **Slow index creation**:
   - This is normal for large PDF files
   - The process only happens once
   - Monitor progress in the Streamlit sidebar

6. **Page numbers not showing**:
   - Ensure your PDF files have proper page metadata
   - Check that the retrieval chain includes source documents

### Performance Tips

- **Large PDFs**: Consider splitting very large documents
- **Index Size**: Monitor your Pinecone usage limits
- **Caching**: The system caches embeddings for faster subsequent runs
- **Model Selection**: Use `gpt-3.5-turbo` for faster responses, `gpt-4` for better quality
- **Chunk Size**: Adjust `CHUNK_SIZE` in `config.py` for optimal performance

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📋 Requirements

### Python Packages
- `streamlit` - Web interface
- `langchain` - LLM framework
- `langchain_openai` - OpenAI integration
- `langchain_pinecone` - Pinecone vector store
- `sentence-transformers` - Embedding model
- `pinecone[grpc]` - Pinecone client
- `pypdf` - PDF processing
- `python-dotenv` - Environment variables

### API Requirements
- **Pinecone**: Free tier available (1000 vectors)
- **OpenAI**: Pay-per-use API (GPT-3.5-turbo is very affordable)

---

**Note**: This chatbot is for educational purposes. Always consult healthcare professionals for medical advice.
