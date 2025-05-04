import htmltabletomd
from langchain_community.document_loaders import UnstructuredPDFLoader

def chunk_file(doc_path, image_path):
    # Chunk text and extract text content
    loader = UnstructuredPDFLoader(file_path=doc_path,
                                   strategy='hi_res',
                                   extract_images_in_pdf=True,
                                   infer_table_structure=True,
                                   mode='elements',
                                   image_output_dir_path='./figures')
    data = loader.load()
    tables = [doc for doc in data if doc.metadata['category'] == 'Table']

    loader = UnstructuredPDFLoader(file_path=doc_path,
                                   strategy='hi_res',
                                   extract_images_in_pdf=True,
                                   infer_table_structure=True,
                                   chunking_strategy="by_title", # section-based chunking
                                   max_characters=4000, # max size of chunks
                                   new_after_n_chars=4000, # preferred size of chunks
                                   combine_text_under_n_chars=2000, # smaller chunks < 2000 chars will be combined into a larger chunk
                                   mode='elements',
                                   image_output_dir_path=image_path)
    docs = loader.load()

    # data = texts + tables
    #
    # #seperate tables and text
    # docs = []
    # tables = []
    #
    # for doc in data:
    #     if doc.metadata['category'] == 'Table':
    #         tables.append(doc)
    #     elif doc.metadata['category'] == 'CompositeElement':
    #         docs.append(doc)


    for table in tables:
        table.page_content = htmltabletomd.convert_table(table.metadata['text_as_html'])
    return docs, tables