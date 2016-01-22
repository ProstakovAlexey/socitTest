# -*- coding: utf-8 -*-
__author__ = 'Prostakov Alexey'
"""
Описание
**********************

Входные данные
**********************

Выходные данные
**********************

"""
import osa
import datetime
import base64
import zipfile
import os
import csv


def getProtokol(addr, string):
    """
    Возвращает протокол за дату. Если не указана, то за вчерашний день.
    :param addr адрес сервиса
    :param date: дата, за которую получать протокол
    :return: список файлов из архива и кол-во ошибок
    """
    err = 0
    fileList = list()
    resp = None
    print('Строка даты=', string)
    # пробуем получить протокол
    try:
        cl = osa.Client(addr+'?wsdl')
        request = cl.types.GetProtocol()
        request.date = string
        resp = cl.service.GetProtocol(request)
    except:
        print('При обращении к методу GetProtocol, адрес %s возникли ошибки' % addr)
        err += 1
    # может прийти и пустой
    if resp is None:
        print('Протокол за %s не получен' % string)
        err += 1
    else:
        # проверяем были ли ошибки
        print(resp.HasError)
        if resp.HasError is False:
            # проверка результата
            if resp.Result is not None:
                # преобразуем протокол из base64 в zip и сохраняем
                open('arh.zip', 'wb').write(base64.standard_b64decode(resp.Result))
                # проверка zip файла
                with zipfile.ZipFile('arh.zip') as zipFile:
                    # проверка файла
                    error = zipFile.testzip()
                    if error is None:
                        print('Полученный zip файл прошел проверку')
                        # разархивирую файлы
                        fileList = zipFile.namelist()
                        print('Внутри архива файлы: %s' % fileList)
                        zipFile.extractall(path='csv/')
                    else:
                        print('Полученный zip файл поврежден. Результат проверки: ' % error)
                        err += 1
                # удалить временный zip файл
                os.remove('arh.zip')
            else:
                print('Вернулься пустой результат')
                err += 1
        else:
            # вернулись ошибки при получении протокола
            err += 1
            print('Вернулась ошибка при получении протокола: %s' % resp.Message)
    return fileList, err


def getData(IS, date=None):
    """
    :param IS: список параметор ИС
    :param date: дата, с какую получать, если не указано - за вчера
    :return:
    """
    if date is None:
        date = datetime.datetime.now() - datetime.timedelta(days=1)
        date = date.strftime('%Y-%m-%d')

    addr = 'http://%s:%s%sexport.asmx' % (IS['adr'], IS['port'], IS['url'])
    fileList, err = getProtokol(addr, date)
    post = dict()
    if err == 0 :
        # определение настроечных констант
        req = r'Регламент:'
        res = r'Запрос к методу'
        zaiv = r'к методу SetRequest'
        status =r'Статус по заявке'
        dtf1 = r'%d.%m.%Y %H:%M:%S'
        dtf2 = r'%d.%m.%Y_%H:30'

        # инициализация
        resCount = 0 # кол-во ответов с час
        reqCount = 0 # кол-во запросов с час
        resTotal = 0 # кол-во ответов всего
        reqTotal = 0 # кол-во запросов всего
        zaivCount = 0 # кол-во заявлений от ПГУ в час
        zaivTotal = 0 # кол-во заявлений от ПГУ всего
        statusCount = 0 # кол-во решений по заявлениям от ПГУ в час
        statusTotal = 0 # кол-во заявлений по заявлениям всего
        # списки
        reqList = list()
        respList = list()
        zaivList = list()
        zaivStatus = list()
        # берем один файл и обрабатываем его
        with open('csv/' + fileList[0], encoding='utf-8') as csvfile:
            old = None
            logReader = csv.reader(csvfile, delimiter='\t')
            for row in logReader:
                # если не установлена старая дата, то это новый файл и ее ставим
                if old is None:
                    row[0] = row[0].replace(u'\ufeff', '')
                    old = datetime.datetime.strptime(row[0], dtf1)
                # ищем только строки с нужным адаптером
                if row[2].find(req)>-1 :
                    # это запрос
                    # проверяем, что она случилась в том же часу
                    now = datetime.datetime.strptime(row[0], dtf1)
                    if now.hour != old.hour :
                        zaivList.append((old.hour, zaivCount))
                        zaivStatus.append((old.hour, statusCount))
                        reqList.append((old.hour, reqCount))
                        respList.append((old.hour, resCount))
                        old = now
                        resCount = 0
                        reqCount = 0
                        statusCount = 0
                        zaivCount = 0
                    reqCount += 1
                    reqTotal += 1
                elif row[2].find(res)>-1:
                    # это ответ
                    # проверяем, что она случилась в том же часу
                    now = datetime.datetime.strptime(row[0], dtf1)
                    if now.hour != old.hour :
                        zaivList.append((old.hour, zaivCount))
                        zaivStatus.append((old.hour, statusCount))
                        reqList.append((old.hour, reqCount))
                        respList.append((old.hour, resCount))
                        old = now
                        resCount = 0
                        reqCount = 0
                        statusCount = 0
                        zaivCount = 0
                    resCount += 1
                    resTotal += 1
                elif row[2].find(zaiv)>-1:
                    # это заявление
                    # проверяем, что она случилась в том же часу
                    now = datetime.datetime.strptime(row[0], dtf1)
                    if now.hour != old.hour :
                        zaivList.append((old.hour, zaivCount))
                        zaivStatus.append((old.hour, statusCount))
                        reqList.append((old.hour, reqCount))
                        respList.append((old.hour, resCount))
                        old = now
                        resCount = 0
                        reqCount = 0
                        statusCount = 0
                        zaivCount = 0
                    zaivCount += 1
                    zaivTotal += 1
                elif row[2].find(status)>-1:
                    # это статус
                    # проверяем, что она случилась в том же часу
                    now = datetime.datetime.strptime(row[0], dtf1)
                    if now.hour != old.hour :
                        zaivList.append((old.hour, zaivCount))
                        zaivStatus.append((old.hour, statusCount))
                        reqList.append((old.hour, reqCount))
                        respList.append((old.hour, resCount))
                        old = now
                        resCount = 0
                        reqCount = 0
                        statusCount = 0
                        zaivCount = 0
                    statusCount += 1
                    statusTotal += 1

        zaivList.append((old.hour, zaivCount))
        zaivStatus.append((old.hour, statusCount))
        reqList.append((old.hour, reqCount))
        respList.append((old.hour, resCount))

        post = {
            "date": datetime.datetime.strptime(date, '%Y-%m-%d'),
            "name": "Протокол",
            "comment": IS['comment'],
            "version": IS['version'],
            "request": reqList,
            "response": respList,
            "zaiv": zaivList,
            "status": zaivStatus,
            "address": addr
        }

    return post, err
