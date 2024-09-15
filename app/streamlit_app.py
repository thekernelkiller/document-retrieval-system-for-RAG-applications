import streamlit as st
import requests
from langchain_groq import ChatGroq
from config import Config

# Set up Groq API key
GROQ_API_KEY = Config.GROQ_API_KEY

# Set up the backend API URL
BACKEND_URL = "http://127.0.0.1:5000"  # Adjust this to your backend URL

# Initialize the Groq chat model
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.7, api_key=GROQ_API_KEY)

def get_relevant_documents(query):
    response = requests.post(f"{BACKEND_URL}/api/search", json={
        "user_id": "streamlit_user",  # You might want to implement user management
        "text": query,
        "top_k": 3,  # Adjust as needed
        "threshold": 0.001
    })
    if response.status_code == 200:
        return response.json()['results']
    else:
        st.error(f"Error fetching relevant documents: {response.text}")
        return []

def generate_response(query, relevant_docs):
    # Prepare the context from relevant documents
    context = "\n\n".join([f"Document {i+1}: {doc['text']}" for i, doc in enumerate(relevant_docs)])
    
    # Prepare the prompt for the LLM
    prompt = f"""Based on the following context, answer the user's query. 
    If the answer is not in the context, say "I don't have enough information to answer that question."
    Always cite your sources by referring to the document numbers.

    Context:
    {context}

    User Query: {query}

    Answer:"""

    # Generate response using Groq's Chat model
    messages = [
        ("system", "You are a helpful assistant."),
        ("human", prompt)
    ]
    response = llm.invoke(messages)

    return response.content.strip()

def main():
    st.title("News Chatbot")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What would you like to know?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Get relevant documents
        relevant_docs = get_relevant_documents(prompt)

        # Generate response
        response = generate_response(prompt, relevant_docs)

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

        # Display relevant documents
        with st.expander("Relevant Documents"):
            for i, doc in enumerate(relevant_docs):
                st.markdown(f"**Document {i+1}:**")
                st.markdown(f"Text: {doc['text'][:200]}...")  # Display first 200 characters
                st.markdown(f"URL: {doc['url']}")
                st.markdown("---")

if __name__ == "__main__":
    main()