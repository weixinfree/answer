from subprocess import check_call
from PIL import Image
from ocr import ocr
import baidu
from analysis_core import analysis
from typing import List
from termcolor import colored
from config import QUESTION_BOX, OPTION_BOX
import traceback


def take_screenshot() -> str:
    image_name = 'q.png'
    check_call(
        f"adb shell screencap /sdcard/screencap.png; adb pull /sdcard/screencap.png {image_name}", shell=True)

    return image_name


def prepare_img(img: str) -> str:
    question = 'question.jpg'
    options = 'options.jpg'
    Image.open(img).crop(QUESTION_BOX).convert('L').save(question)
    Image.open(img).crop(OPTION_BOX).convert('L').save(options)

    return question, options


def get_options(options: str) -> List[str]:
    return parse(options)


def parse(img: str) -> List[str]:
    text = ocr(img)
    return [item['words'] for item in text['words_result']]


def get_question(question: str) -> str:
    return ''.join(parse(question))


def main():
    print()
    print('--' * 20, 'new question', '--' * 20)

    q, o = prepare_img(take_screenshot())

    question = get_question(q)
    options = get_options(o)

    print("question: >>> ", question, options)
    search_reuslt = baidu.search(question, options)

    analysis(question, options, [search_reuslt])


def test():
    q, o = prepare_img('q.png')

    question = get_question(q)
    options = get_options(o)

    print("question: >>> ", question, options)
    search_reuslt = baidu.search(question, options)

    analysis(question, options, [search_reuslt])


if __name__ == '__main__':
    # test()
    while True:
        s = input('start with any input: >>> ')
        if s.strip() == 'exit':
            break
        try:
            main()
        except Exception as e:
            print(colored(f'ERROR!! {e}', 'yellow'))
            print(traceback.format_exc())
