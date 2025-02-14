from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
import threading
import json

# Initialize Flask app and CORS
app = Flask(__name__)
CORS(app)

SESSIONS_FOLDER = './sessions'  # Change this to the actual path where chat histories are saved

# Create the sessions folder if it doesn't exist
if not os.path.exists(SESSIONS_FOLDER):
    os.makedirs(SESSIONS_FOLDER)

# Load API key
with open(r"c:\Users\DELL\VS_Code_Files\thesis\GOOGLE_API_KEY.txt", "r") as file:
    api_key = file.read().strip()

# Configure API key
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize the generative model and embeddings
model = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-1.5-flash")
embeddings = GoogleGenerativeAIEmbeddings(google_api_key=api_key, model="models/embedding-001")

# Directory for PDF files
pdf_directory = "./pdf_files"  # Change to your folder path
docs = []

# Load FAISS index directly from disk
vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)  # Load the saved FAISS index
retriever = vector_store.as_retriever()

# Set up the prompt template for question answering
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

template = """
You are IncidenceResponse-AI, a highly knowledgeable security assistant dedicated to providing expert guidance on incident response.

When answering, consider the context provided below and use your expertise to craft a detailed, clear, and actionable response. Be sure to adapt based on the nature of the user's inquiry.

If the context doesn't contain sufficient information to fully answer the question, say: 
"I'm not sure, but I can try to help! Could you clarify or provide more details?"

If the user asks for a step-by-step process, provide a structured, easy-to-follow breakdown with as much detail as needed.

If the question is a greeting or casual, non-technical inquiry, respond politely and helpfully but keep the focus on being professional. For instance, you can acknowledge the greeting or express a willingness to assist.

If the user asks for something unrelated, such as asking for pictures or general advice outside of incident response, you can say:
"I'm here to help with incident response and security-related questions. Feel free to ask me about those!"

If the user asks about security attacks, give them the answer for how much context that they give you.

If the context that the user gave doesn't ask for an incidence response then reply with only what they ask you for.

Ensure your answer is clear, concise, and directly addresses the question. If necessary, ask clarifying questions to better understand the user's issue.

context: {context}

question: {question}

Provide the answer as follows:
1. If it's a technical incident response question, provide a brief introduction to the situation and detailed steps.
2. If it's a greeting or casual question, respond politely and professionally.
3. If it's unrelated or nonsensical, guide the user back to incident response topics or politely redirect.
4. Any follow-up questions that could help clarify or provide further details on the incident.
"""

prompt = PromptTemplate(template=template)




# Build the RAG chain
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | model
    | StrOutputParser()
)

@app.route('/get_sessions', methods=['GET'])
def get_sessions():
    files = [f for f in os.listdir(SESSIONS_FOLDER) if f.endswith('.json')]
    return jsonify(files)

@app.route('/load_session/<filename>', methods=['GET'])
def load_session(filename):
    with open(f'sessions/{filename}', 'r') as f:
        chat_history = json.load(f)
    return jsonify(chat_history)

@app.route('/save_chat', methods=['POST'])
def save_chat():
    data = request.get_json()
    filename = data['filename']
    chat_history = data['chatHistory']
    
    try:
        # Ensure the filename ends with .json
        if not filename.endswith('.json'):
            filename += '.json'

        # Save the chat history in the sessions folder
        filepath = os.path.join(SESSIONS_FOLDER, filename)
        
        # Save chat history to the specified file
        with open(filepath, 'w') as file:
            json.dump(chat_history, file, indent=4)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error saving chat history: {e}")
        return jsonify({'success': False, 'error': str(e)})



@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data['question'].strip()  # Normalize input

    try:
        response = rag_chain.invoke(question)

        # Handle cases where RAG fails
        if not response.strip() or "Hmmm! I don't know" in response:
            response = "I'm not entirely sure, but I can try to help! Could you provide more details or ask in a different way?"

        # Apply formatting for better readability
        formatted_response = format_response(response)

        return jsonify({
            'answer': formatted_response,
        })

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Something went wrong, but feel free to ask me again!'})


def format_response(response):
    """Formats the chatbot's response for a more readable and friendly tone.""" 
    response = response.replace("**", "")  # Remove bold markers if any
    response = response.replace("* ", "🔹 ")  # Convert bullet points to emojis
    response = response.replace("\n", "<br>")  # Ensure proper spacing for web display
    formatted_response = f'<div style="text-align: left;">{response}</div>'

    # Add a friendly follow-up
    return formatted_response


# Route to handle PDF file upload
@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.endswith('.pdf'):
        # Save the uploaded PDF to the pdf_files directory
        pdf_path = os.path.join(pdf_directory, file.filename)
        file.save(pdf_path)

        # Process the uploaded PDF
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        # Split the document and create embeddings
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)

        # Add the document embeddings to FAISS index
        vector_ids = vector_store.add_documents(splits)

        # Save the updated FAISS index
        vector_store.save_local("faiss_index")

        return jsonify({'success': True, 'message': 'PDF uploaded and processed successfully.'})
    else:
        return jsonify({'error': 'Invalid file type. Only PDF files are allowed.'})

# Directory for PDFs and FAISS index
pdf_directory = "./pdf_files"  # Make sure this is your actual directory for PDFs
faiss_index_path = "faiss_index"

# Route to list all PDFs in the directory
@app.route('/list_pdfs', methods=['GET'])
def list_pdfs():
    try:
        # List all PDF files in the directory
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        return jsonify({'pdfs': pdf_files})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/delete_pdf', methods=['POST'])
def delete_pdf():
    data = request.get_json()
    filename = data['filename']
    pdf_path = os.path.join(pdf_directory, filename)

    try:
        # Delete the PDF file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'PDF not found'})
    except Exception as e:
        return jsonify({'error': str(e)})

def reload_all_pdfs():
    """Reloads all PDFs from the ./pdf_files directory and rebuilds the FAISS index."""
    global vector_store  # Ensure we're updating the global FAISS index

    try:
        # List all PDFs in the directory
        pdf_files = [os.path.join(pdf_directory, f) for f in os.listdir(pdf_directory) if f.endswith('.pdf')]

        if not pdf_files:
            return "No PDF files found in the directory."

        all_docs = []

        # Load all PDFs
        for pdf_path in pdf_files:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            all_docs.extend(docs)

        # Split the documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(all_docs)

        # Create a new FAISS index from the document chunks
        vector_store = FAISS.from_documents(splits, embeddings)

        # Save the FAISS index locally
        vector_store.save_local("faiss_index")

        return "FAISS index successfully rebuilt with all PDFs."

    except Exception as e:
        return f"Error reloading PDFs: {str(e)}"

@app.route('/reload_pdfs', methods=['POST'])
def reload_pdfs():
    """API to reload all PDFs and rebuild the FAISS index."""
    message = reload_all_pdfs()  # Call the function to reload PDFs
    return jsonify({'message': message})


# Function to run the server on port 5005
def run_flask11():
    app.run(debug=False, port=5005)

def start_rag_server():
    flask_thread = threading.Thread(target=run_flask11, daemon=True)
    flask_thread.start()

