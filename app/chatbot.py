import streamlit as st
from rag.pipeline import run_rag_pipeline

st.set_page_config(
    page_title="Victorian Rental Rights Assistant",
    page_icon="🏠",
    layout="centered"
)

st.title("🏠 Victorian Rental Rights Assistant")

st.write(
    "Ask a question about common Victorian rental rights and responsibilities."
)

st.info(
    "This assistant provides general information only and does not provide personalised legal advice."
)

# Store chat messages during the session
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
question = st.chat_input("Ask a rental-rights question...")


if question:
    # Save and display user's question
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    rag_result = run_rag_pipeline(question)

    response = rag_result["answer"]
    retrieved_chunks = rag_result["retrieved_chunks"]

    with st.chat_message("assistant"):
        st.markdown(response)

    with st.expander("🔎 Retrieved evidence and sources"):
        if retrieved_chunks:
            for i, chunk in enumerate(retrieved_chunks, start=1):
                st.markdown(f"### Evidence {i}")
                st.markdown(f"**Source:** {chunk.get('source', 'Unknown source')}")
                st.markdown(f"**Topic:** {chunk.get('topic', 'Unknown topic')}")
                st.markdown(f"**Section:** {chunk.get('section', 'Unknown section')}")
                st.markdown(f"**Chunk ID:** {chunk.get('chunk_id', 'Unknown chunk')}")
                st.markdown(f"**Relevance score:** {chunk.get('score', 'N/A')}")
                st.markdown(f"**Evidence:** {chunk.get('text', '')}")
        else:
            st.write("No evidence was retrieved.")

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )