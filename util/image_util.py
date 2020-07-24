import sys
import os
import random
import string
from datetime import date
from PIL import Image
TODAY = date.today()

WEBSITE_BASE_PATH = "/var/www/html/wordpress"
IMAGE_BASE_PATH = "/var/www/html/wordpress/images"
#WEBSITE_BASE_PATH = "."
#IMAGE_BASE_PATH = "./tmp/"
IMAGE_PATH = os.path.join(IMAGE_BASE_PATH, str(TODAY.year), "%02d-%02d" % (TODAY.month, TODAY.day))

def get_resized_img(img_path, video_size):
    img = Image.open(img_path)
    width, height = video_size
    video_ratio = width / height
    img_ratio = img.size[0] / img.size[1]
    if video_ratio >= 1:
        if img_ratio <= video_ratio:
            width_new = int(height * img_ratio)
            size_new = width_new, height
        else:
            height_new = int(width / img_ratio)
            size_new = width, height_new
    else:
        if img_ratio >= video_ratio:
            height_new = int(width / img_ratio)
            size_new = width, height_new
        else:
            width_new = int(height * img_ratio)
            size_new = width_new, height
    return img.resize(size_new, resample=Image.LANCZOS)

def merge_two_images(img_file, white_path):
    white_path = os.path.abspath('white.png')
    white_path = white_path.replace('\\', '/').replace('crawler', 'util')
    image = get_resized_img(img_file, (400, 400))
    image.save(img_file)
    white = Image.open(white_path)
    white = white.resize((400, 400))
    white.save(white_path)
    white = Image.open(white_path)
    image_copy = white.copy()
    image = Image.open(img_file)
    image_copy.paste(image, ((white.width - image.width) // 2, (white.height - image.height) // 2))
    image_copy.save(img_file)

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


if __name__ == "__main__":
    pass