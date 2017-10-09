import requests
from datetime import datetime
from PIL import Image


def save_verification_code(_):
    """TODO: Docstring for get_verification_code.
    """
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    url = 'http://www.miitbeian.gov.cn/getVerifyCode?80'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'}
    r = requests.get(url=url, headers=headers)
    with open(f"{timestamp}.jpg", 'wb') as f:
        f.write(r.content)


for i in range(5):
    save_verification_code(1)

threshold = 140
table = [ 0 if i < threshold else 1 for i in range(256)]

#  im = Image.open('./20170926124725844258.jpg')
#  im_l = im.convert('L')
#  im_gray = im_l.point(table, '1')
#  im_gray.show()

from image import ImageCaptcha  # pip install captcha
from PIL import Image
image = ImageCaptcha(width=200, height=60, font_sizes=[33, 36, 38], rand_rate=0.5, offset_rate=1)
captcha = image.generate("94FR54")
im = Image.open(captcha)
im.show()
