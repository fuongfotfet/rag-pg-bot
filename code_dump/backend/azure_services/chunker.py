from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import sys 
import os 
import html
import re
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
form_recognizer_key = os.getenv("FORM_RECOGNIZER_SUBSCRIPTION_KEY")
form_recognizer_enpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")

class DataChunker(): 
    def __init__(self, overlap_size = 100, chunk_size = 1000, sentence_search_limit = 100):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
        self.sentence_search_limit = sentence_search_limit
        self.pdf_parser_client = self.client()

    def client(self): 
        credential = AzureKeyCredential(form_recognizer_key)
        client = DocumentAnalysisClient(form_recognizer_enpoint, credential)
        return client

    def table_to_html(self, table) -> str: 
        table_html = "<table>"
        rows = [sorted([cell for cell in table.cells if cell.row_index == i], key=lambda cell: cell.column_index) for i in range(table.row_count)]
        for row_cells in rows:
            table_html += "<tr>"
            for cell in row_cells:
                tag = "th" if (cell.kind == "columnHeader" or cell.kind == "rowHeader") else "td"
                cell_spans = ""
                if cell.column_span > 1: cell_spans += f" colSpan={cell.column_span}"
                if cell.row_span > 1: cell_spans += f" rowSpan={cell.row_span}"
                table_html += f"<{tag}{cell_spans}>{html.escape(cell.content)}</{tag}>"
            table_html +="</tr>"
        table_html += "</table>"
        return table_html

    def get_page_map(self, document_url): 
        page_map = []
        offset = 0
        form_recognizer_client = self.client()
        with open(document_url, "rb") as f:
            poller = form_recognizer_client.begin_analyze_document("prebuilt-layout", f)
        document_results = poller.result()
        for page_num, page in enumerate(document_results.pages):
            tables_on_page = [table for table in document_results.tables if table.bounding_regions[0].page_number == page_num + 1]
            # mark all positions of the table spans in the page
            page_offset = page.spans[0].offset
            page_length = page.spans[0].length
            table_chars = [-1]*page_length
            for table_id, table in enumerate(tables_on_page):
                for span in table.spans:
                    # replace all table spans with "table_id" in table_chars array
                    for i in range(span.length):
                        idx = span.offset - page_offset + i
                        if idx >=0 and idx < page_length:
                            table_chars[idx] = table_id

            # build page text by replacing charcters in table spans with table html
            page_text = ""
            added_tables = set()
            for idx, table_id in enumerate(table_chars):
                if table_id == -1:
                    page_text += document_results.content[page_offset + idx]
                elif not table_id in added_tables:
                    page_text += self.table_to_html(tables_on_page[table_id])
                    added_tables.add(table_id)

            page_text += " "
            page_map.append((page_num, offset, page_text))
            offset += len(page_text)

        return page_map      

    def chunk_text(self, page_map):
        SENTENCE_ENDINGS = [".", "!", "?"]
        WORDS_BREAKS = [",", ";", ":", " ", "(", ")", "[", "]", "{", "}", "\t", "\n"]

        def find_page(offset):
            l = len(page_map)
            for i in range(l - 1):
                if offset >= page_map[i][1] and offset < page_map[i + 1][1]:
                    return i
            return l - 1

        all_text = "".join(p[2] for p in page_map)
        length = len(all_text)
        start = 0
        end = length
        while start + self.overlap_size < length:
            last_word = -1
            end = start + self.chunk_size

            if end > length:
                end = length
            else:
                # Try to find the end of the sentence
                while end < length and (end - start - self.chunk_size) < self.sentence_search_limit and all_text[end] not in SENTENCE_ENDINGS:
                    if all_text[end] in WORDS_BREAKS:
                        last_word = end
                    end += 1
                if end < length and all_text[end] not in SENTENCE_ENDINGS and last_word > 0:
                    end = last_word # Fall back to at least keeping a whole word
            if end < length:
                end += 1

            # Try to find the start of the sentence or at least a whole word boundary
            last_word = -1
            while start > 0 and start > end - self.chunk_size - 2 * self.sentence_search_limit and all_text[start] not in SENTENCE_ENDINGS:
                if all_text[start] in WORDS_BREAKS:
                    last_word = start
                start -= 1
            if all_text[start] not in SENTENCE_ENDINGS and last_word > 0:
                start = last_word
            if start > 0:
                start += 1

            section_text = all_text[start:end]
            yield (section_text, find_page(start))

            last_table_start = section_text.rfind("<table")
            if (last_table_start > 2 * self.sentence_search_limit and last_table_start > section_text.rfind("</table")):
                # If the section ends with an unclosed table, we need to start the next section with the table.
                # If table starts inside self.sentence_search_limit, we ignore it, as that will cause an infinite loop for tables longer than MAX_SECTION_LENGTH
                # If last table starts inside self.overlap_size, keep overlapping
                start = min(end - self.overlap_size, start + last_table_start)
            else:
                start = end - self.overlap_size
            
        if start + self.overlap_size < end:
            yield (all_text[start:end], find_page(start)) #(content, page_num)

    def create_sections(self, document_url):
        page_map = self.get_page_map(document_url)

        def filename_from_url(document_url): 
            return document_url.split("/")[-1]
        
        filename = filename_from_url(document_url)
        for i, (section, pagenum) in enumerate(self.chunk_text(page_map)):
            yield {
                "id": re.sub("[^0-9a-zA-Z_-]","_",f"{filename}-{i}"),
                "content": section,
                "sourcefile": filename,
                "page": pagenum
            }
        
        
        