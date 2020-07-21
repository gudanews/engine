import sys
import urllib
import urllib.request

def download_image_from_url(url,filename):
    if sys.version[0] =='3':
        urllib.request.urlretrieve(url, filename)
    if sys.version[0] =='2':
        urllib.urlretrieve(url, filename)
download_image_from_url('https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png','image.png')