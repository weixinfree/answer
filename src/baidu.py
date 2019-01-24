import requests
from typing import List
import re


def _prepare_options(options: List[str]) -> List[str]:
    return [re.sub(r'[^\d\w]', '', op) for op in options]


def _prepare_question(question: str) -> str:
    return question.rstrip().rstrip('?').rstrip('？')


def search(q: str, options: List[str]) -> str:

    q = _prepare_question(q)
    options = _prepare_options(options)

    query = q + ' ' + ' '.join(options)
    if len(query) > 38:
        query = re.sub(r'[^\d\w]', ' ', query)
        query = re.sub(r'\s+', ' ', query)

    if len(query) > 38:
        query = query[len(query) - 38:]

    print('query: ', query)

    headers = {'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
               'Accept - Encoding': 'gzip, deflate',
               'Accept-Language': 'zh-Hans-CN, zh-Hans; q=0.5',
               'Connection': 'Keep-Alive',
               'Host': 'baidu.com',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36 Edge/15.15063'}

    URL = f'http://www.baidu.com/s?ie=utf-8&wd={query}'
    return requests.get(URL, headers=headers).text
