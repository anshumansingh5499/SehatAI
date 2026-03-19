import os
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

CHROMA_PATH = "./chroma_db"
DATA_PATH = "./data"


def ingest_documents():
    documents = []
    for filename in os.listdir(DATA_PATH):
        path = os.path.join(DATA_PATH, filename)
        print(f"Loading: {filename}")
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(path)
        elif filename.endswith(".txt"):
            loader = TextLoader(path, encoding="utf-8")
        else:
            print(f"  Skipping {filename}")
            continue
        docs = loader.load()
        documents.extend(docs)
        print(f"  Loaded {len(docs)} sections")

    if not documents:
        print("No documents found in data/ folder!")
        return None

    print(f"\nTotal documents loaded: {len(documents)}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"Created {len(chunks)} chunks")

    print("Creating embeddings locally...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print(f"Done! ChromaDB saved to {CHROMA_PATH}")
    return vectorstore


if __name__ == "__main__":
    ingest_documents()