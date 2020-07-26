import sys
import os
import random
import string
from datetime import date
from PIL import Image, ImageOps
from util.common import LoggedTestCase
import unittest
from util.config_util import Configure
import logging
from math import log, floor

logger = logging.getLogger("Util.Image")

TODAY = date.today()

config = Configure()

WEBSITE_BASE_PATH = config.setting["website_path"]
IMAGE_BASE_PATH = config.setting["image_path"]
IMAGE_PATH = os.path.join(IMAGE_BASE_PATH, str(TODAY.year), "%02d-%02d" % (TODAY.month, TODAY.day))

IMAGE_WIDTH = 780
IMAGE_HEIGHT = 538
THUMBNAIL_WIDTH = 300
THUMBNAIL_HEIGHT = 208
DEFAULT_FILLING = (255, 255, 255)
IMAGE_PIXEL_MIN = 20

def _generate_random_alphanumeric_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    result = ''.join((random.choice(letters_and_digits) for i in range(length)))
    return result

def human_format(number):
    units = ['', 'K', 'M', 'G', 'T', 'P']
    k = 1024.0
    magnitude = int(floor(log(number, k)))
    return '%.2f%s' % (number / k**magnitude, units[magnitude])

class ImageHelper:

    def __init__(self, url, path=None):
        self.url = url
        if not path:
            _name = _generate_random_alphanumeric_string(24) + ".jpg"
            path = os.path.join(IMAGE_PATH, _name)
        elif not os.path.isabs(path):
            path = os.path.normpath(os.path.join(WEBSITE_BASE_PATH, path))
        self.path = path
        self._thumbnail = None

    @property
    def thumbnail(self):
        if not self._thumbnail:
            name, extension = os.path.splitext(self.path)
            self._thumbnail = os.path.join(os.path.dirname(self.path),
                                           name + '_%sX%s' % (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT) + extension)
        return self._thumbnail

    @property
    def db_path(self):
        return os.path.relpath(self.path, WEBSITE_BASE_PATH)

    @property
    def db_thumbnail(self):
        return os.path.relpath(self.thumbnail, WEBSITE_BASE_PATH)

    def _create_parent_folders(self, path):
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

    def is_image_valid(self, path=None):
        if not path:
            path = self.path
        with Image.open(path) as img:
            width_current, height_current = img.size # (width, height) format
            return width_current > IMAGE_PIXEL_MIN and height_current > IMAGE_PIXEL_MIN

    def download_image(self, url=None, path=None, thumbnail=True, keep_original=False, default=None):
        if not url:
            url = self.url
        if not path:
            path = self.path
        self._create_parent_folders(path)
        result = None
        if sys.version[0] =='3':
            import urllib.request
            result = urllib.request.urlretrieve(url, path)
        if sys.version[0] =='2':
            import urllib
            result = urllib.urlretrieve(url, path)
        file_size = int(result[1]["Content-Length"]) if "Content-Length" in result[1] else 0
        logger.info("Image file [%s] created, size [%s]" % (path, human_format(file_size)))
        if self.is_image_valid():
            if not keep_original:
                self.resize(IMAGE_WIDTH, IMAGE_HEIGHT)
            if thumbnail:
                self._generate_thumbnail()
            return True
        logger.info("Image link [%s] ist invalid" % self.url)
        return False

    def _generate_thumbnail(self):
        size = self.resize(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, dst_path=self.thumbnail)
        logger.info("Thumbnail image [%s] created, with resolution %s" % (self.thumbnail, size))

    def resize(self, width, height, keep_aspect_ratio=True, src_path=None, dst_path=None): # Only works for shrinking size
        if not src_path:
            src_path = self.path
        if not dst_path:
            dst_path = src_path
        size = (width, height)
        with Image.open(src_path) as img:
            width_current, height_current = img.size # (width, height) format
            if width > width_current and height > height_current:
                return img.size
            if keep_aspect_ratio:
                ratio = min(float(width / width_current), float(height / height_current))
                size = tuple([int(i*ratio) for i in img.size])
            if ratio < 1:
                img.thumbnail(size, Image.ANTIALIAS)
            self._create_parent_folders(dst_path)
            img.save(dst_path)
        if size != (width, height):
            return self._padding(width, height, src_path=dst_path, dst_path=dst_path)
        logger.debug("Image file [%s] resized to resolution %s" % (dst_path, str(size)))
        return size

    def _padding(self, width, height, src_path=None, dst_path=None, fill=DEFAULT_FILLING):
        if not src_path:
            src_path = self.path
        if not dst_path:
            dst_path = src_path
        size = (width, height)
        with Image.open(src_path) as img:
            width_current, height_current = img.size # (width, height) format
            if width < width_current or height < height_current: # cannot padding
                return img.size
            # create a new image and paste the resized on it
            with Image.new("RGB", size, fill) as new_img:
                width_delta = width - width_current
                height_delta = height - height_current
                new_img.paste(img, (width_delta//2, height_delta//2))
                self._create_parent_folders(dst_path)
                new_img.save(dst_path)
        logger.debug("Image file [%s] padded to resolution %s" % (dst_path, str(size)))
        return size

    def expand(self, width, height, keep_aspect_ratio=True, src_path=None, dst_path=None, fill=DEFAULT_FILLING):
        if not src_path:
            src_path = self.path
        if not dst_path:
            dst_path = src_path
        size = (width, height)
        with Image.open(src_path) as img:
            width_current, height_current = img.size # (width, height) format
            if width < width_current and height < height_current:
                return img.size
            if keep_aspect_ratio:
                ratio = min(float(width / width_current), float(height / height_current))
                size = tuple([int(i*ratio) for i in img.size])
            width_delta = width - width_current
            height_delta = height - height_current
            with ImageOps.expand(img, (width_delta//2, height_delta//2, width_delta-(width_delta//2),
                                       height_delta-(height_delta//2)), fill) as new_img:
                self._create_parent_folders(dst_path)
                new_img.save(dst_path)
        if size != (width, height):
            return self._padding(width, height, src_path=dst_path, dst_path=dst_path)
        logger.debug("Image file [%s] expanded to resolution %s" % (dst_path, str(size)))
        return size


class TestCase(LoggedTestCase):

    def setUp(self):
        self.image = ImageHelper(url="https://s4.reutersmedia.net/resources/r/?m=02&d=20200725&t=2&i=1527081659&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6O02V",
                              path="/tmp/images/testing/testing.jpg")

    def test_download_url(self):
        self.image.download_image()
        self.assertTrue(os.path.exists(self.image.path))
        self.assertTrue(os.path.exists(self.image.thumbnail))
        with Image.open(self.image.path) as img:
            self.assertEqual(img.size, (IMAGE_WIDTH, IMAGE_HEIGHT))

    def test_resize_smaller(self):
        self.image.download_image()
        self.image.resize(640, 480)
        with Image.open(self.image.path) as img:
            self.assertEqual(img.size, (640, 480))

    def test_resize_only_height(self):
        self.image.download_image()
        self.image.resize(IMAGE_WIDTH, 480)
        with Image.open(self.image.path) as img:
            self.assertEqual(img.size, (IMAGE_WIDTH, 480))

    def test_resize_only_width(self):
        self.image.download_image()
        self.image.resize(600, IMAGE_HEIGHT)
        with Image.open(self.image.path) as img:
            self.assertEqual(img.size, (600, IMAGE_HEIGHT))

    def test_resize_smaller_width_larger_height(self):
        self.image.download_image()
        self.image.resize(480, 800)
        with Image.open(self.image.path) as img:
            self.assertEqual(img.size, (480, 800))

    def test_resize_larger_width_smaller_height(self):
        self.image.download_image()
        self.image.resize(800, 400)
        with Image.open(self.image.path) as img:
            self.assertEqual(img.size, (800, 400))

    def test_exanding_larger(self):
        self.image.download_image()
        self.image.expand(1024, 768)
        with Image.open(self.image.path) as img:
            self.assertEqual(img.size, (1024, 768))


if __name__ == "__main__":
    unittest.main()
