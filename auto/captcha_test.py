# from captcha.image import ImageCaptcha

# # 创建一个 ImageCaptcha 实例
# image = ImageCaptcha()

# # 生成验证码内容（可以自定义字符集）
# captcha_text = "AB12"  # 你可以随机生成字符，比如使用 random 库

# # 生成验证码图像
# image_data = image.generate(captcha_text)

# # 保存图像到文件
# image.write(captcha_text, "captcha.png")

# print("✅ 验证码生成成功！")

from captcha.image import ImageCaptcha
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import numpy as np

def random_text(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def generate_hard_captcha(text=None, width=200, height=80):
    if not text:
        text = random_text()

    # 使用 captcha 生成基础图像
    image_captcha = ImageCaptcha(width=width, height=height)
    image = image_captcha.generate_image(text)

    # 转换为 PIL 图像用于处理
    draw = ImageDraw.Draw(image)

    # 添加干扰线
    for _ in range(10):
        x1, y1 = random.randint(0, width), random.randint(0, height)
        x2, y2 = random.randint(0, width), random.randint(0, height)
        draw.line(((x1, y1), (x2, y2)), fill=(random.randint(0, 150),)*3, width=2)

    # 添加噪声点
    for _ in range(200):
        x, y = random.randint(0, width), random.randint(0, height)
        draw.point((x, y), fill=(random.randint(0, 255),)*3)

    # 模糊处理
    image = image.filter(ImageFilter.GaussianBlur(1.2))

    # 保存并返回路径
    filename = f"hard_captcha_{text}.png"
    image.save(filename)
    print(f"✅ 高难度验证码已生成: {filename} （内容为: {text}）")
    return filename, text

# 生成示例
generate_hard_captcha()

