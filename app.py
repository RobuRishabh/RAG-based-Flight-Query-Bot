"""
UI using Streamlit
"""
import streamlit as st
from query_handler import process_query
from ollama_api import check_ollama_availability, generate_response

# ✅ Set page config
st.set_page_config(
    page_title="Flight Information Assistant",
    page_icon="✈️"
)

# ✅ Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# ✅ Check Ollama server availability
ollama_available, ollama_message = check_ollama_availability()

def display_chat_message(role, content):
    """
    Display messages in the chat interface.
    
    Args:
        role (str): Role of the message sender (user or assistant).
        content (str): Message content.
    """
    with st.chat_message(role):
        st.markdown(content)

# ✅ Main UI
st.title("✈️ Flight Information Assistant")

# ✅ Display Ollama server availability message
if not ollama_available:
    st.warning(f"⚠️ {ollama_message}\nUsing simplified responses until Ollama becomes available.")

# ✅ Instructions for the user
st.markdown("""
**Ask me about flights!** Try questions like:
- What flights are available from New York to London?
- Show me flight NY100.
- Are there any flights from Chicago?
""")

# ✅ Display chat history
for message in st.session_state.messages:
    display_chat_message(message["role"], message["content"])

# ✅ Chat input handling
if prompt := st.chat_input("Ask about flights..."):
    # ✅ Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    display_chat_message("user", prompt)

    try:
        # ✅ Process user query
        success, message, flights = process_query(prompt)

        if not success:
            st.error(message)  # Show error message in UI
            response = "⚠️ I couldn't process your request. Try rephrasing your question."
        else:
            # ✅ Generate assistant response
            response = generate_response(prompt, flights)

        # ✅ Store and display assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        display_chat_message("assistant", response)

    except Exception as e:
        error_message = f"❌ An error occurred: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_message})
        display_chat_message("assistant", error_message)
