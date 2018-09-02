import requests
import re
import jieba
from typing import List, Dict, Callable
from dataclasses import dataclass
import math
from collections import defaultdict
import operator
from itertools import groupby
from termcolor import colored
from functools import wraps
import re


def weight(weight: int = 100, curve: Callable[[int, int], float] = lambda x, y: x / y):
    def inner(fn):
        @wraps(fn)
        def compute_weight_after(*args, **kargs):
            result = fn(*args, **kargs)
            print()
            print('ANALYSIS:', fn.__name__, result)

            max_score = max(score for _, score in result.items())

            def compute_score(score):
                percent = curve(score, max_score)
                assert percent >= 0 and percent <= 1

                return max(1, int(percent * weight))

            final_scores = {index: compute_score(score) for index, score in result.items()}
            print('ANALYSIS SCORE:', fn.__name__, final_scores)
            return final_scores

        return compute_weight_after
    return inner


Question = 0
Option = 1


@dataclass
class Lable:
    word: str
    lable: int
    index: int


@dataclass
class SearchResult:
    q: str
    options: List[str]
    query_words: List[str]
    response: str
    labling: List[Lable]


@weight(100, curve=lambda x, y: 1 / x)
def _analysis_distance(result: SearchResult):
    labling = result.labling

    distance = defaultdict(int)

    last_q = 0
    for index, lable in enumerate(labling):
        if lable.lable == Question:
            last_q = index
            continue

        distance[lable.index] += (index - last_q) ** 2

    return dict(distance)


@weight(100)
def _analysis_seq(result: SearchResult):
    labling = result.labling

    def compute_score(lables):
        first_lable = lables[0]
        match_len = len(first_lable.word)
        for index, lable in enumerate(lables[1:]):
            if lable.index == first_lable.index:
                match_len += len(lable.word) * (index + 1)
            else:
                break

        return first_lable.index, match_len * 2

    result = defaultdict(int)
    for key, item in groupby(labling, operator.attrgetter('lable')):
        if key == Option:
            lables = list(item)
            index, score = compute_score(lables)
            result[index] += score

    return dict(result)


@weight(weight=2)
def _analysis_count(result: SearchResult) -> Dict[int, int]:
    labling = result.labling
    options = [lable.index for lable in labling if lable.lable == Option]

    return {index: options.count(index) for index in range(len(result.options))}


def _prepare_options(options: List[str]) -> List[str]:
    return [re.sub(r'[^\d\w]', '', op) for op in options]


def _prepare_question(question: str) -> str:
    return question.rstrip().rstrip('?').rstrip('？')


def _baidu(q: str, options: List[str]) -> str:

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
    return requests.get(URL, headers=headers)


def search(q: str, options: List[str]):

    query_words = [w for w in jieba.cut_for_search(q) if len(w) >= 2]

    res = _baidu(q, options)

    keywords = re.findall(r'<em>(.*?)</em>', res.text, re.DOTALL)
    print(keywords)
    ems = [w for item in keywords for w in jieba.lcut(item)]
    labling = _labling(query_words, options, ems)

    print(', '.join(f'<{lable.word}|{lable.lable}|{lable.index}>' for lable in labling))

    search_result = SearchResult(q, options, query_words, res.text, labling)

    analysis_result = {index: 1 for index in range(len(options))}

    def _update(scores: Dict[int, int]):
        if not scores:
            return

        for index, score in scores.items():
            analysis_result[index] = analysis_result[index] * score

    for analy in [_analysis_count, _analysis_seq]:
        _update(analy(search_result))

    scores = [(index, options[index], score) for index, score in analysis_result.items()]
    scores.sort()

    _max = max(score for _, _, score in scores)

    print('>' * 20, 'suggest answers', '<' * 20)
    for item in scores:
        index, option, score = item
        color = 'red' if score == _max else 'white'
        print(colored(f'{index+1}). {option}: {score/_max:.2f}', color))
    print()


def _labling(query_words: List[str], options: List[str], ems: List[str]) -> List[Lable]:
    labling = []
    for item in ems:
        if item in query_words and len(item) > 1:
            index = query_words.index(item)
            labling.append(Lable(item, Question, index))
            continue

        for _index, option in enumerate(options):
            if item in option:
                labling.append(Lable(item, Option, _index))

    return labling


if __name__ == '__main__':
    search('演绎了经典曲目《追梦人》,被誉为“帽子歌后”的是哪位女歌手?', ['邓丽君', '凤飞飞', '徐小凤'])
