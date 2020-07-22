import sys
import urllib
import urllib.request
import os
def download_image_from_url(url,filename):
    if sys.version[0] =='3':
        urllib.request.urlretrieve(url, filename)
    if sys.version[0] =='2':
        urllib.urlretrieve(url, filename)
def find_image_path(image):
    return os.path.abspath(image)
#download_image_from_url('https://s2.reutersmedia.net/resources/r/?m=02&d=20200721&t=2&i=1526623666&w=1100&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6K1Q4','1.png')