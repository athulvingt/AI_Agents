from flask import Flask, request, render_template
import os
import markdown
import re
from werkzeug.utils import secure_filename
from rag import add_document, answer_query, list_collections

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)

# Utility to extract and format citation context
def get_cited_context(result_obj):
    source_with_citations = {}

    def highlight_text(context, quote):
        quote = re.sub(r'\s+', ' ', quote).strip()
        context = re.sub(r'\s+', ' ', context).strip()
        phrases = [phrase.strip() for phrase in re.split(r'[.!?]', quote) if phrase.strip()]
        highlighted_context = context
        for phrase in phrases:
            escaped_phrase = re.escape(phrase)
            pattern = re.compile(r'\b' + escaped_phrase + r'\b', re.IGNORECASE)
            highlighted_context = pattern.sub(lambda m: f"**{m.group(0)}**", highlighted_context)
        return highlighted_context

    for cite in result_obj['citations'].dict()['citations']:
        cite_id = cite['id']
        title = cite['title']
        source = cite['source']
        page = cite['page']
        quote = cite['quotes']

        if (source, title) not in source_with_citations:
            source_with_citations[(source, title)] = {
                'title': title,
                'source': source,
                'citations': []
            }

        citation_entry = next(
            (c for c in source_with_citations[(source, title)]['citations'] if c['id'] == cite_id and c['page'] == page),
            None
        )
        if citation_entry is None:
            citation_entry = {'id': cite_id, 'page': page, 'quote': [quote], 'context': None}
            source_with_citations[(source, title)]['citations'].append(citation_entry)
        else:
            citation_entry['quote'].append(quote)

    for context in result_obj['context']:
        context_id = context.metadata['id']
        context_page = context.metadata['page']
        source = context.metadata['source']
        title = context.metadata['title']
        page_content = context.page_content

        if (source, title) in source_with_citations:
            for citation in source_with_citations[(source, title)]['citations']:
                if citation['id'] == context_id and citation['page'] == context_page:
                    highlighted_content = page_content
                    for quote in citation['quote']:
                        highlighted_content = highlight_text(highlighted_content, quote)
                    citation['context'] = markdown.markdown(highlighted_content)

    return [
        {
            'title': details['title'],
            'source': details['source'],
            'citations': details['citations']
        }
        for details in source_with_citations.values()
    ]

@app.route('/', methods=['GET', 'POST'])
def index():
    collections = list_collections()
    result = None
    active_tab = 'upload'  # Default tab

    if request.method == 'POST':
        active_tab = request.form.get('active_tab', 'upload')

        if 'documents' in request.files:
            # Determine collection name from form
            new_collection = request.form.get('new_collection', '').strip()
            existing_collection = request.form.get('existing_collection', '').strip()
            collection = new_collection if new_collection else existing_collection

            # Handle document upload
            if collection:
                files = request.files.getlist("documents")
                for file in files:
                    filename = secure_filename(file.filename)
                    save_path = os.path.join(UPLOAD_DIR, filename)
                    file.save(save_path)
                    add_document(save_path, collection)

        else:
            # Handle question query
            collection = request.form['collection_name']
            question = request.form['query']
            result = answer_query(question, collection)
            result['answer'] = markdown.markdown(result['answer'])  # Convert Markdown to HTML
            result['formatted_citations'] = get_cited_context(result)
            active_tab = 'ask'

    return render_template("index.html", collections=collections, result=result, active_tab=active_tab)

if __name__ == '__main__':
    app.run(debug=True)