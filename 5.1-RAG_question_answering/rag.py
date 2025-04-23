import os
import uuid
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables import RunnableLambda
from langchain.schema import StrOutputParser
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from operator import itemgetter
from typing import List
import time

from sqlalchemy.orm import query_expression

from log import logger
from schema import QuotedCitations

#load environment variable
load_dotenv()

#set directory to upload files
UPLOAD_DIR = "uploads"
CHROMA_DIR =  "./rag_chroma_db"
os.makedirs(UPLOAD_DIR, exist_ok=True)


embedding_model = OpenAIEmbeddings(model='text-embedding-3-small')
chatgpt = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_chatgpt = chatgpt.with_structured_output(QuotedCitations)

def save_uploaded_file(file_storage) :
    filename = f"{file_storage.filename}"
    path = os.path.join(UPLOAD_DIR, filename)
    file_storage.save(path)
    return path

def get_chroma_collection(collection_name):
    return Chroma(
        collection_name=collection_name,
        embedding_function=embedding_model,
        collection_metadata={"hnsw:space": "cosine"},
        persist_directory=os.path.join(CHROMA_DIR, collection_name)
    )

def list_collections():
    return os.listdir(CHROMA_DIR)

def generate_chunk_context(document, chunk):

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

    agentic_chunk_chain = (prompt_template
                                |
                            chatgpt
                                |
                            StrOutputParser())

    context = agentic_chunk_chain.invoke({'paper': document, 'chunk': chunk})

    return context

def create_contextual_chunks(file_path, chunk_size=3500, chunk_overlap=0):

    logger.info(f'Loading pages: {file_path}')
    loader = PyMuPDFLoader(file_path)
    doc_pages = loader.load()

    logger.info(f'Chunking pages: {file_path}')
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                              chunk_overlap=chunk_overlap)
    doc_chunks = splitter.split_documents(doc_pages)

    logger.info(f'Generating contextual chunks: {file_path}')
    original_doc = '\n'.join([doc.page_content for doc in doc_chunks])
    contextual_chunks = []
    for chunk in doc_chunks:
        chunk_content = chunk.page_content
        chunk_metadata = chunk.metadata
        chunk_metadata_upd = {
            'id': str(uuid.uuid4()),
            'page': chunk_metadata['page'],
            'source': chunk_metadata['source'],
            'title': chunk_metadata['source'].split('/')[-1]
        }
        context = generate_chunk_context(original_doc, chunk_content)
        contextual_chunks.append(Document(page_content=context+'\n'+chunk_content,
                                          metadata=chunk_metadata_upd))
    logger.info(f'Finished processing: {file_path}')
    return contextual_chunks

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def format_docs_with_metadata(docs: List[Document]) -> str:
    formatted_docs = [
        f"""Context Article ID: {doc.metadata['id']}
            Context Article Source: {doc.metadata['source']}
            Context Article Title: {doc.metadata['title']}
            Context Article Page: {doc.metadata['page']}
            Context Article Details: {doc.page_content}
         """
            for i, doc in enumerate(docs)
    ]
    return "\n\n" + "\n\n".join(formatted_docs)

def add_document(file_path, collection):
    chroma_path = os.path.join(CHROMA_DIR, collection)
    os.makedirs(chroma_path, exist_ok=True)
    vectorstore = get_chroma_collection(collection)
    docs = create_contextual_chunks(file_path=file_path, chunk_size=3500)
    vectorstore.add_documents(docs)
    return True

def get_retriever(collection):
    vectorstore = get_chroma_collection(collection)
    similarity_retriever = vectorstore.as_retriever(search_type="similarity",
                                                  search_kwargs={"k": 5})
    return similarity_retriever

def answer_query(query, collection):
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
    rag_response_chain = (
            {
                "context": (itemgetter('context')
                            |
                            RunnableLambda(format_docs_with_metadata)),
                "question": itemgetter("question")
            }
            |
            rag_prompt_template
            |
            chatgpt
            |
            StrOutputParser()
    )
    cite_response_chain = (
            {
                "context": itemgetter('context'),
                "question": itemgetter("question"),
                "answer": itemgetter("answer")
            }
            |
            cite_prompt_template
            |
            structured_chatgpt
    )

    rag_chain_w_citations = (
            {
                "context": get_retriever(collection),
                "question": RunnablePassthrough()
            }
            |
            RunnablePassthrough.assign(answer=rag_response_chain)
            |
            RunnablePassthrough.assign(citations=cite_response_chain)

    )
    return rag_chain_w_citations.invoke(query)

if __name__ == "__main__":
    # import glob
    # from schema import Citation
    # pdf_files = glob.glob('/media/athul/CAD3-F0DD/courses/analytics vidya/5. RAG Systems Essentials/RAG Project Dataset/*.pdf')
    # for fp in pdf_files:
    #     add_document(fp,'test_collection')
    query = "What are the main components of a RAG model, and how do they interact?"
    answer = answer_query(query,'test_collection')
    print(answer.keys())
    print(answer['answer'])
    # print(answer['context'])
    print(answer['citations'])