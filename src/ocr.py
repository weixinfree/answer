#!/usr/bin/env python3

from aip import AipOcr
from config import *


client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


def ocr(file: str):
    """ 读取图片 """
    def get_file_content(filePath):
        with open(filePath, 'rb') as fp:
            return fp.read()

    image = get_file_content(file)

    """ 调用通用文字识别, 图片参数为本地图片 """
    # client.basicGeneral(image)

    """ 如果有可选参数 """
    options = {}
    options["language_type"] = "CHN_ENG"
    options["detect_direction"] = "true"
    options["detect_language"] = "true"
    options["probability"] = "true"

    """ 带参数调用通用文字识别, 图片参数为本地图片 """
    result = client.basicGeneral(image, options)

    return result


if __name__ == '__main__':
    import sys
    for file in sys.argv[1:]:
        ocr(file)
