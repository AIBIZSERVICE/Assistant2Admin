import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.schema import Document
from pypdf import PdfReader
from langchain.llms.openai import OpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pdfplumber
from transformers import pipeline

# Extract Information from PDF file
def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# iterate over files in
# that user uploaded PDF files, one by one
def create_docs(user_pdf_list, unique_id):
    docs=[]
    for filename in user_pdf_list:
        
        chunks=get_pdf_text(filename)

        #Adding items to our list - Adding data & its metadata
        docs.append(Document(
            page_content=chunks,
            metadata={"name": filename.name,"type=":filename.type,"size":filename.size,"unique_id":unique_id},
        ))

    return docs

def split_docs(documents, chunk_size=3000, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    return docs

# Create embeddings instance
def create_embeddings_load_data():
    embeddings = OpenAIEmbeddings()
    #embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    return embeddings


# Function to push data to Vector Store - FAISS here
def push_to_store(embeddings,docs):
    db = FAISS.from_documents(docs, embeddings)
    print("done......upload to vector store")
    return db

    
# Function to help us get relavant documents from vector store - based on user input
def get_similar_docs(query,k,db,embeddings,unique_id):
    similar_docs = db.similarity_search(query, int(k),{"unique_id":unique_id})
    print(similar_docs)
    return similar_docs


# Helps us get the summary of a document
def get_summary(current_doc):
    llm = OpenAI(temperature=0)
    #llm = HuggingFaceHub(repo_id="bigscience/bloom", model_kwargs={"temperature":1e-10})
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = chain.run([current_doc])

    return summary

# Combined the relevant reference for answer the enquiry
def combined_text(relevant_docs):
    text = ""
    for item in range(len(relavant_docs)):
        text = text + relavant_docs[item]
    return text

# Load pre-trained NLP model for question answering
nlp = pipeline("question-answering")
def answer_question(question, context):
    return nlp(question=question, context=context)
