import streamlit as st
from typing import Dict
import markdown
from weasyprint import HTML, CSS
from datetime import datetime
import os

# HTML template (inlined here; could stay in a separate file)
def get_html_template():
    return '''
<!DOCTYPE html>
<html>
<head>
    <style>
        @page {{
            size: letter portrait;
            margin: 2.5cm 1cm 2cm 1cm;
            @top-center {{ content: element(header); width: 100%; }}
            @bottom-center {{ content: counter(page); }}
        }}
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 0;
            counter-reset: page 1;
            font-size: 11pt;
        }}
        #header {{
            position: running(header);
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100vw;
            padding: 10px;
            background-color: white;
            border-bottom: 1px solid #ddd;
            box-sizing: border-box;
        }}
        .header-left {{
            flex: 1;
            text-align: left;
        }}
        .header-left h3 {{
            margin: 0;
            padding: 0;
            font-size: 12pt;
            color: #333;
        }}
        .header-left p {{
            margin: 5px 0 0 0;
            padding: 0;
            font-size: 9pt;
            color: #666;
        }}
        .header-right {{
            flex: 1;
            text-align: right;
        }}
        .header-logo {{
            width: 200px;
            height: auto;
            max-height: 45px;
            object-fit: contain;
        }}
        .content {{
            width: 100%;
            max-width: 1200px;
            page-break-before: always;
            text-align: justify;
        }}
        .content p {{
            text-align: justify;
            text-justify: inter-word;
        }}
        h1 {{
            font-size: 18pt;
            margin-top: 30px;
            margin-bottom: 15px;
            color: #000080;
            border-bottom: 1px solid #ddd;
            padding-bottom: 5px;
        }}
        h2 {{
            font-size: 14pt;
            margin-top: 25px;
            margin-bottom: 12px;
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 11pt;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }}
        th {{
            background-color: #f5f5f5;
            font-weight: bold;
            color: #333;
        }}
    </style>
</head>
<body>
    <div id="header">
        <div class="header-left">
            <h3>{subject_company}</h3>
            <p>Generated on {generation_date}</p>
        </div>
        <div class="header-right">
            <a href="{company_website}"><img src="{logo_path}" alt="Company Logo" class="header-logo"></a>
        </div>
    </div>
    <div class="content">
        {content}
    </div>
</body>
</html>
'''

# Conversion function
def convert_markdown_to_pdf(markdown_content: str, output_path: str, company_info: Dict[str, str], 
                          subject_company_info: Dict[str, str]) -> str:
    html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
    template = get_html_template()
    current_date = datetime.now().strftime('%d-%m-%Y')
    logo_path = "./artha intelligence.png"  # Must be in repo or uploaded
    filled_template = template.format(
        company_name=company_info["name"],
        company_website=company_info["website"],
        subject_company=subject_company_info["name"],
        generation_date=current_date,
        content=html_content,
        logo_path=logo_path
    )
    HTML(string=filled_template, base_url=os.path.dirname(__file__)).write_pdf(
        output_path, stylesheets=[CSS(string='@page { size: letter portrait; margin: 2.5cm 1cm 2cm 1cm; }')]
    )
    return output_path

# Streamlit app
st.title("Markdown to PDF Converter")

# Hardcoded company info (could be made editable via st.text_input)
creator_company_info = {"name": "Artha Intelligence", "website": "https://www.arthaintelligence.in/"}
subject_company_info = {"name": "Zen Technologies Limited", "website": ""}

# File uploader
uploaded_files = st.file_uploader("Upload Markdown files", type="md", accept_multiple_files=True)

# Toggle for combining PDFs
combine_pdfs = st.toggle("Combine all files into one PDF", value=False)

if uploaded_files:
    if combine_pdfs:
        # Combine Markdown content
        combined_content = ""
        for file in uploaded_files:
            combined_content += file.read().decode('utf-8') + "\n\n---\n\n"  # Separator between files
        output_path = "combined_output.pdf"
        convert_markdown_to_pdf(combined_content, output_path, creator_company_info, subject_company_info)
        with open(output_path, "rb") as f:
            st.download_button("Download Combined PDF", f, file_name=output_path)
    else:
        # Individual PDFs
        for file in uploaded_files:
            content = file.read().decode('utf-8')
            output_path = f"{file.name.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            convert_markdown_to_pdf(content, output_path, creator_company_info, subject_company_info)
            with open(output_path, "rb") as f:
                st.download_button(f"Download {file.name}", f, file_name=output_path)