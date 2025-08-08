import os
import uuid
from dotenv import load_dotenv
from typing import List, TypedDict, Optional

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_chroma import Chroma

from langgraph.graph import StateGraph, START, END

from operator import itemgetter

from log import logger
from schema import QuotedCitations

# Load environment variables
load_dotenv()

# Directories
UPLOAD_DIR = "uploads"
CHROMA_DIR = "./rag_chroma_db"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Lazy-initialized models
_embedding_model = None
_chatgpt = None
_structured_chatgpt = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')
    return _embedding_model


def get_chat_model():
    global _chatgpt
    if _chatgpt is None:
        _chatgpt = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return _chatgpt


def get_structured_chat_model():
    global _structured_chatgpt
    if _structured_chatgpt is None:
        _structured_chatgpt = get_chat_model().with_structured_output(QuotedCitations)
    return _structured_chatgpt


def get_chroma_collection(collection_name: str) -> Chroma:
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embedding_model(),
        collection_metadata={"hnsw:space": "cosine"},
        persist_directory=os.path.join(CHROMA_DIR, collection_name),
    )


def list_collections() -> List[str]:
    if not os.path.exists(CHROMA_DIR):
        return []
    return [name for name in os.listdir(CHROMA_DIR) if os.path.isdir(os.path.join(CHROMA_DIR, name))]


# ---------- Chunking with generated context ----------

def generate_chunk_context(document: str, chunk: str) -> str:
    chunk_process_prompt = """You are an AI assistant specializing in research paper analysis.
                            Your task is to provide brief, relevant context for a chunk of text
                            based on the following research paper.

                            Here is the research paper:
                            <paper>
                            {paper}
                            </paper>

                            Here is the chunk we want to situate within the whole document:
                            <chunk>
                            {chunk}
                            </chunk>

                            Provide a concise context (3-4 sentences max) for this chunk,
                            considering the following guidelines:

                            - Give a short succinct context to situate this chunk within the overall document
                            for the purposes of improving search retrieval of the chunk.
                            - Answer only with the succinct context and nothing else.
                            - Context should be mentioned like 'Focuses on ....'
                            do not mention 'this chunk or section focuses on...'

                            Context:
                        """

    prompt_template = ChatPromptTemplate.from_template(chunk_process_prompt)

    agentic_chunk_chain = (
        prompt_template
        | get_chat_model()
        | StrOutputParser()
    )

    context = agentic_chunk_chain.invoke({'paper': document, 'chunk': chunk})
    return context


def create_contextual_chunks(file_path: str, chunk_size: int = 3500, chunk_overlap: int = 0) -> List[Document]:
    logger.info(f'Loading pages: {file_path}')
    loader = PyMuPDFLoader(file_path)
    doc_pages = loader.load()

    logger.info(f'Chunking pages: {file_path}')
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    doc_chunks = splitter.split_documents(doc_pages)

    logger.info(f'Generating contextual chunks: {file_path}')
    original_doc = '\n'.join([doc.page_content for doc in doc_chunks])
    contextual_chunks: List[Document] = []
    for chunk in doc_chunks:
        chunk_content = chunk.page_content
        chunk_metadata = chunk.metadata
        chunk_metadata_upd = {
            'id': str(uuid.uuid4()),
            'page': chunk_metadata['page'],
            'source': chunk_metadata['source'],
            'title': chunk_metadata['source'].split('/')[-1],
        }
        context = generate_chunk_context(original_doc, chunk_content)
        contextual_chunks.append(
            Document(page_content=context + '\n' + chunk_content, metadata=chunk_metadata_upd)
        )
    logger.info(f'Finished processing: {file_path}')
    return contextual_chunks


def add_document(file_path: str, collection: str) -> bool:
    chroma_path = os.path.join(CHROMA_DIR, collection)
    os.makedirs(chroma_path, exist_ok=True)
    vectorstore = get_chroma_collection(collection)
    docs = create_contextual_chunks(file_path=file_path, chunk_size=3500)
    vectorstore.add_documents(docs)
    return True


def get_retriever(collection: str):
    vectorstore = get_chroma_collection(collection)
    similarity_retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})
    return similarity_retriever


def format_docs_with_metadata(docs: List[Document]) -> str:
    formatted_docs = [
        f"""Context Article ID: {doc.metadata['id']}
            Context Article Source: {doc.metadata['source']}
            Context Article Title: {doc.metadata['title']}
            Context Article Page: {doc.metadata['page']}
            Context Article Details: {doc.page_content}
         """
        for doc in docs
    ]
    return "\n\n" + "\n\n".join(formatted_docs)


# ---------- LangGraph RAG ----------

class RAGState(TypedDict, total=False):
    question: str
    collection: str
    context: List[Document]
    answer: str
    citations: QuotedCitations


def retrieve_node(state: RAGState) -> RAGState:
    question = state["question"]
    collection = state["collection"]
    retriever = get_retriever(collection)
    docs = retriever.get_relevant_documents(question)
    return {"context": docs}


def answer_node(state: RAGState) -> RAGState:
    rag_prompt = """You are an assistant who is an expert in question-answering tasks.
                    Answer the following question using only the following pieces of retrieved context.
                    If the answer is not in the context, do not make up answers, just say that you don't know.
                    Keep the answer detailed and well formatted based on the information from the context.

                    Question:
                    {question}

                    Context:
                    {context}

                    Answer:
                """
    rag_prompt_template = ChatPromptTemplate.from_template(rag_prompt)

    formatted_context = format_docs_with_metadata(state["context"]) if state.get("context") else ""

    chain = (
        rag_prompt_template
        | get_chat_model()
        | StrOutputParser()
    )

    answer = chain.invoke({
        "question": state["question"],
        "context": formatted_context,
    })

    return {"answer": answer}


def cite_node(state: RAGState) -> RAGState:
    citations_prompt = """You are an assistant who is an expert in analyzing answers to questions
                              and finding out referenced citations from context articles.

                              Given the following question, context and generated answer,
                              analyze the generated answer and quote citations from context articles
                              that can be used to justify the generated answer.

                              Question:
                              {question}

                              Context Articles:
                              {context}

                              Answer:
                              {answer}
                          """
    cite_prompt_template = ChatPromptTemplate.from_template(citations_prompt)

    formatted_context = format_docs_with_metadata(state["context"]) if state.get("context") else ""

    # Structured output to QuotedCitations
    citations = (cite_prompt_template | get_structured_chat_model()).invoke({
        "question": state["question"],
        "context": formatted_context,
        "answer": state["answer"],
    })

    return {"citations": citations}


def _build_graph():
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve_node)
    graph.add_node("answer", answer_node)
    graph.add_node("cite", cite_node)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", "cite")
    graph.add_edge("cite", END)

    return graph.compile()


compiled_graph = _build_graph()


def answer_query(query: str, collection: str):
    """Run the LangGraph RAG pipeline and return a result mirroring the original shape.

    Returns a dict with keys: 'context' (List[Document]), 'answer' (str), 'citations' (QuotedCitations)
    """
    state_input: RAGState = {
        "question": query,
        "collection": collection,
    }
    result_state = compiled_graph.invoke(state_input)

    # Ensure the return shape matches the original app expectations
    return {
        "context": result_state.get("context", []),
        "answer": result_state.get("answer", ""),
        "citations": result_state.get("citations"),
    }


if __name__ == "__main__":
    query = "What are the main components of a RAG model, and how do they interact?"
    # This will require you to have a populated collection
    # print(answer_query(query, 'test_collection'))