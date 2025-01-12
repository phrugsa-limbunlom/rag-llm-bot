import json
import os
from flask import Flask, request, jsonify, app
from flask_cors import CORS
import yaml
from dotenv import load_dotenv
from groq import Groq
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

app = Flask(__name__)

# Allow CORS for all routes
CORS(app)

# Groq API
def query_groq_api(prompt):
    """Query the Groq API directly and return the response."""

    model_list = load_model('model.yaml')
    model = model_list["LLM"]

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=model,
        temperature=0.5,
        max_tokens=1024,
        stop=None,
        stream=False,
    )
    return response.choices[0].message.content


# RAG-based QA chain
def generate_answer(query):
    """Generate an answer using RAG and the Groq API."""

    # retrieve context from the vector store from query
    context = retriever.invoke(query)

    # answer by prompt template
    prompt = prompt_template.format(context=" ".join([doc.page_content for doc in context]), query=query)

    # get the answer from the Groq API
    answer = query_groq_api(prompt)

    return answer

def load_prompt_template(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data['template']

def load_model(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
        return data

# # chatbot interaction
# def chatbot():
#     print("Welcome to AI Chatbot. Type 'exit' to quit.")
#     while True:
#         query = input("\nUser: ")
#         if query.lower() == 'exit':
#             break
#
#         # Get response using RAG and Groq API
#         result = generate_answer(query)
#         print("\nBot:", result)

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("query")
    if not user_input:
        return jsonify({"error": "Query not provided"}), 400

    try:
        response = generate_answer(user_input)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    load_dotenv('.env')

    # groq API client
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # embedding
    loader = TextLoader("document/ai_knowledge_base.txt")
    documents = loader.load()

    model_list = load_model('model.yaml')

    model_id = model_list["EMBEDDING"]
    embeddings = HuggingFaceEmbeddings(model_name=model_id)

    # vector store
    vector_store = FAISS.from_documents(documents, embeddings)

    # vector retriever
    retriever = vector_store.as_retriever()

    # Prompt template
    template = load_prompt_template("prompt_template.json")

    prompt_template = PromptTemplate(
        input_variables=["context", "query"],
        template=template
    )

    # chatbot()

    # Run Flask app
    app.run(host="0.0.0.0", port=5000)