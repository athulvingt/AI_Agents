import PyPDF2


def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    content = ""
    for page in reader.pages:
        content += page.extract_text()
    return content