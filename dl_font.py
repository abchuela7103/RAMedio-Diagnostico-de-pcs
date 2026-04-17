import urllib.request
import os

font_dir = os.path.abspath("agente")
if not os.path.exists(font_dir):
    os.makedirs(font_dir)

url = "https://github.com/twbs/icons/raw/main/font/fonts/bootstrap-icons.ttf"
dest = os.path.join(font_dir, "bootstrap-icons.ttf")

urllib.request.urlretrieve(url, dest)
print("Font downloaded to", dest)
