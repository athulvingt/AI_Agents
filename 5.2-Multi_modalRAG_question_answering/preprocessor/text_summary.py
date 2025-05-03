from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnablePassthrough

def generate_text_table_summaries(docs, tables, chat_model=None):
    """
    Generate summaries for text and table documents using a chained LangChain pipeline.
    docs: list of text document objects
    tables: list of table document objects
    chat_model: optional ChatOpenAI model, if not passed a default will be created
    """
    if chat_model is None:
        chat_model = ChatOpenAI()

    # Prompt template
    prompt_text = """
    You are an assistant tasked with summarizing tables and text particularly for semantic retrieval.
    These summaries will be embedded and used to retrieve the raw text or table elements
    Give a detailed summary of the table or text below that is well optimized for retrieval.
    For any tables also add in a one line description of what the table is about besides the summary.
    Do not add redundant words like Summary.
    Just output the actual summary content.

    Table or text chunk:
    {element}
    """
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # Define the summary chain
    summarize_chain = (
        {"element": RunnablePassthrough()}
        | prompt
        | chat_model
        | StrOutputParser()
    )

    # Extract content
    text_docs = [doc.page_content for doc in docs]
    table_docs = [table.page_content for table in tables]

    # Run summaries using batch execution
    text_summaries = summarize_chain.batch(text_docs, {"max_concurrency": 5})
    table_summaries = summarize_chain.batch(table_docs, {"max_concurrency": 5})

    return text_summaries,text_docs, table_summaries, table_docs
