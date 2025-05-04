import re
import base64
from typing import List
from langchain_core.documents import Document

def looks_like_base64(sb):
    """Check if the string looks like base64"""
    return re.match("^[A-Za-z0-9+/]+[=]{0,2}$", sb) is not None


def is_image_data(b64data):
    """
    Check if the base64 data is an image by looking at the start of the data
    """
    image_signatures = {
        b"\xff\xd8\xff": "jpg",
        b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a": "png",
        b"\x47\x49\x46\x38": "gif",
        b"\x52\x49\x46\x46": "webp",
    }
    try:
        header = base64.b64decode(b64data)[:8]  # Decode and get the first 8 bytes
        for sig, format in image_signatures.items():
            if header.startswith(sig):
                return True
        return False
    except Exception:
        return False


def split_image_text_types(docs):
    """
    Split base64-encoded images and texts
    """
    b64_images = []
    texts = []
    for doc in docs:
        # Check if the document is of type Document and extract page_content if so
        if isinstance(doc, Document):
            doc = doc.page_content.decode('utf-8')
        else:
            doc = doc.decode('utf-8')
        if looks_like_base64(doc) and is_image_data(doc):
            b64_images.append(doc)
        else:
            texts.append(doc)
    return {"images": b64_images, "texts": texts}

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

def insert_meta(id_key, chunk_metadata):
    chunk_metadata_upd = {
        'doc_id': id_key,
        'page': chunk_metadata['page'],
        'source': chunk_metadata['source'],
        'title': chunk_metadata['source'].split('/')[-1]
    }
    return chunk_metadata_upd