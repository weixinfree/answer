from subprocess import check_call
from PIL import Image
from ocr import ocr
import baidu
from typing import List
from termcolor import colored
from config import CUT_BOX


def take_screenshot() -> str:
    image_name = 'q.png'
    check_call(f'and_screencap {image_name}', shell=True)

    return image_name


def prepare_img(img: str) -> str:
    crop_image = 'cq.jpg'
    Image.open(img).crop(CUT_BOX).convert('L').save(crop_image)

    return crop_image


def trans2question(text):
    word_list = [w['words'] for w in text['words_result']]
    count = len(word_list)
    if count >= 4:
        return ''.join(word_list[:-3]), word_list[-3:]

    print('error, can not parse question!', word_list)


def guess_answer(q: str, options: List[str]):
    baidu.search(q, options)


def main():
    print()
    print('--' * 20, 'new question', '--' * 20)

    shot = prepare_img(take_screenshot())

    text = ocr(shot)

    question, options = trans2question(text)

    print("question: >>> ", question, options)
    guess_answer(question, options)


if __name__ == '__main__':
    while True:
        s = input('start with any input: >>> ')
        if s.strip() == 'exit':
            break
        try:
            main()
        except Exception as e:
            print(colored(f'ERROR!! {e}', 'yellow'))
