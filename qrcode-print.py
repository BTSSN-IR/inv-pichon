import os
import qrcode
from docx import Document
from docx.shared import Inches, Cm
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Spacer

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def create_labels_with_qr_codes(data_list, rows, cols, output_filename, label_width, label_height, cube_image_path):
    document = Document()

    sections = document.sections
    for section in sections:
        section.top_margin = Cm(0.6)
        section.bottom_margin = Cm(0)
        section.left_margin = Cm(1.2)
        section.right_margin = Cm(0)

    table = document.add_table(rows=rows, cols=cols)
    
    # Ajuster les dimensions des cellules pour qu'elles correspondent à la taille des étiquettes
    table.autofit = False
    for row in table.rows:
        row.height = Cm(label_height)
        for cell in row.cells:
            cell.width = Cm(label_width)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER

    # Insérer les QR codes, les images de cubes et le texte dans les cellules du tableau
    data_index = 0
    for i in range(rows):
        for j in range(cols):
            if data_index < len(data_list):
                filename = f'qrcodes/qrcode_{data_index}.png'
                generate_qr_code(data_list[data_index], filename)
                cell = table.cell(i, j)
                paragraph = cell.paragraphs[0]
                run = paragraph.add_run()
                
                # Ajouter le QR code
                run.add_picture(filename, width=Cm(label_width * 0.3))
                
                # Ajouter l'image du cube
                run.add_picture(cube_image_path, width=Cm(label_width * 0.3))
                
                # Ajouter le texte
                run.add_text(str(data_list[data_index]))
                
                data_index += 1

    document.save(output_filename)

# Exemple d'utilisation
data_list = [f'qrcode-{i}' for i in range(1, 66)]
rows = 13  # Nombre de rangées d'étiquettes
cols = 5  # Nombre de colonnes d'étiquettes
label_width = 4  # Largeur des étiquettes en centimètres
label_height = 1  # Hauteur des étiquettes en centimètres
cube_image_path = 'static/favicon-pichon.png'  # Chemin de l'image du cube

create_labels_with_qr_codes(data_list, rows, cols, 'labels_with_pichon.docx', label_width, label_height, cube_image_path)

def convert_docx_to_pdf(docx_path, pdf_path):
    # Lire le fichier DOCX
    doc = Document(docx_path)
    
    # Créer un document PDF
    pdf = SimpleDocTemplate(pdf_path, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    
    # Lire le contenu du DOCX et écrire dans le PDF
    for element in doc.element.body:
        if element.tag.endswith('p'):
            para = Paragraph(element.text, normal_style)
            elements.append(para)
            elements.append(Spacer(1, 12))
        elif element.tag.endswith('tbl'):
            table_data = []
            table = element
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    cell_text = ' '.join(paragraph.text for paragraph in cell.paragraphs)
                    row_data.append(cell_text)
                table_data.append(row_data)
            
            # Créer le tableau ReportLab
            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 12))
    
    # Sauvegarder le PDF
    pdf.build(elements)

# Exemple d'utilisation :
convert_docx_to_pdf("labels_with_pichon.docx", "output.pdf")

# os.startfile('labels_with_pichon.docx', "print") # Lancement de l'impression sur l'imprimante par défaut
