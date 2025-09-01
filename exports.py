# exports.py

import json
import pandas as pd
from xhtml2pdf import pisa

def export_to_json(survey: str) -> str:
    """Export the survey to a JSON format."""
    try:
        survey_dict = {"survey": survey}  # Wrapping the survey in a dictionary
        return json.dumps(survey_dict, indent=4)
    except Exception as e:
        return f"Error exporting to JSON: {e}"

def export_to_csv(survey: str) -> str:
    """Export the survey to a CSV format."""
    try:
        # Assuming survey is in a readable format
        survey_list = [{"question": question.strip()} for question in survey.split('\n') if question.strip()]
        df = pd.DataFrame(survey_list)
        csv_file = "survey.csv"
        df.to_csv(csv_file, index=False)
        return csv_file
    except Exception as e:
        return f"Error exporting to CSV: {e}"

def export_to_html(survey: str) -> str:
    """Export the survey to an HTML form."""
    try:
        # Preprocess survey text to replace newlines with <br> tags for better formatting in HTML
        formatted_survey = survey.replace('\n', '<br>')
        html_content = f"<html><body><h1>Survey</h1><p>{formatted_survey}</p></body></html>"
        
        html_file = "survey.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        return html_file
    except Exception as e:
        return f"Error exporting to HTML: {e}"

def export_to_pdf(survey: str) -> str:
    """Export the survey to a PDF using xhtml2pdf."""
    try:
        # Preprocess survey text to replace newlines with <br> tags for better formatting in HTML
        formatted_survey = survey.replace('\n', '<br>')
        html_content = f"<html><body><h1>Survey</h1><p>{formatted_survey}</p></body></html>"
        
        pdf_file = "survey.pdf"
        with open(pdf_file, "wb") as f:
            pisa_status = pisa.CreatePDF(html_content, dest=f)
        
        if pisa_status.err:
            return "Error exporting to PDF: PDF creation failed"
        return pdf_file
    except Exception as e:
        return f"Error exporting to PDF: {e}"
