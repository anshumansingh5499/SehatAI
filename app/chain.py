import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from app.guardrails import build_system_prompt

load_dotenv()

CHROMA_PATH = "./chroma_db"
chat_histories = {}


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 10}
    )

    llm = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.2,
        max_tokens=600
    )

    system = build_system_prompt()
    prompt = PromptTemplate.from_template(
        system + """
Medical context:
{context}

Chat history:
{chat_history}

Patient says: {question}

Your triage response:"""
    )

    def get_response(inputs):
        question = inputs["question"]
        session_id = inputs.get("session_id", "default")

        if session_id not in chat_histories:
            chat_histories[session_id] = []

        history_str = ""
        for msg in chat_histories[session_id][-5:]:
            if isinstance(msg, HumanMessage):
                history_str += f"Patient: {msg.content}\n"
            elif isinstance(msg, AIMessage):
                history_str += f"Assistant: {msg.content}\n"

        docs = retriever.invoke(question)
        context = format_docs(docs)

        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({
            "question": question,
            "context": context,
            "chat_history": history_str
        })

        chat_histories[session_id].append(HumanMessage(content=question))
        chat_histories[session_id].append(AIMessage(content=response))

        return {"answer": response, "source_documents": docs}

    return get_response