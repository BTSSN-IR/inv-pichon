"""
import PIL
from pyzbar import pyzbar
def read_qr_code(filename):
    codes = pyzbar.decode(PIL.Image.open(filename))
    return codes[0].data.decode() 

# Exemple d'utilisation
url = read_qr_code("test_QRCode.png")
print(url) l


import pyzbar.pyzbar
import PIL.Image
import webbrowser

def read_qr_code(filename):
    image = PIL.Image.open('r',filename,encoding = 'utf-8')
    codes = pyzbar.pyzbar.decode(image)
    return codes[0].data.decode()

url = read_qr_code('C:\Users\User\Documents\BTS\Projet E6.5\inv-pichon\inv-pichon\upload\QR_Code_example.png')
print(url)

"""

import pyzbar.pyzbar
from PIL import Image
import webbrowser

def read_qr_code(filename):
    image = Image.open(filename)
    codes = pyzbar.pyzbar.decode(image)
    return codes[0].data.decode()

url = read_qr_code('C:\Users\User\Documents\BTS\Projet E6.5\inv-pichon\inv-pichon\upload\QR_Code_example.png')
print(url)
