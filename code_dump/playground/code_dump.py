

def chunk_text(text, max_chunk_size=1000):
    words = text.split()
    chunks = []
    current_chunk = []

    for word in words:
        if len(" ".join(current_chunk + [word])) <= max_chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

all_text = []
for page in document_results.pages:
    for line in page.lines:
        all_text.append(line.content)

full_text = " ".join(all_text)
text_chunks = chunk_text(full_text)

# Assuming you have an Azure Search client set up

search_service_endpoint = "YOUR_SEARCH_SERVICE_ENDPOINT"
search_index_name = "YOUR_INDEX_NAME"
search_api_key = "YOUR_SEARCH_API_KEY"

search_client = SearchClient(endpoint=search_service_endpoint, index_name=search_index_name, credential=AzureKeyCredential(search_api_key))

# Create the index if it doesn't exist
index_client = SearchIndexClient(endpoint=search_service_endpoint, credential=AzureKeyCredential(search_api_key))
fields = [
    SimpleField(name="id", type=edm.String, key=True),
    SimpleField(name="content", type=edm.String)
]
index = SearchIndex(name=search_index_name, fields=fields)
index_client.create_index(index)

# Upload the chunks to Azure Search
for i, chunk in enumerate(text_chunks):
    document = {"id": str(i), "content": chunk}
    search_client.upload_documents(documents=[document])

print("Text chunks have been uploaded to Azure Search.")

from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, edm

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import sys 
import os 
# Add the root project folder to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "/Users/giangpham/Desktop/VCB/test")))
from config import form_recognizer_enpoint, form_recognizer_key

# Document files or link 
credential = AzureKeyCredential(form_recognizer_key)
client = DocumentAnalysisClient(form_recognizer_enpoint, credential)
document_url = "/Users/giangpham/Desktop/VCB/small.pdf"

with open(document_url, "rb") as f:
    poller = client.begin_analyze_document("prebuilt-layout", f)
document_results = poller.result()

# To learn the detailed concept of "span" in the following codes, visit: https://aka.ms/spans 
def _in_span(word, spans):
    for span in spans:
        if word.span.offset >= span.offset and (word.span.offset + word.span.length) <= (span.offset + span.length):
            return True
    return False

def get_words(page, line):
    result = []
    for word in page.words:
        if _in_span(word, line.spans):
            result.append(word)
    return result

# for page in document_results.pages:
#     print(f"----Analyzing layout from page #{page.page_number}----")
#     print(f"Page has width: {page.width} and height: {page.height}, measured with unit: {page.unit}")
#     page_map = []
#     # Analyze lines.
#     if page.lines:
#         for line_idx, line in enumerate(page.lines):
#             words = get_words(page, line)
#             print(
#                 f"...Line # {line_idx} has word count {len(words)} and text '{line.content}' "
#                 f"within bounding polygon '{line.polygon}'"
#             )

#             # Analyze words.
#             for word in words:
#                 print(f"......Word '{word.content}' has a confidence of {word.confidence}")

# all_text = []
# for page in document_results.pages:
#     for line in page.lines:
#         all_text.append(line.content)

# full_text = " ".join(all_text)
# print(full_text)

# print(document_results.paragraphs[6].content)

for paragraph in document_results.paragraphs: 
    print(paragraph.content)
    def get_pdf_files_from_blob(container_name, connection_string):
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)
        blob_list = container_client.list_blobs()
        pdf_files = [blob.name for blob in blob_list if blob.name.endswith('.pdf')]
        return pdf_files

    container_name = "your-container-name"
    connection_string = "your-connection-string"
    pdf_files = get_pdf_files_from_blob(container_name, connection_string)

    for pdf_file in pdf_files:
        blob_client = BlobServiceClient.from_connection_string(connection_string).get_blob_client(container_name, pdf_file)
        with open(pdf_file, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())
        with open(pdf_file, "rb") as f:
            poller = form_recognizer_client.begin_analyze_document("prebuilt-layout", f)
        document_results = poller.result()
        for page_num, page in enumerate(document_results.pages):
            tables_on_page = [table for table in document_results.tables if table.bounding_regions[0].page_number == page_num + 1]
