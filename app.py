import streamlit as st
from google import genai
import os

st.set_page_config(page_title="Gita AI Assistant", page_icon="📜")
st.title("📜 Chat with the Bhagavad Gita")

# 1. Verify API Key
if "GEMINI_API_KEY" not in st.secrets:
    st.error("Please set GEMINI_API_KEY in your .streamlit/secrets.toml file.")
    st.stop()

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
# CHANGE THIS LINE:
PDF_PATH = "GITA Material/bhagavad-gita-in-english-source-file.pdf"

# 2. Upload to Gemini Files API (Runs only ONCE per session)
# We store the Google Cloud file reference in session_state
if "gemini_document" not in st.session_state:
    if not os.path.exists(PDF_PATH):
        st.error(f"Could not find '{PDF_PATH}' in your project folder. Please add it.")
        st.stop()
        
    with st.spinner("Uploading the Gita to Gemini's secure cache... (Happens once)"):
        # This uploads the file to Google's servers and returns a reference
        st.session_state.gemini_document = client.files.upload(file=PDF_PATH)
        
st.success("📖 Bhagavad Gita uploaded and cached successfully!")

# 3. Chat History Setup
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Greetings. Ask me any question about the teachings or philosophy of the Bhagavad Gita."}
    ]

# Render past chat logs
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. Handle Chat Prompt
if user_prompt := st.chat_input("Ask a question about the Gita..."):
    
    # Display user question
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.messages.append({"role": "user", "content": user_prompt})

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing cached text..."):
            try:
                # Build conversation history context
                history_context = ""
                for msg in st.session_state.messages[:-1]:
                    history_context += f"{msg['role'].capitalize()}: {msg['content']}\n"
                
                engineered_prompt = f"""You are an expert guide on the Bhagavad Gita.
                Answer the user's question accurately using the attached document.
                
                History:
                {history_context}
                
                Question: {user_prompt}"""
                
                # Notice how we pass the cached file reference instead of raw bytes!
                # Gemini 2.5's implicit caching will recognize this and skip re-reading the whole book.
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[st.session_state.gemini_document, engineered_prompt]
                )
                
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                
            except Exception as e:
                st.error(f"Error: {e}")