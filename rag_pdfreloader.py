import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
import numpy as np

# Load API key
with open(r"c:\Users\DELL\VS_Code_Files\thesis\GOOGLE_API_KEY.txt", "r") as file:
    api_key = file.read().strip()

# Configure API key
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Test API
response = model.generate_content("what's 2+2")
print(response.text)

# Initialize the generative model and embeddings
model = ChatGoogleGenerativeAI(api_key=api_key, model="gemini-1.5-flash")
embeddings = GoogleGenerativeAIEmbeddings(google_api_key=api_key, model="models/embedding-001")

# Check whether the model is working properly or not
response = model.invoke(["what is 2+1"])
print(response.content)

# Check whether the embedding works or not
data = embeddings.embed_query("what is 2+1")
print(data[:5])

data = embeddings.embed_documents(
    [
        "Today is Monday",
        "Today is Tuesday",
        "Today is holiday",
    ]
)
print(len(data), len(data[0]))

# Initialize the LLM (Generative Model)
llm = ChatGoogleGenerativeAI(
    google_api_key=api_key,
    model="gemini-1.5-pro",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
)

# Print the output directly instead of using response.content
pdf_directory = "./pdf_files"  # ✅ Change this to your folder path
docs = []

for filename in os.listdir(pdf_directory):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, filename)
        print(f"Loading: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        docs.extend(loader.load())

print(f"Total Documents Loaded: {len(docs)}")

# Split documents and create embeddings
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)

# Embed the documents
embeddings_data = embeddings.embed_documents([doc.page_content for doc in splits])

# Now using Langchain's FAISS to store the embeddings
vector_store = FAISS.from_documents(splits, embeddings)

# Save the FAISS index (optional)
vector_store.save_local("faiss_index")

# Define the retriever that will use the FAISS index
retriever = vector_store.as_retriever()

# Set up the prompt template for question answering
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

template = """
Answer the question based on the context below. If the context is not relevant, just reply "Hmmm! I don't know"

context: {context}

question: {question}
"""

prompt = PromptTemplate(template=template)

# Build the RAG (Retrieval-Augmented Generation) chain
rag_chain = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | model
    | StrOutputParser()
)


