import streamlit as st
import PyPDF2
from groq import Groq
import time # For simulating loading times and showing animations

# 🔐 Hardcoded Groq API key (you can still load from .env for security)
# IMPORTANT: For deployment, use st.secrets["GROQ_API_KEY"] instead of hardcoding!

# Get API key securely
API_KEY = st.secrets["groq"]["api_key"]


# --- Page Configuration ---
st.set_page_config(
    page_title="PDF AI Assistant",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded",
    menu_items={
        'About': "A Streamlit app to chat with your PDFs using AI."
    }
)

# --- Custom CSS for a professional, unique look with animations ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Poppins:wght@400;600;700&display=swap');

        html, body, [class*="st-"] {
            font-family: 'Inter', sans-serif;
            color: #2c3e50; /* Darker text for readability */
            line-height: 1.6;
        }

        /* Keyframe for fade-in animation */
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Main container background and shadow */
        .st-emotion-cache-18ni7ap { /* This targets the main app container */
            background: linear-gradient(135deg, #f0f2f6 0%, #dbe4ee 100%); /* Softer gradient background */
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15); /* More prominent shadow */
            margin-top: 30px;
            margin-bottom: 30px;
            animation: fadeIn 0.8s ease-out forwards; /* Apply fade-in to main content */
        }

        /* Header styling */
        h1 {
            color: #2980b9; /* A professional blue */
            text-align: center;
            font-family: 'Poppins', sans-serif; /* Different font for headers */
            font-weight: 700;
            font-size: 2.8em;
            margin-bottom: 0.6em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.08); /* Stronger text shadow */
        }
        h2 {
            color: #34495e; /* Darker blue-gray for subheaders */
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 2em;
            border-bottom: 2px solid #e0e0e0; /* Lighter border */
            padding-bottom: 0.6em;
            margin-top: 2em;
            margin-bottom: 1em;
        }
        h3 {
            color: #34495e;
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 1.6em;
            margin-bottom: 1em;
        }

        /* Sidebar styling */
        .st-emotion-cache-1d391kg { /* Targets the sidebar container */
            background-color: #ffffff; /* White sidebar */
            border-right: 1px solid #e0e0e0;
            box-shadow: 3px 0 15px rgba(0,0,0,0.08); /* More prominent shadow */
            border-radius: 0 20px 20px 0; /* More rounded */
            padding: 2rem;
        }
        .st-emotion-cache-1d391kg h2 { /* Sidebar header */
            color: #2980b9;
            font-size: 1.8em;
            border-bottom: none;
            padding-bottom: 0;
            margin-top: 0;
            margin-bottom: 1.5em;
        }

        /* Message styling (success, info, error) */
        .st-emotion-cache-10trblm, /* Success message */
        .st-emotion-cache-1c7sm6m, /* Info message */
        .st-emotion-cache-1f1903m { /* Error message */
            border-radius: 10px;
            padding: 15px 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            animation: fadeIn 0.5s ease-out forwards; /* Fade in messages */
        }
        .st-emotion-cache-10trblm { /* Success */
            background-color: #e6ffe6;
            border-left: 6px solid #28a745;
            color: #1a5e20;
        }
        .st-emotion-cache-1c7sm6m { /* Info */
            background-color: #e0f2f7;
            border-left: 6px solid #17a2b8;
            color: #0c5460;
        }
        .st-emotion-cache-1f1903m { /* Error */
            background-color: #ffe6e6;
            border-left: 6px solid #dc3545;
            color: #721c24;
        }

        /* Text input and text area styling */
        .st-emotion-cache-158w83p { /* Text input/area container */
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 6px 20px rgba(0,0,0,0.08); /* Stronger shadow */
            padding: 20px;
            border: 1px solid #e0e0e0;
            transition: box-shadow 0.3s ease-in-out; /* Smooth shadow transition */
        }
        .st-emotion-cache-158w83p:focus-within { /* Highlight on focus */
            box-shadow: 0 8px 25px rgba(0,0,0,0.15), 0 0 0 3px rgba(41, 128, 185, 0.3);
            border-color: #2980b9;
        }
        .st-emotion-cache-158w83p label {
            font-weight: 600;
            color: #34495e;
            font-size: 1.2em;
            margin-bottom: 10px;
            display: block; /* Ensure label is on its own line */
        }
        .st-emotion-cache-158w83p textarea, .st-emotion-cache-158w83p input {
            border: none !important; /* Remove default input border */
            outline: none !important; /* Remove outline on focus */
            font-size: 1.1em;
            color: #444;
        }

        /* Expander styling */
        .st-emotion-cache-cnbvqg { /* Expander header */
            background-color: #ecf0f1;
            border-radius: 10px;
            padding: 12px 20px;
            border: 1px solid #dcdcdc;
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
            transition: all 0.3s ease-in-out; /* Smooth transition for hover */
            cursor: pointer;
        }
        .st-emotion-cache-cnbvqg:hover {
            background-color: #e0e6e9;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transform: translateY(-2px); /* Slight lift on hover */
        }
        .st-emotion-cache-13ln4jo { /* Expander content area */
            background-color: #ffffff;
            border-radius: 0 0 10px 10px;
            border: 1px solid #dcdcdc;
            border-top: none;
            padding: 20px;
            box-shadow: 0 3px 8px rgba(0,0,0,0.05);
            animation: fadeIn 0.6s ease-out forwards; /* Fade in expander content */
        }

        /* Button styling */
        .st-emotion-cache-vk33gh { /* Targets Streamlit buttons */
            background-color: #2980b9; /* Professional blue */
            color: white;
            border-radius: 10px;
            padding: 12px 25px;
            font-weight: 600;
            font-size: 1.1em;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease, transform 0.2s ease, box-shadow 0.3s ease;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }
        .st-emotion-cache-vk33gh:hover {
            background-color: #3498db; /* Lighter blue on hover */
            transform: translateY(-3px) scale(1.01); /* Lift and slightly enlarge */
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        .st-emotion-cache-vk33gh:active {
            transform: translateY(0); /* Press effect */
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }

        /* Custom spinner style */
        .st-spinner > div > div {
            border-top-color: #2980b9 !important; /* Blue spinner */
            border-width: 4px !important; /* Thicker spinner */
        }

        /* Initial message styling */
        .initial-message {
            text-align: center;
            padding: 60px;
            background-color: #ffffff;
            border-radius: 20px;
            box-shadow: 0 8px 30px rgba(0,0,0,0.1);
            margin-top: 40px;
            animation: fadeIn 1s ease-out forwards; /* Fade in initial message */
        }
        .initial-message p {
            font-size: 1.6em;
            color: #555;
            font-weight: 300;
            margin-bottom: 15px;
        }
        .initial-message .emoji {
            font-size: 4em;
            margin-bottom: 25px;
            animation: bounce 2s infinite; /* Subtle bounce animation for emoji */
        }

        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
            40% { transform: translateY(-15px); }
            60% { transform: translateY(-7px); }
        }

        /* Text area for extracted text */
        .st-emotion-cache-1q1n00x textarea { /* Targets the textarea specifically */
            background-color: #f8f9fa; /* Light background for text area */
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e0e0e0;
            min-height: 200px; /* Ensure a decent height */
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.05); /* Inner shadow */
        }
    </style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.markdown("<h1><span style='font-size:1.2em;'>📚</span> PDF AI Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #555;'>Unlock insights from your documents with the power of AI.</p>", unsafe_allow_html=True)

# --- Sidebar for PDF Upload ---
with st.sidebar:
    st.header("Upload Your PDF")
    st.markdown("---") # Separator

    pdf_file = st.file_uploader("Choose a PDF file", type=["pdf"], help="Upload your document here to start asking questions.")

    if pdf_file:
        st.success("✅ **PDF uploaded successfully!**")
        st.info("💡 Now, head to the main area to ask your questions.")

        # Read and extract text
        with st.spinner("Processing PDF content..."):
            # Simulate a brief processing time for better UX with spinner
            time.sleep(0.5)
            reader = PyPDF2.PdfReader(pdf_file)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n" # Add newline for better separation

        # Store full_text in session state to persist it across reruns
        st.session_state['full_text'] = full_text

        # Show optional view of PDF text in sidebar
        with st.expander("📄 **View Extracted Text**"):
            if 'full_text' in st.session_state and st.session_state['full_text']:
                display_text = st.session_state['full_text']
                if len(display_text) > 3000:
                    st.text_area("Extracted Text Preview", display_text[:3000] + "\n\n... (text truncated for display)", height=300)
                else:
                    st.text_area("Extracted Text", display_text, height=300)
            else:
                st.write("No text extracted yet or PDF is empty.")
    else:
        st.markdown("<p style='text-align: center; color: #777;'>Upload a PDF to enable the Q&A feature.</p>", unsafe_allow_html=True)

# --- Main Content Area ---
st.markdown("---") # Separator

if 'full_text' in st.session_state and st.session_state['full_text']:
    # Use columns for a clear separation of input and output
    col_input, col_output = st.columns([1, 2]) # Input column smaller than output

    with col_input:
        st.subheader("❓ Ask a Question")
        question = st.text_area(
            "Enter your question about the PDF content:",
            height=180, # Slightly taller text area
            placeholder="e.g., What is the main topic of this document? Summarize the key findings. Who are the key figures mentioned?",
            key="user_question" # Unique key for the widget
        )

        # Button to trigger the AI response
        if st.button("Get AI Answer", use_container_width=True):
            if question:
                if not API_KEY:
                    st.error("⚠️ **Error:** Groq API key is missing. Please provide it in the `API_KEY` variable or use Streamlit secrets.")
                else:
                    with col_output: # Show spinner in the output column
                        with st.spinner("💬 AI is thinking... Generating your answer..."):
                            # Simulate AI processing time for better UX
                            time.sleep(1)
                            try:
                                client = Groq(api_key=API_KEY)
                                response = client.chat.completions.create(
                                    model="llama3-8b-8192", # Using a fast model
                                    messages=[
                                        {"role": "system", "content": "You are a helpful assistant. Answer the question based *only* on the provided document text. If the answer is not in the document, state that you cannot find the information."},
                                        {"role": "user", "content": f"Document:\n{st.session_state['full_text'][:4000]}\n\nQuestion: {question}"} # Limit context to 4000 chars
                                    ],
                                    temperature=0.1 # Keep answers concise and factual
                                )
                                answer = response.choices[0].message.content
                                st.subheader("🧠 **AI Answer**")
                                st.markdown(f"**Your Question:** *{question}*")
                                st.success(answer) # Display answer in a success box
                            except Exception as e:
                                st.error(f"⚠️ **Error calling AI:** {e}")
                                st.warning("Please ensure your Groq API key is correct and you have an active internet connection.")
            else:
                with col_output:
                    st.warning("Please enter a question before clicking 'Get AI Answer'.")
    with col_output:
        if 'full_text' in st.session_state and st.session_state['full_text'] and not question:
            st.info("Type your question on the left and click 'Get AI Answer' to get started!")
        elif not pdf_file:
            st.markdown("""
                <div class="initial-message">
                    <p class="emoji">⬆️</p>
                    <p>Upload a PDF file using the sidebar on the left to begin your AI-powered Q&A session.</p>
                </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
        <div class="initial-message">
            <p class="emoji">⬆️</p>
            <p>Upload a PDF file using the sidebar on the left to begin your AI-powered Q&A session.</p>
        </div>
    """, unsafe_allow_html=True)
