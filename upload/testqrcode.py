"""
import PIL
from pyzbar import pyzbar
def read_qr_code(filename):
    codes = pyzbar.decode(PIL.Image.open(filename))
    return codes[0].data.decode() 

# Exemple d'utilisation
url = read_qr_code("test_QRCode.png")
print(url) 
"""
import pyzbar.pyzbar
import PIL.Image
import webbrowser

def read_qr_code(filename):
    image = PIL.Image.open(filename)
    codes = pyzbar.pyzbar.decode(image)
    return codes[0].data.decode() if codes else None

url = read_qr_code("test_QRCode.png")
webbrowser.open(url)