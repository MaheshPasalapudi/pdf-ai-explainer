import streamlit as st
import PyPDF2
from groq import Groq

# --- Streamlit Secrets for API Key ---
try:
    API_KEY = st.secrets["groq"]["api_key"]
except (KeyError, st.errors.MissingSecretsError):
    st.error("⚠️ **Error:** Groq API key is missing from Streamlit secrets.")
    st.info("Please add your Groq API key to your Streamlit secrets.toml file.")
    st.stop() # Stop the app if the key is not available

# --- Page Configuration ---
st.set_page_config(
    page_title="PDF AI Assistant",
    layout="centered", # 'centered' layout works well for single-column mobile apps
    initial_sidebar_state="collapsed", # Always collapsed for a cleaner mobile view
    menu_items={
        'About': "A simple and professional Streamlit app to chat with your PDFs using AI."
    }
)

# --- Custom CSS for a clean, modern look ---
st.markdown("""
    <style>
        /* General body and font styling */
        body {
            font-family: 'Inter', sans-serif;
            color: #2c3e50; /* Darker text for readability */
            line-height: 1.6;
        }

        /* Main container styling for a clean card-like appearance */
        .main .block-container {
            background-color: #ffffff;
            border-radius: 16px; /* Slightly more rounded corners */
            padding: 2rem 1.5rem; /* Adjusted padding for mobile */
            box-shadow: 0 8px 24px rgba(0,0,0,0.1); /* Softer, more professional shadow */
            margin-top: 20px;
            margin-bottom: 20px;
        }

        /* Header styling */
        h1 {
            color: #2980b9; /* Professional blue */
            text-align: center;
            font-family: 'Poppins', sans-serif;
            font-weight: 700;
            font-size: 2.2em; /* Adjusted font size for mobile */
            margin-bottom: 0.8em;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.05);
        }
        h2 {
            color: #34495e;
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 1.6em; /* Adjusted font size for mobile */
            border-bottom: 1px solid #e0e0e0;
            padding-bottom: 0.5em;
            margin-top: 1.5em;
            margin-bottom: 1em;
        }
        h3 {
            color: #34495e;
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 1.3em; /* Adjusted font size for mobile */
            margin-bottom: 0.8em;
        }

        /* Button styling */
        .stButton button {
            background-color: #2980b9; /* Professional blue */
            color: white;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 600;
            font-size: 1em;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 100%; /* Make buttons full width on mobile */
        }
        .stButton button:hover {
            background-color: #3498db; /* Lighter blue on hover */
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
        }
        .stButton button:active {
            transform: translateY(0);
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
        }

        /* Text input and text area styling */
        .st-emotion-cache-158w83p { /* Targets the input/textarea container */
            border-radius: 10px;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); /* Inner shadow for depth */
            border: 1px solid #e0e0e0;
            padding: 10px; /* Reduced padding */
        }
        .st-emotion-cache-158w83p label {
            font-weight: 600;
            color: #34495e;
            font-size: 1em;
            margin-bottom: 8px;
        }
        .st-emotion-cache-158w83p textarea, .st-emotion-cache-158w83p input {
            font-size: 0.95em;
            color: #444;
        }

        /* Message styling (success, info, warning, error) */
        .st-emotion-cache-10trblm, /* Success */
        .st-emotion-cache-1c7sm6m, /* Info */
        .st-emotion-cache-1f1903m, /* Error */
        .st-emotion-cache-1kyxreq { /* Warning */
            border-radius: 8px;
            padding: 12px 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        .st-emotion-cache-10trblm { background-color: #e6ffe6; border-left: 5px solid #28a745; color: #1a5e20; }
        .st-emotion-cache-1c7sm6m { background-color: #e0f2f7; border-left: 5px solid #17a2b8; color: #0c5460; }
        .st-emotion-cache-1f1903m { background-color: #ffe6e6; border-left: 5px solid #dc3545; color: #721c24; }
        .st-emotion-cache-1kyxreq { background-color: #fff3cd; border-left: 5px solid #ffc107; color: #856404; }

        /* Custom spinner style */
        .st-spinner > div > div {
            border-top-color: #2980b9 !important;
            border-width: 3px !important;
        }

        /* Initial message styling */
        .initial-message {
            text-align: center;
            padding: 40px 20px; /* Adjusted padding for mobile */
            background-color: #f8f9fa; /* Lighter background for initial state */
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            margin-top: 30px;
        }
        .initial-message p {
            font-size: 1.2em; /* Adjusted font size */
            color: #666;
            font-weight: 300;
            margin-bottom: 10px;
        }
        .initial-message .emoji {
            font-size: 3em; /* Adjusted emoji size */
            margin-bottom: 15px;
            animation: bounce 2s infinite;
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-10px); }
            60% { transform: translateY(-5px); }
        }
    </style>
""", unsafe_allow_html=True)

# --- App Title and Description ---
st.markdown("<h1><span style='font-size:1.2em;'>📚</span> PDF AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Unlock insights from your documents with the power of AI.</p>", unsafe_allow_html=True)

st.markdown("---") # Separator

# --- File Uploader ---
st.subheader("1. Upload a PDF")
pdf_file = st.file_uploader("Choose a PDF file", type=["pdf"], help="Upload your document here to start asking questions.")

# --- Main App Logic ---
if pdf_file:
    # Check if a new file is uploaded or if 'full_text' is not in session state
    if "full_text" not in st.session_state or st.session_state.get('uploaded_file_name') != pdf_file.name:
        st.session_state.uploaded_file_name = pdf_file.name # Store file name to detect new uploads
        
        with st.spinner("Processing PDF content..."):
            try:
                reader = PyPDF2.PdfReader(pdf_file)
                full_text = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                st.session_state['full_text'] = full_text
                st.success("✅ PDF processed successfully!")
            except Exception as e:
                st.error(f"⚠️ **Error processing PDF:** {e}")
                st.warning("Please ensure the PDF is not corrupted and is readable.")
                st.session_state['full_text'] = "" # Clear text if processing fails
                st.stop() # Stop execution if PDF processing fails

    st.markdown("---")

    # --- Question and Answer Section ---
    st.subheader("2. Ask a Question")
    question = st.text_area(
        "Enter your question about the PDF content:",
        height=120,
        placeholder="e.g., What is the main topic of this document? Summarize the key findings.",
        key="user_question"
    )

    if st.button("Get AI Answer", use_container_width=True):
        if not question:
            st.warning("Please enter a question before clicking 'Get AI Answer'.")
        elif not st.session_state['full_text']:
            st.warning("No text extracted from the PDF. Please upload a valid PDF.")
        else:
            with st.spinner("💬 AI is thinking... Generating your answer..."):
                try:
                    client = Groq(api_key=API_KEY)

                    # Limit the context for faster and more reliable responses
                    context_text = st.session_state['full_text']
                    if len(context_text) > 8000: # Increased context limit slightly
                        context_text = context_text[:8000]
                        st.info("💡 Document context has been truncated to improve performance for very large PDFs.")

                    response = client.chat.completions.create(
                        model="llama3-8b-8192", # Using a fast model
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant. Answer the question based *only* on the provided document text. If the answer is not in the document, state that you cannot find the information."},
                            {"role": "user", "content": f"Document:\n{context_text}\n\nQuestion: {question}"}
                        ],
                        temperature=0.1 # Keep answers concise and factual
                    )
                    answer = response.choices[0].message.content

                    st.markdown("---")
                    st.subheader("🧠 AI Answer")
                    st.markdown(f"**Your Question:** *{question}*")
                    st.success(answer)

                except Exception as e:
                    st.error(f"⚠️ **Error calling AI:** {e}")
                    st.warning("Please ensure your Groq API key is correct and you have an active internet connection.")
else:
    # Initial message when no PDF is uploaded
    st.markdown("""
        <div class="initial-message">
            <p class="emoji">⬆️</p>
            <p>Upload a PDF file to begin your AI-powered Q&A session.</p>
        </div>
    """, unsafe_allow_html=True)
