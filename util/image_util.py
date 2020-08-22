import sys
import os
from datetime import date
from PIL import Image, ImageOps
from util.common import LoggedTestCase
import unittest
from util.config_util import Configure
import logging
from util import generate_random_alphanumeric_string, create_parent_folders, human_format
from typing import List, Dict, Tuple, Optional, Any


logger = logging.getLogger("Util.Image")

TODAY = date.today()

config = Configure()

WEBSITE_BASE_PATH = config.setting["website_path"]
IMAGE_BASE_PATH = config.setting["image_path"]
IMAGE_PATH = os.path.join(IMAGE_BASE_PATH, str(TODAY.year), "%02d" % TODAY.month, "%02d" % TODAY.day)

IMAGE_WIDTH = 648
IMAGE_HEIGHT = 365
THUMBNAIL_WIDTH = 144
THUMBNAIL_HEIGHT = 108
DEFAULT_FILLING = (255, 255, 255)
IMAGE_PIXEL_MIN = 20


class ImageHelper:

    def __init__(self, url, path=None):
        # type: (str, Optional[str]) -> None
        self.url = url
        if not path:
            _name = generate_random_alphanumeric_string(24) + ".jpg"
            path = os.path.join(IMAGE_PATH, _name)
        elif not os.path.isabs(path):
            path = os.path.normpath(os.path.join(WEBSITE_BASE_PATH, path))
        self.path = path
        self._thumbnail = None

    @property
    def thumbnail(self):
        if not self._thumbnail:
            name, extension = os.path.splitext(os.path.basename(self.path))
            self._thumbnail = os.path.join(os.path.dirname(self.path), name + "_TIMG" + extension)
        return self._thumbnail

    @property
    def db_path(self):
        return os.path.relpath(self.path, WEBSITE_BASE_PATH)

    @property
    def db_thumbnail(self):
        if self.thumbnail:
            return os.path.relpath(self.thumbnail, WEBSITE_BASE_PATH)

    def is_image_valid(self, path=None):
        # type: (Optional[str]) -> bool
        if not path:
            path = self.path
        size = self.get_image_size(path)
        for pixel in size:
            if pixel < IMAGE_PIXEL_MIN:
                return False
        return True

    def get_image_size(self, path=None):
        # type: (Optional[str]) -> Tuple
        if not path:
            path = self.path
        with Image.open(path) as img:
            return img.size # (width, height) format

    def download_image(self, url=None, path=None, generate_thumbnail=False, keep_original=False):
        # type: (Optional[str], Optional[str], Optional[bool], Optional[bool]) -> bool
        if not url:
            url = self.url
        if not path:
            path = self.path
        create_parent_folders(path)
        result = None
        try:
            if sys.version[0] =='3':
                import urllib.request
                result = urllib.request.urlretrieve(url, path)
            elif sys.version[0] =='2':
                import urllib
                result = urllib.urlretrieve(url, path)
            file_size = int(result[1]["Content-Length"]) if "Content-Length" in result[1] else 0
            logger.info("Image file [%s] downloaded size [%s]" % (path, human_format(file_size)))
        except Exception as e:
            logger.warning("%s" % e)
            logger.warning("Error when download image [%s]" % url)
            return False
        if self.is_image_valid():
            if generate_thumbnail:
                self.generate_thumbnail()
            if not keep_original:
                self.resize(IMAGE_WIDTH, IMAGE_HEIGHT)
                self.cropping(IMAGE_WIDTH, IMAGE_HEIGHT)
            return True
        logger.warning("Image link [%s] ist invalid" % self.url)
        return False

    def generate_thumbnail(self):
        # type: () -> None
        self.resize(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, src_path=self.path, dst_path=self.thumbnail)
        self.cropping(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT, src_path=self.thumbnail, dst_path=self.thumbnail)
        logger.debug("Creating thumbnail image [%s]" % self.thumbnail)


    def resize(self, width, height, keep_aspect_ratio=True, for_chopping=True, src_path=None, dst_path=None):
        # type: (int, int, Optional[bool], Optional[bool], Optional[str], Optional[str]) -> Tuple
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
                ratio = max(float(width / width_current), float(height / height_current)) if for_chopping \
                    else min(float(width / width_current), float(height / height_current))
                size = tuple([int(i*ratio) for i in img.size])
            img = img.resize(size, Image.ANTIALIAS)
            create_parent_folders(dst_path)
            rgb_img = img.convert('RGB')
            rgb_img.save(dst_path)
        logger.debug("Image file [%s] resized to resolution %s" % (dst_path, str(size)))
        return size

    def padding(self, width, height, src_path=None, dst_path=None, fill=DEFAULT_FILLING):
        # type: (int, int, Optional[str], Optional[str], Optional[str]) -> Tuple
        if not src_path:
            src_path = self.path
        if not dst_path:
            dst_path = src_path
        size = (width, height)
        with Image.open(src_path) as img:
            width_current, height_current = img.size # (width, height) format
            if width < width_current or height < height_current or size == img.size: # cannot padding
                return img.size
            # create a new image and paste the resized on it
            with Image.new("RGB", size, fill) as new_img:
                width_delta = width - width_current
                height_delta = height - height_current
                new_img.paste(img, (width_delta//2, height_delta//2))
                create_parent_folders(dst_path)
                rgb_img = new_img.convert('RGB')
                rgb_img.save(dst_path)
        logger.debug("Image file [%s] padded to resolution %s" % (dst_path, str(size)))
        return size

    def cropping(self, width, height, src_path=None, dst_path=None):
        # type: (int, int, Optional[str], Optional[str]) -> Tuple
        if not src_path:
            src_path = self.path
        if not dst_path:
            dst_path = src_path
        size = (width, height)
        with Image.open(src_path) as img:
            width_current, height_current = img.size # (width, height) format
            if width > width_current or height > height_current or size == img.size: # cannot cropping
                return img.size
            width_delta = width_current - width
            height_delta = height_current - height
            img = img.crop((width_delta//2, height_delta//2, width_current-(width_delta//2), height_current-(height_delta//2)))
            create_parent_folders(dst_path)
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
            self.image.download_image(generate_thumbnail=False)
            self.image.resize(640, 480, keep_aspect_ratio=False)

    def test_download_url(self):
        """skip_setup"""
        self.image.download_image(keep_original=False, generate_thumbnail=True)
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
        self.image.cropping(320, 320)
        self.assertEqual(self.image.get_image_size(), (320, 320))

    def test_resize_no_keep_ratio(self):
        self.image.resize(320, 500, keep_aspect_ratio=False)
        self.assertEqual(self.image.get_image_size(), (320, 500))

    def test_padding(self):
        self.image.padding(800, 800)
        self.assertEqual(self.image.get_image_size(), (800, 800))

    def test_cropping(self):
        self.image.cropping(400, 400)
        self.assertEqual(self.image.get_image_size(), (400, 400))


if __name__ == "__main__":
    unittest.main()
