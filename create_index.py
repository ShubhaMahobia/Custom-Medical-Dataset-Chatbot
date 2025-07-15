"""
Standalone script to create Pinecone index for medical knowledge base.
Run this script once to set up the index, then use the Streamlit app.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.vector_store import create_index_if_not_exists

def main():
    print("🏥 Medical Knowledge Base Index Creator")
    print("=" * 50)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create a .env file with your API keys:")
        print("PINECONE_API_KEY=your_pinecone_api_key")
        print("OPENAI_API_KEY=your_openai_api_key")
        return
    
    # Check if PDF files exist
    pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
    if not pdf_files:
        print("❌ No PDF files found in the current directory!")
        print("Please add your medical PDF files to this directory.")
        return
    
    print(f"📄 Found {len(pdf_files)} PDF file(s): {', '.join(pdf_files)}")
    print()
    
    # Create index
    if create_index_if_not_exists():
        print()
        print("🎉 Setup complete! You can now run the Streamlit app:")
        print("streamlit run app.py")
    else:
        print()
        print("❌ Setup failed. Please check your API keys and try again.")

if __name__ == "__main__":
    main() 