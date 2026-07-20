import os
import csv
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ReportGenerator:
    @staticmethod
    def generate_pdf_report(title: str, content: str, output_path: str) -> str:
        """
        Generates a clean PDF document from markdown-like text.
        """
        # Ensure parent directories exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=letter,
            rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54
        )
        
        styles = getSampleStyleSheet()
        story = []
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=22,
            textColor=colors.HexColor('#4f46e5'),
            spaceAfter=15
        )
        
        heading_style = ParagraphStyle(
            'ReportHeading',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            textColor=colors.HexColor('#1e293b'),
            spaceBefore=15,
            spaceAfter=8
        )
        
        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['BodyText'],
            fontName='Helvetica',
            fontSize=10,
            textColor=colors.HexColor('#334155'),
            leading=14,
            spaceAfter=10
        )
        
        # Header
        story.append(Paragraph(title, title_style))
        story.append(Paragraph(f"Generated on: {colors.HexColor('#64748b')}", body_style))
        story.append(Spacer(1, 10))
        
        # Parse content line by line for basic Markdown headers/lists
        lines = content.split('\n')
        for line in lines:
            line_str = line.strip()
            if not line_str:
                story.append(Spacer(1, 4))
                continue
                
            if line_str.startswith('###'):
                story.append(Paragraph(line_str.replace('###', '').strip(), heading_style))
            elif line_str.startswith('##'):
                story.append(Paragraph(line_str.replace('##', '').strip(), heading_style))
            elif line_str.startswith('#'):
                story.append(Paragraph(line_str.replace('#', '').strip(), title_style))
            elif line_str.startswith('-') or line_str.startswith('*'):
                cleaned = line_str.lstrip('-*').strip()
                story.append(Paragraph(f"&bull; {cleaned}", body_style))
            else:
                # Normal paragraph text
                story.append(Paragraph(line_str, body_style))
                
        doc.build(story)
        return output_path

    @staticmethod
    def export_table_to_csv(query: str, db_path: str, output_path: str) -> str:
        """
        Runs a query and saves the output to a CSV file.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            headers = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            with open(output_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)
                
            return output_path
        finally:
            conn.close()
