import pytesseract
import pyautogui
import re
from PIL import Image
import numpy as np

# 截图坐标初始化
x, y, width, height= 190, 670, 100, 30


def simple_binarize(input_image, threshold=200):
    """
    最简单的二值化函数
    """
    # 打开图片并转为灰度
    img_grey = input_image.convert('L')
    img_array = np.array(img_grey, 'uint8')

    # 二值化
    binary_array = (img_array > threshold).astype(np.uint8) * 255

    # 保存
    binary_image = Image.fromarray(binary_array)
    print(f"二值化完成")

    return binary_image

def simple_capture_and_recognize(x, y, width, height):
    """简化版本的验证码识别"""
    try:
        # 截图
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        binary_img = simple_binarize(screenshot)

        screenshot.save('screenshot.png')
        binary_img.save('binary_img.png')

        # 直接识别（不进行复杂预处理）
        custom_config = r'--oem 3 --psm 8'
        text = pytesseract.image_to_string(screenshot, config=custom_config)

        print(text)

        test = re.sub(r'\D', '', text)

        print(test)
        # 清理结果
        text = ''.join(filter(str.isalnum, text))

        return text, screenshot, True if text else False

    except Exception as e:
        print(f"识别过程中出错: {e}")
        return None, None, False

def main():
    simple_capture_and_recognize(x, y, width, height)


if __name__ == "__main__":
    main()