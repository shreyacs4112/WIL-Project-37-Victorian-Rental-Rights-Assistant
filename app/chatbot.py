import streamlit as st

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

def get_demo_response(question):
    """
    Temporary rule-based responses for UI testing.
    This will be replaced by the real RAG pipeline later.
    """

    q = question.lower()

    if any(word in q for word in ["repair", "heater", "broken", "maintenance"]):
        return (
            "Repairs and maintenance are an important part of Victorian rental rights. "
            "If something in the rental property needs repair, the appropriate next step "
            "depends on the type and urgency of the problem. "
            "The final RAG system will retrieve the relevant Victorian rental guidance "
            "and show the supporting source for this question."
        )

    elif any(word in q for word in ["bond", "deposit", "refund"]):
        return (
            "Bond issues can include bond lodgement, claims, deductions and refunds. "
            "The correct process depends on the circumstances of the rental agreement. "
            "The final RAG system will retrieve the relevant Victorian bond information "
            "and provide the supporting source."
        )

    elif any(word in q for word in ["rent increase", "increase rent", "rent higher"]):
        return (
            "Victorian rental rules place requirements around rent increases, "
            "including how and when renters are notified. "
            "The final RAG system will retrieve the relevant information for your "
            "situation and display the supporting Victorian source."
        )

    elif any(word in q for word in ["inspection", "enter", "entry", "landlord come"]):
        return (
            "Rental providers and agents must follow Victorian requirements when "
            "entering a rented property or conducting inspections. "
            "The final RAG system will retrieve the relevant entry and inspection "
            "guidance and show the supporting source."
        )

    elif any(word in q for word in ["minimum standard", "minimum standards"]):
        return (
            "Victorian rental properties are subject to minimum rental standards. "
            "The final RAG system will retrieve the relevant standard from the "
            "knowledge base and provide the supporting evidence."
        )

    elif any(word in q for word in ["moving in", "condition report"]):
        return (
            "Moving into a rental property can involve important steps such as "
            "checking the condition of the property and reviewing the condition report. "
            "The final RAG system will retrieve the relevant Victorian guidance and "
            "show its source."
        )

    elif any(word in q for word in ["moving out", "end lease", "ending lease", "vacate"]):
        return (
            "Ending a rental agreement can involve notice requirements, property "
            "condition, bond matters and other responsibilities. "
            "The final RAG system will retrieve the relevant Victorian guidance "
            "and display the supporting source."
        )

    else:
        return (
            "I could not match this question to one of the current rental-rights "
            "topics in the prototype. The full RAG system will search the Victorian "
            "rental-rights knowledge base before generating an answer."
        )
    
if question:
    # Save and display user's question
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    response = get_demo_response(question)
    
    with st.chat_message("assistant"):
        st.markdown(response)

    with st.expander("🔎 Retrieved evidence and sources"):
        st.write(
            "Retrieved knowledge-base passages and source information "
            "will be displayed here once the RAG backend is connected."
        )

    # Save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )