import os
from pdf2image import convert_from_path
from pypdf import PdfReader, PdfWriter

class pdfSplitter:
    def convert_pdf_to_png(pdf_path, output_folder):
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0].replace(" ", "_")

        pages = convert_from_path(pdf_path)

        processed = []

        for i, page in enumerate(pages):
            file_name = f"{base_name}_{i + 1}.png"
            save_path = os.path.join(output_folder, file_name)
            
            page.save(save_path, "PNG")

            processed.append(save_path)
        return processed

    def fragment_pdf(input_pdf_path, total_pages, path, chunk_size=50):
        reader = PdfReader(input_pdf_path)
        base_name = os.path.splitext(os.path.basename(input_pdf_path))[0].replace(" ", "_")
        output_files = []

        for start_page in range(0, total_pages, chunk_size):
            writer = PdfWriter()
            end_page = min(start_page + chunk_size, total_pages)
            
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            part_num = (start_page // chunk_size) + 1
            output_filename = f"{base_name}_part_{part_num}.pdf"
            
            with open(os.path.join(path, output_filename), "wb") as f:
                writer.write(f)
            
            output_files.append(os.path.join(path, output_filename))

        return output_files