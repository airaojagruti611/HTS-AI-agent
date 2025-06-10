"""
HTS AI Agent - Frontend with REAL LLM Integration
Uses actual LLM to generate responses from PDF content
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Page configuration
st.set_page_config(
    page_title="TariffBot - HTS AI Agent",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1f4e79;
    text-align: center;
    margin-bottom: 2rem;
}
.sub-header {
    font-size: 1.2rem;
    color: #666;
    text-align: center;
    margin-bottom: 3rem;
}
.response-box {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 10px;
    margin: 1rem 0;
    border-left: 4px solid #1f4e79;
}
.api-key-box {
    background-color: #fff3cd;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #ffc107;
    margin: 1rem 0;
}
.success-box {
    background-color: #d4edda;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #28a745;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_bot():
    """Initialize TariffBot with real LLM (cached)"""
    try:
        # Import the real LLM agent
        sys.path.append(str(Path(__file__).parent.parent))
        from agent_real_llm import create_tariff_bot
        from database import setup_database
        
        # Setup database if needed
        if not os.path.exists("data/hts_data.db"):
            with st.spinner("Setting up database for first time use..."):
                setup_database()
        
        # Initialize bot with real LLM
        with st.spinner("Initializing TariffBot with LLM..."):
            bot = create_tariff_bot()
        
        return bot, None
    except Exception as e:
        return None, str(e)

def check_openai_setup():
    """Check if OpenAI is properly configured"""
    api_key = os.getenv('OPENAI_API_KEY')
    return api_key is not None

def main():
    # Header
    st.markdown('<h1 class="main-header">🚢 TariffBot</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Intelligent Assistant with Real LLM Responses</p>', unsafe_allow_html=True)
    
    # Check OpenAI setup
    has_openai = check_openai_setup()
    
    if has_openai:
        st.markdown('<div class="success-box">✅ <strong>OpenAI API Key Detected</strong> - Full LLM functionality enabled</div>', unsafe_allow_html=True)
    else:
        st.markdown('''
        <div class="api-key-box">
        ⚠️ <strong>OpenAI API Key Not Found</strong><br>
        For full LLM functionality, set your OpenAI API key as an environment variable:<br>
        <code>export OPENAI_API_KEY="your-api-key-here"</code><br>
        The system will use basic text extraction as fallback.
        </div>
        ''', unsafe_allow_html=True)
    
    # Initialize bot
    bot, error = initialize_bot()
    if error:
        st.error(f"Failed to initialize TariffBot: {error}")
        st.stop()
    
    # Sidebar
    st.sidebar.title("Navigation")
    mode = st.sidebar.selectbox(
        "Choose Mode",
        ["💬 Chat with TariffBot", "📚 Sample Questions", "🔧 Setup Guide", "ℹ️ About"]
    )
    
    if mode == "💬 Chat with TariffBot":
        chat_interface(bot, has_openai)
    elif mode == "📚 Sample Questions":
        sample_questions_interface(bot, has_openai)
    elif mode == "🔧 Setup Guide":
        setup_guide_interface()
    elif mode == "ℹ️ About":
        about_interface()

def chat_interface(bot, has_openai):
    """Main chat interface with real LLM responses"""
    st.header("Chat with TariffBot")
    
    if has_openai:
        st.success("🤖 Using OpenAI LLM for intelligent responses from HTS General Notes")
    else:
        st.warning("📄 Using basic text extraction (set OPENAI_API_KEY for full LLM functionality)")
    
    st.write("Ask me anything about HTS tariffs, trade agreements, or duty calculations!")
    
    # Chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant":
                st.markdown(f'<div class="response-box">{message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about HTS codes, tariffs, or trade agreements..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get bot response using real LLM
        with st.chat_message("assistant"):
            with st.spinner("Generating response with LLM..." if has_openai else "Processing with text extraction..."):
                try:
                    response = bot.query(prompt)
                except Exception as e:
                    response = f"I encountered an error processing your question: {str(e)}"
                
            st.markdown(f'<div class="response-box">{response}</div>', unsafe_allow_html=True)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})

def sample_questions_interface(bot, has_openai):
    """Sample questions interface with real LLM"""
    st.header("Sample Questions")
    
    if has_openai:
        st.success("🤖 These questions will be answered using OpenAI LLM with HTS General Notes content")
    else:
        st.warning("📄 These questions will be answered using basic text extraction")
    
    st.write("Try these sample questions to see TariffBot's LLM capabilities:")
    
    sample_questions = [
        {
            "question": "What is the United States-Israel Free Trade Agreement?",
            "category": "Trade Agreements",
            "description": "LLM will analyze HTS General Notes to explain the 1985 FTA"
        },
        {
            "question": "Can a product that exceeds its tariff-rate quota still qualify for duty-free entry under GSP?",
            "category": "Trade Policy",
            "description": "LLM will explain the relationship between TRQs and GSP from official documentation"
        },
        {
            "question": "How is classification determined for an imported item used in manufacturing?",
            "category": "Classification",
            "description": "LLM will extract and explain HTS classification rules from the PDF"
        },
        {
            "question": "What's the HTS code for donkeys?",
            "category": "HTS Search",
            "description": "Database search for specific animal classifications"
        },
        {
            "question": "Calculate tariff for HTS code 0101.30.00.00 with cost $10,000",
            "category": "Tariff Calculation",
            "description": "Real tariff calculation with duty rate parsing"
        }
    ]
    
    for i, item in enumerate(sample_questions):
        with st.expander(f"{item['category']}: {item['question']}"):
            st.write(f"**How it works:** {item['description']}")
            
            if st.button(f"Ask this question", key=f"sample_{i}"):
                # Get response using real LLM
                with st.spinner("Generating LLM response..." if has_openai else "Processing..."):
                    try:
                        response = bot.query(item['question'])
                    except Exception as e:
                        response = f"Error: {str(e)}"
                
                st.markdown(f'<div class="response-box">{response}</div>', unsafe_allow_html=True)
                
                # Show method used
                if has_openai:
                    st.info("✅ Response generated using OpenAI LLM with HTS General Notes content")
                else:
                    st.info("📄 Response generated using basic text extraction")

def setup_guide_interface():
    """Setup guide for OpenAI integration"""
    st.header("🔧 Setup Guide for Full LLM Functionality")
    
    st.markdown("""
    ### Step 1: Get OpenAI API Key
    
    1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
    2. Sign in or create an account
    3. Click "Create new secret key"
    4. Copy your API key (starts with `sk-`)
    
    ### Step 2: Set Environment Variable
    
    **On Windows:**
    ```bash
    set OPENAI_API_KEY=your-api-key-here
    ```
    
    **On Mac/Linux:**
    ```bash
    export OPENAI_API_KEY="your-api-key-here"
    ```
    
    **Or create a .env file:**
    ```
    OPENAI_API_KEY=your-api-key-here
    ```
    
    ### Step 3: Restart Streamlit
    
    ```bash
    streamlit run frontend/app.py
    ```
    
    ### What You Get with OpenAI:
    
    - 🤖 **Real LLM Responses**: Generated from actual HTS General Notes content
    - 📚 **Intelligent Analysis**: Deep understanding of trade regulations
    - 🎯 **Accurate Answers**: Based on official documentation
    - 💬 **Natural Language**: Professional, comprehensive responses
    
    ### Without OpenAI (Fallback):
    
    - 📄 **Text Extraction**: Basic PDF text parsing
    - 🔍 **Keyword Matching**: Simple pattern-based responses
    - ⚡ **Fast Processing**: No API calls required
    - 🆓 **Free to Use**: No API costs
    """)
    
    # Current status
    has_openai = check_openai_setup()
    
    if has_openai:
        st.success("✅ OpenAI API Key is configured! You're getting full LLM functionality.")
    else:
        st.warning("⚠️ OpenAI API Key not found. Follow the steps above to enable full LLM functionality.")

def about_interface():
    """About interface with LLM information"""
    st.header("About TariffBot with Real LLM")
    
    st.markdown("""
    **TariffBot** uses real Large Language Models (LLMs) to generate intelligent responses from actual HTS General Notes content.
    
    ### 🤖 LLM Integration:
    - **OpenAI GPT**: Primary LLM for generating responses
    - **Vector Search**: FAISS for finding relevant document sections
    - **RAG Pipeline**: Retrieval-Augmented Generation from PDF content
    - **Fallback System**: Text extraction when LLM unavailable
    
    ### 📚 How It Works:
    
    1. **Document Processing**: HTS General Notes PDF is split into chunks
    2. **Vector Embeddings**: Text chunks are converted to embeddings
    3. **Similarity Search**: Relevant chunks are found for each question
    4. **LLM Generation**: OpenAI generates responses from relevant content
    5. **Professional Output**: Formatted, comprehensive answers
    
    ### 🎯 Response Quality:
    
    **With OpenAI LLM:**
    - Intelligent analysis of HTS documentation
    - Professional trade terminology
    - Comprehensive, detailed explanations
    - Context-aware responses
    
    **Without LLM (Fallback):**
    - Basic text extraction from PDF
    - Pattern-based keyword matching
    - Simple but functional responses
    - No API costs required
    
    ### 💡 Example LLM Process:
    
    **Question:** "What is the United States-Israel Free Trade Agreement?"
    
    **Step 1:** Search HTS General Notes for "Israel", "Free Trade Agreement"
    **Step 2:** Find relevant document sections about US-Israel FTA
    **Step 3:** Send context to OpenAI LLM with professional prompt
    **Step 4:** Generate comprehensive response based on official documentation
    **Step 5:** Return formatted, professional answer
    
    ### 🔧 Technical Stack:
    - **LangChain**: LLM orchestration and RAG pipeline
    - **OpenAI API**: GPT models for text generation
    - **FAISS**: Vector similarity search
    - **Streamlit**: Web interface
    - **SQLite**: HTS tariff data storage
    
    ### 📄 Data Sources:
    - HTS General Notes (PDF) → LLM-processed responses
    - HTS Tariff Schedule (CSV) → Database queries
    - Trade agreement documentation → Vector search
    
    **Note**: This system generates responses from official HTS documentation using advanced AI. For legal determinations, consult licensed customs brokers.
    """)

if __name__ == "__main__":
    main()

