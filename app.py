"""
Flight Information Chatbot UI using Streamlit
"""
import streamlit as st
from query_handler import process_query
from ollama_api import check_ollama_availability, generate_response

# Set Streamlit page config
st.set_page_config(
    page_title="Flight Information Assistant",
    page_icon="✈️",
)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

def display_chat_message(role, content):
    """Display a chat message in Streamlit UI."""
    with st.chat_message(role):
        st.markdown(content)

# Display the title
st.title("✈️ Flight Information Assistant")

# Check Ollama server availability
ollama_status, ollama_message = check_ollama_availability()
if not ollama_status:
    st.warning("⚠️ Ollama server is unavailable. Responses will be simplified.")

# Show instructions
st.markdown("""
### **Ask me about flights!**  
Try questions like:  
- ✈️ What flights are available from New York to London?  
- 🔍 Show me flight NY100.  
- 📍 Are there any flights from Chicago?  
""")

# Display chat history
for message in st.session_state.messages:
    display_chat_message(message["role"], message["content"])

# Chat input handling
user_input = st.chat_input("Ask about flights...")

if user_input:
    # Add user query to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    display_chat_message("user", user_input)

    # Process query
    with st.spinner("Searching for flights..."):
        try:
            success, message, flights = process_query(user_input)

            if not success:
                response = f"⚠️ {message}"
            else:
                response = generate_response(user_input, flights)

        except ValueError as ve:
            response = f"❌ Invalid input: {str(ve)}"
        except Exception as e:
            response = f"❌ An unexpected error occurred: {str(e)}"

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
    display_chat_message("assistant", response)
