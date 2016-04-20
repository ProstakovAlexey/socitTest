#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'Prostakov Alexey'
"""
Описание
**********************
анализирует показатели быстродействия веб-интерфейса ТИ, с учетом версии

Входные данные
**********************
вычитавает из БД

Выходные данные
**********************
готовит файлы для GnuPlot и вызывает ее для построения

"""
from pymongo import MongoClient
import subprocess
import time

"""
пример структуры записи:
post = {
            "date": datetime.datetime.now(),
            "name": "Тестирование веб-интерфейса ТИ",
            "comment": "Результат автоматического тестирования",
            "version": version,
            "data":
                {
                    "Предварительная остановка очереди запросов": runTime[1] - runTime[0],
                    "Запуск очереди запросов": runTime[2] - runTime[1],
                    "Просмотр СМЭВ запросов": runTime[3] - runTime[2],
                    "Просмотр заявлений ПГУ": runTime[4] - runTime[3],
                    "Просмотр протокола ошибок": runTime[5] - runTime[4],
                    "Просмотр протокола событий": runTime[6] - runTime[5],
                    "Просмотр входящих СМЭВ запросов": runTime[7] - runTime[6],
                    "Остановка очереди запросов": runTime[8] - runTime[7],
                    "Итого": runTime[8] - runTime[0]
                },
            "errors": 0,
            "address": base_url
"""

if __name__ == '__main__':
    # список полей и их очередность
    data = ("Предварительная остановка очереди запросов", "Запуск очереди запросов", "Просмотр СМЭВ запросов",
                "Просмотр заявлений ПГУ", "Просмотр протокола ошибок", "Просмотр протокола событий",
                "Просмотр входящих СМЭВ запросов", "Остановка очереди запросов", "Итого")
    # Выполняется если файл запускается как программа
    base_url = "http://172.21.245.71/SocPortal"
    client = MongoClient('192.168.0.89', 27017)
    db = client['test']
    collection = db['Tests']
    versions = collection.distinct("version", {"name": "Тестирование веб-интерфейса ТИ"})
    print('В БД есть результаты по тестированию ТИ на Туле для версий:', versions)
    
    # файл для данных для графиков
    fp = open('Графики/data.txt', 'w')

    # перебираем все найденные версии, будем получить средние данные для каждой
    for version in versions:
        y_data = list()
        print('\nСредние результаты для версии', version)
        print('****************************************')
        res = collection.find({"name": "Тестирование веб-интерфейса ТИ", "comment": "Тула", "errors": 0, "version": version})
        # заполнение пустого словаря для среднего
        avr = dict()
        for pole in data:
            avr[pole] = 0
        # посчет среднего
        j = 0
        for i in res:
            j +=1
            for key in data:
                avr[key] += i['data'][key]

        # взять последние цифры версии, после точки
        st = version[version.rfind('.')+1:]
        # печать
        for key in data:
            if j>0:
            	avr[key] = avr[key]/j
            	print(key, avr[key])
            	st += " " + str(avr[key])
        # сохранение в файл, для постороения по нему графика gnuplot
        print(" ".join(data), file=fp)
        print(st, file=fp)

    fp.close()
    # построение графика
    p = subprocess.Popen("gnuplot Графики/webTI.gnuplot", shell=True)
    # ждем завершения
    p.wait()
    
    """
    # графики для Тулы
    # веб-интерфейс
    #findStr = 'Оценка производительности Тула'
    findStr = 'Липецк'
    fp = open ('Веб.txt', 'w')
    result = collection.find({"name": "Тестирование веб-интерфейса ТИ", "comment": findStr})
    for post in result:
        st = '%s\t%s' % (post['date'].strftime("%d.%m.%Y %H:%M"), post['data']['Итого'])
        print(st, file=fp)
    fp.close()

    # 409
    fp = open ('409.txt', 'w')
    result = collection.find({"name": "Тестирование 409 сервиса", "comment": findStr})
    for post in result:
        st = '%s\t%s' % (post['date'].strftime("%d.%m.%Y %H:%M"), post['data']['Итого'])
        print(st, file=fp)
    fp.close()
    p = subprocess.Popen("gnuplot Графики/webSpeed.plt", shell=True)

     # ПГУ
    fp = open ('ПГУ.txt', 'w')
    result = collection.find({"name": "Тестирование ПГУ сервиса", "comment": findStr})
    for post in result:
        st = '%s\t%s' % (post['date'].strftime("%d.%m.%Y %H:%M"), post['data']['Итого'])
        print(st, file=fp)
    fp.close()
    p = subprocess.Popen("gnuplot Графики/webSpeed.plt", shell=True)
    # ждем завершения
    p.wait()
    """
    client.close()
    exit(0)
