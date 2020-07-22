import sys
import os
import random
import string
from datetime import date

TODAY = date.today()

WEBSITE_BASE_PATH = "/var/www/html"
IMAGE_BASE_PATH = "/var/www/html/images"
IMAGE_PATH = os.path.join(IMAGE_BASE_PATH, str(TODAY.year), "%02d-%02d" % (TODAY.month, TODAY.day))

def _get_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result

def save_image_from_url(url):
    name = _get_random_alphanumeric_string(32) + ".png"
    if not os.path.exists(IMAGE_PATH):
        os.makedirs(IMAGE_PATH)
    img_file = os.path.join(IMAGE_PATH, name)
    if sys.version[0] =='3':
        import urllib.request
        urllib.request.urlretrieve(url, img_file)
    if sys.version[0] =='2':
        import urllib
        urllib.urlretrieve(url, img_file)
    return os.path.relpath(img_file, WEBSITE_BASE_PATH)