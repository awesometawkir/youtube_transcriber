
import os
from pypdf import PdfReader, PdfWriter

def get_pdf_info(file_path):
    try:
        reader = PdfReader(file_path)
        return {'pages': len(reader.pages), 'is_encrypted': reader.is_encrypted}
    except Exception as e:
        return {'error': str(e)}

def extract_pdf_text(file_path):
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            text += page.extract_text() + "\n\n"
        return text.strip()
    except Exception as e:
        return str(e)

def split_pdf(file_path, parts, output_dir):
    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)
        pages_per_part = total_pages // parts
        remainder = total_pages % parts
        
        generated_files = []
        current_page = 0
        
        base_name = os.path.splitext(os.path.basename(file_path))[0]

        for i in range(parts):
            writer = PdfWriter()
            # Calculate end page for this chunk
            count = pages_per_part + (1 if i < remainder else 0)
            end_page = current_page + count
            
            for p in range(current_page, end_page):
                writer.add_page(reader.pages[p])
            
            output_filename = f"{base_name}_part_{i+1}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            generated_files.append(output_filename)
            current_page = end_page
            
        return generated_files
    except Exception as e:
        raise e

def unlock_pdf(file_path, output_path):
    try:
        reader = PdfReader(file_path)
        if reader.is_encrypted:
            reader.decrypt('') # Try empty password first
            
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
        
        return True
    except Exception as e:
        raise e
