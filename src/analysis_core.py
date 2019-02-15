from typing import List, Set, Tuple
import re
import jieba
from functools import partial
from itertools import groupby
from collections import defaultdict
from termcolor import colored


class Result:
    pass


cut = partial(jieba.cut, cut_all=True)


def _doc_seg(docs: List[str]) -> List[str]:
    words = ','.join([','.join(re.findall(r'([\u4e00-\u9fa5]+)', doc, re.DOTALL))
                      for doc in docs])

    return [seg for seg in cut(words) if seg.strip()]


def _question_seg(q: str) -> Set[str]:
    return set(cut(q))


def _options_seg(options: List[str]) -> List[Set[str]]:
    segs = [set(cut(option)) for option in options]

    return [seg for seg in segs]


def _mark(w: str, q: Set[str], options: List[Set[str]]):

    ops = []
    for i, words in enumerate(options):
        if w in words:
            ops.append(str(i))

    if len(ops) == 1:
        return ops[0]

    if w in q:
        return 'q'

    return None


def _compute_score(index: int, segs: List[Tuple[str, int]]):
    tag, _ = segs[index]
    if tag == 'q':
        return tag, -1

    score = 0
    if index + 1 < len(segs):
        t, s = segs[index + 1]
        if t == 'q':
            score += s ** 1.2
    if index - 1 > 0:
        t, s = segs[index - 1]
        if t == 'q':
            score += s ** 0.5
    return tag, score


def analysis(question: str, options: List[str], docs: List[str]) -> Result:
    doc_segs = _doc_seg(docs)
    q_segs = _question_seg(question)
    options_segs = _options_seg(options)

    marks = [_mark(w, q_segs, options_segs) for w in doc_segs]
    marks = [m for m in marks if m]

    seg = [(tag, len(list(li))) for tag, li in groupby(marks)]
    print('-' * 100)
    print(seg)

    scores = defaultdict(int)
    for i in range(len(seg)):
        tag, s = _compute_score(i, seg)
        if s >= 0:
            scores[tag] += s

    print('-' * 100)
    print()

    if not scores.values():
        return
    max_score = max(scores.values())
    items = list(scores.items())
    items.sort()
    for o, s in items:
        color = 'red' if s == max_score else 'white'
        print(colored(f'{o}). {options[int(o)]}: {s/max_score:.2f}', color))

    print()
    print('-' * 100)
