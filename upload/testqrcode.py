import pyzbar.pyzbar
from PIL import Image
import webbrowser

def read_qr_code(filename):
    image = Image.open(filename)
    codes = pyzbar.pyzbar.decode(image)
    return codes[0].data.decode()

url = read_qr_code("C:\\Users\\Gwendal\\Desktop\\inv-pichon\\inv-pichon\\upload\\QR_Code_example.png")
print(url)