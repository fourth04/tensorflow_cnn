# coding: utf-8
"""
    captcha.image
    ~~~~~~~~~~~~~

    Generate Image CAPTCHAs, just the normal image CAPTCHAs you are using.
"""

import os
import random
from PIL import Image
from PIL import ImageFilter
from PIL.ImageDraw import Draw
from PIL.ImageFont import truetype
try:
    from cStringIO import StringIO as BytesIO
except ImportError:
    from io import BytesIO
try:
    from wheezy.captcha import image as wheezy_captcha
except ImportError:
    wheezy_captcha = None

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
DEFAULT_FONTS = [os.path.join(DATA_DIR, 'DroidSansMono.ttf')]

if wheezy_captcha:
    __all__ = ['ImageCaptcha', 'WheezyCaptcha']
else:
    __all__ = ['ImageCaptcha']


table = []
for i in range(256):
    table.append(i * 1.97)


class _Captcha(object):
    def generate(self, chars, format='png'):
        """Generate an Image Captcha of the given characters.

        :param chars: text to be generated.
        :param format: image file format
        """
        im = self.generate_image(chars)
        out = BytesIO()
        im.save(out, format=format)
        out.seek(0)
        return out

    def write(self, chars, output, format='png'):
        """Generate and write an image CAPTCHA data to the output.

        :param chars: text to be generated.
        :param output: output destination.
        :param format: image file format
        """
        im = self.generate_image(chars)
        return im.save(output, format=format)


class WheezyCaptcha(_Captcha):
    """Create an image CAPTCHA with wheezy.captcha."""

    def __init__(self, width=200, height=75, fonts=None):
        self._width = width
        self._height = height
        self._fonts = fonts or DEFAULT_FONTS

    def generate_image(self, chars):
        text_drawings = [
            wheezy_captcha.warp(),
            wheezy_captcha.rotate(),
            wheezy_captcha.offset(),
        ]
        fn = wheezy_captcha.captcha(
            drawings=[
                wheezy_captcha.background(),
                wheezy_captcha.text(fonts=self._fonts, drawings=text_drawings),
                wheezy_captcha.curve(),
                wheezy_captcha.noise(),
                wheezy_captcha.smooth(),
            ],
            width=self._width,
            height=self._height,
        )
        return fn(chars)


class ImageCaptcha(_Captcha):
    """Create an image CAPTCHA.

    Many of the codes are borrowed from wheezy.captcha, with a modification
    for memory and developer friendly.

    ImageCaptcha has one built-in font, DroidSansMono, which is licensed under
    Apache License 2. You should always use your own fonts::

        captcha = ImageCaptcha(fonts=['/path/to/A.ttf', '/path/to/B.ttf'])

    You can put as many fonts as you like. But be aware of your memory, all of
    the fonts are loaded into your memory, so keep them a lot, but not too
    many.

    :param width: The width of the CAPTCHA image.
    :param height: The height of the CAPTCHA image.
    :param fonts: Fonts to be used to generate CAPTCHA images.
    :param font_sizes: Random choose a font size from this parameters.
    """

    def __init__(
            self,
            width=160,
            height=60,
            fonts=None,
            font_sizes=None,
            rand_rate=0.25,
            offset_rate=0.1):
        self._width = width
        self._height = height
        self._fonts = fonts or DEFAULT_FONTS
        self._font_sizes = font_sizes or (42, 50, 56)
        self._rand_rate = rand_rate
        self._offset_rate = offset_rate
        self._truefonts = []

    @property
    def truefonts(self):
        if self._truefonts:
            return self._truefonts
        self._truefonts = tuple([
            truetype(n, s)
            for n in self._fonts
            for s in self._font_sizes
        ])
        return self._truefonts

    @staticmethod
    def create_noise_curve(image, color):
        """
        画噪点曲线
        """
        w, h = image.size
        #  第一个点的x轴，0~(1/5画布宽) 中的某个值
        x1 = random.randint(0, int(w / 5))
        #  第二个点的x轴，剩下的(4/5画布宽)~(画布宽)的某个值
        x2 = random.randint(w - int(w / 5), w)
        #  第一个点的y轴，(1/5画布高)~(4/5画布高) 中的某个值
        y1 = random.randint(int(h / 5), h - int(h / 5))
        #  第二个点的y轴，(y1)~(1/5画布高) 中的某个值
        y2 = random.randint(y1, h - int(h / 5))
        points = [x1, y1, x2, y2]
        end = random.randint(160, 200)
        start = random.randint(0, 20)
        Draw(image).arc(points, start, end, fill=color)
        return image

    @staticmethod
    def create_noise_line(image, color):
        """
        画噪点直线
        """
        w, h = image.size
        x1 = random.randint(0, w)
        y1 = random.randint(0, h)
        for i in range(random.randint(1, 4)):
            x2 = random.randint(0, w)
            y2 = random.randint(0, h)
            points = [x1, y1, x2, y2]
            Draw(image).line(points, fill = color)
            x1 = x2
            y1 = y2
        return image

    @staticmethod
    def create_noise_dots(image, color, width=3, number=30):
        draw = Draw(image)
        w, h = image.size
        while number:
            x1 = random.randint(0, w)
            y1 = random.randint(0, h)
            draw.line(((x1, y1), (x1 - 1, y1 - 1)), fill=color, width=width)
            number -= 1
        return image

    def create_captcha_image(self, chars, color, background):
        """Create the CAPTCHA image itself.

        :param chars: text to be generated.
        :param color: color of the text.
        :param background: color of the background.

        The color should be a tuple of 3 numbers, such as (0, 255, 255).
        """
        image = Image.new('RGB', (self._width, self._height), background)
        draw = Draw(image)

        def _draw_character(c):
            font = random.choice(self.truefonts)
            w, h = draw.textsize(c, font=font)

            dx = random.randint(0, 4)
            dy = random.randint(0, 6)
            im = Image.new('RGBA', (w + dx, h + dy))
            Draw(im).text((dx, dy), c, font=font, fill=color)

            # rotate，旋转，正负30度
            im = im.crop(im.getbbox())
            im = im.rotate(random.uniform(-30, 30), Image.BILINEAR, expand=1)

            # warp，弯曲
            #  dx = w * random.uniform(0.1, 0.3)
            #  dy = h * random.uniform(0.2, 0.3)
            #  x1 = int(random.uniform(-dx, dx))
            #  y1 = int(random.uniform(-dy, dy))
            #  x2 = int(random.uniform(-dx, dx))
            #  y2 = int(random.uniform(-dy, dy))
            #  w2 = w + abs(x1) + abs(x2)
            #  h2 = h + abs(y1) + abs(y2)
            #  data = (
                #  x1, y1,
                #  -x1, h2 - y2,
                #  w2 + x2, h2 + y2,
                #  w2 - x2, -y1,
            #  )
            #  im = im.resize((w2, h2))
            #  im = im.transform((w, h), Image.QUAD, data)

            return im

        images = []
        for c in chars:
            images.append(_draw_character(c))

        #  所有的字宽
        text_width = sum([im.size[0] for im in images])

        #  对比画布大小和所有的字宽大小，重新将画布拓展为最大的宽度
        width = max(text_width, self._width)
        image = image.resize((width, self._height))

        #  平均每个字多宽
        average = int(text_width / len(chars))
        #  字的边缘，相当于字与字之间的间隔
        rand = int(self._rand_rate * average)
        #  第一个字到画布最左边之间偏移像素
        offset = int(self._offset_rate * average)

        for im in images:
            w, h = im.size
            #  将文字的子图合并到背景上，注意offset第一次为“第一个字到画布最左边之间偏移像素”，第二次则为在此基础上加上当前字宽，再加上字的边缘大小或者不减
            mask = im.convert('L').point(table)
            #  原来的写法，验证码基本保持在中轴线的位置，开始写字的y轴值改为从0~(画布高-字高)中的值
            #  image.paste(im, (offset, int((self._height - h) / 2)), mask)
            image.paste(im, (offset, random.randint(0, int((self._height - h)))), mask)
            offset = offset + w + random.randint(0, rand)

        if width > self._width:
            image = image.resize((self._width, self._height))

        return image

    def generate_image(self, chars):
        """Generate the image of the given characters.

        :param chars: text to be generated.
        """
        background = random_color(238, 255)
        color = random_color(0, 200, random.randint(220, 255))
        im = self.create_captcha_image(chars, color, background)
        #  self.create_noise_dots(im, color)
        #  self.create_noise_curve(im, color)
        self.create_noise_line(im, color)
        im = im.filter(ImageFilter.SMOOTH)
        return im


def random_color(start, end, opacity=None):
    red = random.randint(start, end)
    green = random.randint(start, end)
    blue = random.randint(start, end)
    if opacity is None:
        return (red, green, blue)
    return (red, green, blue, opacity)

if __name__ == "__main__":
    from PIL import Image
    image = ImageCaptcha(width=200, height=60, fonts=[r'C:\Windows\Fonts\ARIALN.TTF'], font_sizes=[35, 37, 40], rand_rate=0.25, offset_rate=1)
    captcha = image.generate("94FR54")
    im = Image.open(captcha)
    im.show()
