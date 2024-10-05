import streamlit as st
import json
from difflib import get_close_matches

# Load and save the knowledge base
def load_knowledge_base(file_path: str) -> dict:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Initialize with empty structure if file is not found or is invalid
        data = {"questions": []}
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

# Find the closest matching question
def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

# Get the answer for a specific question
def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]

# Streamlit chatbot
def chatbot():
    st.title("Chatbot with Learning Capability")

    # Load the knowledge base into session state if not already loaded
    if 'knowledge_base' not in st.session_state:
        st.session_state.knowledge_base = load_knowledge_base('knowledge_base.json')

    # Form for asking a question
    with st.form(key='ask_form', clear_on_submit=True):
        user_input = st.text_input("Ask a question:")
        submit_question = st.form_submit_button("Submit")

    if submit_question:
        if user_input:
            # Find best match
            questions = [q['question'] for q in st.session_state.knowledge_base['questions']]
            best_match = find_best_match(user_input, questions)

            # If a match is found, display the answer
            if best_match:
                answer = get_answer_for_question(best_match, st.session_state.knowledge_base)
                st.write(f"Bot: {answer}")
                # Clear any stored state if match was found
                st.session_state.new_question = None
            else:
                st.write("Bot: I don't know the answer. Can you teach me?")
                # Store the user question for future learning
                st.session_state.new_question = user_input

    # Handle teaching the bot a new response if it doesn't know the answer
    if 'new_question' in st.session_state and st.session_state.new_question:
        with st.form(key='teach_form', clear_on_submit=True):
            new_answer = st.text_input("Type the answer (or leave blank to skip):")
            submit_answer = st.form_submit_button("Teach the Bot")

        if submit_answer and new_answer:
            # Add the new question and answer to the knowledge base
            st.session_state.knowledge_base["questions"].append({
                "question": st.session_state.new_question, 
                "answer": new_answer
            })

            # Save the updated knowledge base to the JSON file
            save_knowledge_base('knowledge_base.json', st.session_state.knowledge_base)
            st.write("Bot: Thank you! I learned a new response.")
            
            # Clear the state after learning
            st.session_state.new_question = None
            st.session_state.new_answer = ''  # Use empty string instead of None to avoid error

# Run the chatbot
if __name__ == "__main__":
    chatbot()
