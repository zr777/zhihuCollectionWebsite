# -*- coding: utf-8 -*-
from flask import Flask
import json
from flask_jsonpify import jsonpify


app = Flask(__name__)

collections = []
with open(u'知乎收藏文章.json', 'r', encoding='utf-8') as f:
    collections = json.load(f)

qa_dict = {}
with open('url_answer.json', 'r', encoding='utf-8') as f:
    qa_dict = json.load(f)
# print(qa_dict['question/31116099/answer/116025931'])

index_html = ''
with open('zhihuCollection.html', 'r', encoding='utf-8') as f:
    index_html = f.read()


@app.route('/')
def index():
    return index_html


@app.route('/collections')
def collectionsApi():
    return jsonpify(collections)


@app.route('/find/<path:answer_url>') # 使用path修正斜杠的副作用，参见http://flask.pocoo.org/snippets/76/
def answersApi(answer_url):
    # show the post with the given id, the id is an integer
    return jsonpify({'answer': qa_dict[answer_url]})


@app.route('/test')
def test():
    # show the post with the given id, the id is an integer
    return jsonpify(qa_dict)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
