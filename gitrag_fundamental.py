## Updated RAG-based GitHub context LLM modeling

import os
import uuid
import gc
import streamlit as st
from langchain.schema import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from gitingest import ingest
from langchain_groq import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
from langchain.chains.combine_documents import create_stuff_documents_chain

# Load environment variables
load_dotenv()

# Initialize LLM
llm = ChatGroq(model="llama-3.1-8b-instant")
print(llm)

# Initialize HuggingFace Embeddings
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Streamlit UI
st.title("RAG GitHub Repo Analyzer")

repo_url = st.text_input("Enter GitHub Repository URL")
query = st.text_input("Ask something about the repository")

if st.button("Process Repo") and repo_url:
    # Ingest repository (dummy or real)
    summary, tree, content = ingest(repo_url)

    # Create documents
    docs = [
        Document(page_content=tree, metadata={"type": "structure"}),
        Document(page_content=summary, metadata={"type": "summary"}),
        Document(page_content=content, metadata={"type": "content"}),
    ]

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    documents = text_splitter.split_documents(docs)

    # Create FAISS vector store
    vector_store = FAISS.from_documents(documents=documents, embeddings=embeddings)
    retriever = vector_store.as_retriever()

    # Prompt template
    prompt = ChatPromptTemplate.from_template(
        """
        You are an AI assistant specialized in analyzing GitHub repositories.

        Repository structure:

        Context information from the repository:
        {context}
        ---------------------

        Given the repository structure and context above, provide a clear and precise answer to the query.
        Focus on the repository's content, code structure, and implementation details.
        If the information is not available in the context, respond with 'I don't have enough information about that aspect of the repository.'

        Query: {input}
        Answer: 
        """
    )

    # Create chains
    document_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    retrieval_chain = create_retrieval_chain(retriever, document_chain)

    # Get response
    if query:
        response = retrieval_chain.invoke({"input": query})
        st.markdown("### Response from AI:")
        st.write(response.get("answer", "No answer returned"))
