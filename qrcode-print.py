import os
import qrcode
from docx import Document
from docx.shared import Inches, Cm, Pt
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT

import sqlite3

def get_qrcodes_from_db(db_file, table):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    if table == 'Computers':
        liste_qr = cur.execute("SELECT id FROM Computers").fetchall()
        liste_qr = [i[0] for i in liste_qr]
        liste_qr = ['Computers,' + str(i) for i in liste_qr]

    if table == 'Screens':
        liste_qr = cur.execute("SELECT serialnumber FROM Screens").fetchall()
        liste_qr = [i[0] for i in liste_qr]
        liste_qr = ['Screens,' + i for i in liste_qr]

    if table == 'Phones':
        liste_qr = cur.execute("SELECT serialnumber FROM Phones").fetchall()
        liste_qr = [i[0] for i in liste_qr]
        liste_qr = ['Phones,' + i for i in liste_qr]

    if table == 'Printers':
        liste_qr = cur.execute("SELECT serialnumber FROM Printers").fetchall()
        liste_qr = [i[0] for i in liste_qr]
        liste_qr = ['Printers,' + i for i in liste_qr]

    if table == 'ExternalDrives':
        liste_qr = cur.execute("SELECT serialnumber FROM ExternalDrives").fetchall()
        liste_qr = [i[0] for i in liste_qr]
        liste_qr = ['ExternalDrives,' + i for i in liste_qr]
    
    if table == 'All':
        liste_qr = []
        for i in ['Computers', 'Screens', 'Phones', 'Printers', 'ExternalDrives']:
            liste_qr.extend(get_qrcodes_from_db(db_file, i))

    return liste_qr


def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def create_labels_with_qr_codes(data_list, rows, cols, output_filename, label_width, label_height, cube_image_path):
    document = Document()

    sections = document.sections
    for section in sections:
        section.top_margin = Cm(1)
        section.bottom_margin = Cm(0)
        section.left_margin = Cm(0.5)
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
                run.font.size = Pt(4)

                # Ajouter le QR code
                run.add_picture(filename, width=Cm(label_width * 0.4))
                
                # Ajouter l'image du logo Pichon
                run.add_picture(cube_image_path, width=Cm(label_width * 0.2))
                
                # Ajouter le texte
                # run.add_text(str(data_list[data_index]))
                
                data_index += 1

    document.save(output_filename)

def gen_qrcodes_bulk(table, starting_index):
    if table == 'Computers':
        return [ f'Computers,{i}' for i in range(starting_index,starting_index + 65) ]
    elif table == 'Phones':
        return [ f'Phones,{i}' for i in range(starting_index,starting_index + 65) ]
    elif table == 'Screens':
        return [ f'Screens,{i}' for i in range(starting_index,starting_index + 65) ]
    elif table == 'Printers':
        return [ f'Printers,{i}' for i in range(starting_index,starting_index + 65) ]
    elif table == 'ExternalDrives':
        return [ f'ExternalDrives,{i}' for i in range(starting_index,starting_index + 65) ]

# Exemple d'utilisation
data_list = gen_qrcodes_bulk('Computers', 1)
rows = 13  # Nombre de rangées d'étiquettes
cols = 5  # Nombre de colonnes d'étiquettes
label_width = 4.05  # Largeur des étiquettes en centimètres
label_height = 2.12  # Hauteur des étiquettes en centimètres
cube_image_path = 'static/favicon-pichon.png'  # Chemin de l'image du cube

create_labels_with_qr_codes(data_list, rows, cols, 'printing/labels_with_pichon.docx', label_width, label_height, cube_image_path)

# Exemple d'utilisation :

# os.startfile('labels_with_pichon.docx', "print") # Lancement de l'impression sur l'imprimante par défaut
os.startfile('printing\\labels_with_pichon.docx')