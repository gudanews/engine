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
        if self.thumbnail:
            return os.path.relpath(self.thumbnail, WEBSITE_BASE_PATH)

    def _create_parent_folders(self, path):
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)

    def is_image_valid(self, path=None):
        if not path:
            path = self.path
        size = self.get_image_size(path)
        for pixel in size:
            if pixel < IMAGE_PIXEL_MIN:
                return False
        return True

    def get_image_size(self, path=None):
        if not path:
            path = self.path
        with Image.open(path) as img:
            return img.size # (width, height) format

    def download_image(self, url=None, path=None, generate_thumbnail=True, keep_original=False, default=None):
        if not url:
            url = self.url
        if not path:
            path = self.path
        self._create_parent_folders(path)
        result = None
        try:
            if sys.version[0] =='3':
                import urllib.request
                result = urllib.request.urlretrieve(url, path)
            elif sys.version[0] =='2':
                import urllib
                result = urllib.urlretrieve(url, path)
            file_size = int(result[1]["Content-Length"]) if "Content-Length" in result[1] else 0
            logger.info("Image file [%s] created, size [%s]" % (path, human_format(file_size)))
        except:
            logger.warning("Error when download image [%s]" % url)
            return False
        if self.is_image_valid():
            if generate_thumbnail:
                self.generate_thumbnail()
            if not keep_original:
                width, height = self.resize(IMAGE_WIDTH, IMAGE_HEIGHT)
                if (width, height) != (IMAGE_WIDTH, IMAGE_HEIGHT):
                    return self.padding(IMAGE_WIDTH, IMAGE_HEIGHT)
            return True
        logger.warning("Image link [%s] ist invalid" % self.url)
        return False

    def generate_thumbnail(self):
        (width, height) = self.resize(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, for_padding=False,
                                      src_path=self.path, dst_path=self.thumbnail)
        if (width, height) != (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT):
            logger.debug("Creating thumbnail image [%s]" % self.thumbnail)
            self.cropping(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, src_path=self.thumbnail, dst_path=self.thumbnail)

    def resize(self, width, height, keep_aspect_ratio=True, for_padding=True, src_path=None, dst_path=None):
        # for_cropping if not for_padding
        if not src_path:
            src_path = self.path
        if not dst_path:
            dst_path = src_path
        size = (width, height)
        with Image.open(src_path) as img:
            width_current, height_current = img.size # (width, height) format
            if width == width_current and height == height_current:
                return img.size
            if keep_aspect_ratio:
                ratio = min(float(width / width_current), float(height / height_current)) if for_padding \
                    else max(float(width / width_current), float(height / height_current))
                size = tuple([int(i*ratio) for i in img.size])
            img = img.resize(size, Image.ANTIALIAS)
            self._create_parent_folders(dst_path)
            rgb_img = img.convert('RGB')
            rgb_img.save(dst_path)
        logger.debug("Image File [%s] Resized To Resolution %s" % (dst_path, str(size)))
        return size

    def padding(self, width, height, src_path=None, dst_path=None, fill=DEFAULT_FILLING):
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
                rgb_img = new_img.convert('RGB')
                rgb_img.save(dst_path)

    def cropping(self, width, height, src_path=None, dst_path=None):
        if not src_path:
            src_path = self.path
        if not dst_path:
            dst_path = src_path
        size = (width, height)
        with Image.open(src_path) as img:
            width_current, height_current = img.size # (width, height) format
            if width > width_current or height > height_current: # cannot cropping
                return img.size
            width_delta = width_current - width
            height_delta = height_current - height
            img = img.crop((width_delta//2, height_delta//2, width_current-(width_delta//2), height_current-(height_delta//2)))
            self._create_parent_folders(dst_path)
            rgb_img = img.convert('RGB')
            rgb_img.save(dst_path)
        logger.debug("Image file [%s] cropped to resolution %s" % (dst_path, str(size)))
        return size


class TestCase(LoggedTestCase):

    def setUp(self):
        self.image = ImageHelper(url="https://s4.reutersmedia.net/resources/r/?m=02&d=20200728&t=2&i=1527434485&w=800&fh=&fw=&ll=&pl=&sq=&r=LYNXNPEG6R1DY",
                              path="/tmp/images/testing/testing.jpg")
        name = self.shortDescription()
        if name != "skip_setup":
            self.image.download_image(keep_original=True, generate_thumbnail=False)
            self.image.resize(640, 480, keep_aspect_ratio=False)

    def test_download_url(self):
        """skip_setup"""
        self.image.download_image()
        self.assertTrue(os.path.exists(self.image.path))
        self.assertTrue(os.path.exists(self.image.thumbnail))
        self.assertEqual(self.image.get_image_size(), (IMAGE_WIDTH, IMAGE_HEIGHT))
        self.assertEqual(self.image.get_image_size(self.image.thumbnail), (THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))

    def test_resize_smaller(self):
        self.image.resize(320, 240)
        self.assertEqual(self.image.get_image_size(), (320, 240))

    def test_resize_larger(self):
        self.image.resize(1024, 768)
        self.assertEqual(self.image.get_image_size(), (1024, 768))

    def test_resize_keep_ratio(self):
        self.image.resize(320, 320)
        self.assertEqual(self.image.get_image_size(), (320, 240))

    def test_resize_no_keep_ratio(self):
        self.image.resize(320, 320, keep_aspect_ratio=False)
        self.assertEqual(self.image.get_image_size(), (320, 320))

    def test_padding(self):
        self.image.padding(800, 800)
        self.assertEqual(self.image.get_image_size(), (800, 800))

    def test_cropping(self):
        self.image.cropping(400, 400)
        self.assertEqual(self.image.get_image_size(), (400, 400))


if __name__ == "__main__":
    unittest.main()
