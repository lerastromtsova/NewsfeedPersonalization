import requests
from bs4 import BeautifulSoup
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import defaultdict
import nltk
from nltk.corpus import wordnet as wn
import math
from bottle import route, request, run, template
from bottle import redirect


def get_news(source):
    """[{'author': 'evo_9',
        'comments': 0,
        'points': 1,
        'title': 'Daily Action – Sign Up to Join the Resistance',
        'url': 'https://dailyaction.org/'},"""
    assert requests.get(source).status_code != 404, "Страницы не существует"
    r = requests.get(source)
    page = BeautifulSoup(r.text, 'html.parser')
    tr_list = page.table.findAll('tr', 'athing')
    subtext = page.table.findAll('td', 'subtext')
    answ_list = []
    for i in range(len(tr_list)-1):
        try:
            title = tr_list[i].find('a', 'storylink').text
            url = tr_list[i].find('span', 'sitestr').text
            likes = int(subtext[i].find('span', 'score').text.split(' ')[0])
            author = subtext[i].find('a', 'hnuser').text
            comments = subtext[i].findAll('a')[-1].text
            if comments == 'discuss':
                comments = 0
            else:
                comments = int(comments.split('\xa0')[0])
            answ_list.append({'author': author, 'comments': comments, 'points': likes, 'title': title, 'url': url})
        except AttributeError:
            pass
    # global next
    # next = page.table.find('a','morelink')['href']
    return answ_list

Base = declarative_base()


class News(Base):
    __tablename__ = "news"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)

engine = create_engine("sqlite:///news.db")
Base.metadata.create_all(bind=engine)


session = sessionmaker(bind=engine)
s = session()


def tokenize(title):
    tokens = nltk.word_tokenize(title)  # список слов в новости
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()
        if wn.morphy(tokens[i]) != None:
            tokens[i] = wn.morphy(tokens[i])  # используем morphy, чтобы убрать множ число и формы глаголов, а также понижаем регистр
    return tokens


def train(sample):
    classes, freq = defaultdict(lambda: 0), defaultdict(lambda: 0)
    stops = open('stop-words.txt', 'r')
    punkts = [',', '.', '?', '!', ':', ';', '%', '(', ')', '*']
    for news in sample:
        tokens = tokenize(news.title)
        for i in range(len(tokens)):
            for p in punkts:
                if p in tokens[i]:
                    tokens[i] = tokens[i].replace(p, '')  # deleting the punctuation
            if tokens[i] not in stops:  # deleting stop-words
                freq[news.label, tokens[i]] += 1  # считаем соотношение слов и лейблов
        classes[news.label] += 1  # считаем количество лейблов "good","maybe","never"
    for label, token in freq:
        freq[label, token] /= classes[label]*10**8
    for c in classes:
        classes[c] /= len(sample)*10**8
    return classes, freq  # return P(C) and P(O|C)

P_C, P_O_C = train(s.query(News).all())


def classifier(data):
    summ = defaultdict(lambda: 0)
    tokens = tokenize(data)
    for label in ['good', 'maybe', 'never']:
            if P_C[label] != 0:
                summ[label] = math.log(P_C[label])
            else:
                summ[label] = 0
    for token in tokens:
        if P_O_C[label, token] != 0:
            summ[label] += math.log(P_O_C[label, token])
    for key, value in iter(summ.items()):
        if value == max(summ.values()):
            f_class = key
    return f_class


@route('/news')
def news_list():
    s = session()
    rows = s.query(News).all()[-31:-1]
    rows = sorted(rows, key=lambda row: row.label)
    return template('news_template', rows=rows)


@route('/add_label/')
def add_label():
    label = request.query.label
    idd = request.query.id
    s.query(News).filter(News.id == idd).update({'label': label})
    s.commit()
    redirect('/news')
    

@route('/update_news')
def update_news():
    newslist = get_news('https://news.ycombinator.com/newest')
    for i in newslist:
        news = News(**i)
        rows = s.query(News).filter(News.title == news.title).filter(News.author == news.author).all()
        if len(rows) == 0:
            news.label = classifier(news.title)
            s.add(news)
    s.commit()
    redirect('/news')

run(host='localhost', port=8080)
