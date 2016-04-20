#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
"""
Описание
**********************
Веб-сервис, с помощью которого можно вызвать различные тесты
"""
from flask import Flask

app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello!"
"""
@app.route('/runtest/<int:test_id>', methods=['GET'])
def run_test(test_id):
    test = filter(lambda t: t['id'] == test_id, testsList)
    if len(test) == 0:
        abort(404)
    return jsonify({'test': test[0]})
"""
#if __name__ == '__main__':
app.debug = True
app.run(host='0.0.0.0')
