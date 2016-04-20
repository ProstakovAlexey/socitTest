#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'alexey'

import smev
import sys
import configparser
from xml.dom.minidom import *
import os
import datetime
import  time
import http.client


def print_res(result):
    for i in range(0, len(result)):
        for j in range(0, len(result[i])):
            print (result[i][j],)
        print()


def service_409(req, IS, name='409'):
    '''Получает ответ от 409 сервиса, подставляет текущую дату в
    исходный файл.
    req: строка запроса (обязательный,в нем меняется время, наименование ИС, КОД, ОКТМО)
    numer: (обязательный, номер для образования имени)
    IS: обязательный, словарь. Наименование ИС, мнемоника, ОКТМО
    ответ сервера в строке или None в случае ошибки
    '''
    # проводим замены
    s = smev.change(req, IS)
    # сохранить запрос
    smev.write_file(s, name)
    # соединяется с веб-сервисом
    con = http.client.HTTPConnection(IS['adr'], IS['port'])
    # пытаемся отправить 1-ю часть и получить guid
    headers = {"Content-Type": "text/xml; charset=utf-8",
               "SOAPAction": "http://sum-soc-help.skmv.rstyle.com/SumSocHelpService/SumSocHelpRequestMessage"}
    try:
        con.request("POST", IS['url']+"SMEV/SocPayments256.ashx", s.encode('utf-8'), headers=headers)
        result = con.getresponse().read()
        result = result.decode('utf-8')
        smev.write_file(result, name)
        status = parseString(result).getElementsByTagName('smev:Status')[0].firstChild.nodeValue
    except:
        Type, Value, Trace = sys.exc_info()
        print("Не удалось обратится к методу Request (1-я часть запроса), возникли ошибки:")
        print("Тип:", Type, "Значение:", Value)
        print("Выполнение будет продолжено")
        result = None
    else:
        # проверим, нет ли ошибки в 1-й части
        if status == u"ACCEPT":
            # нашли что статус ACCEPT
            # получение guid
            # сохранить ответ

            for node in parseString(result).getElementsByTagName('smev:RequestIdRef'):
                guid = node.childNodes[0].nodeValue
            #guid = guid.encode('utf8')
            s = open(r"Шаблоны/409-Ping.xml", "r", encoding="utf8").read()
            # проводим замены
            s = smev.change(s, IS)
            # и меняем GUID
            s = s.replace(r"#RequestIdRef#", guid)
            s = s.replace(r"#OriginRequestIdRef#", guid)
            # сохранить запрос
            smev.write_file(s,name)

            # пытаемся отправить 2-ю часть
            headers = {"Content-Type": "text/xml; charset=utf-8",
               "SOAPAction": "http://sum-soc-help.skmv.rstyle.com/SumSocHelpService/SumSocHelpRequestDataMessage"}
            try:
                con.request("POST", IS['url']+"SMEV/SocPayments256.ashx", s.encode('utf-8'), headers=headers)
                result = con.getresponse().read()
                result = result.decode('utf-8')
            except:
                Type, Value, Trace = sys.exc_info()
                print("Не удалось обратится к методу Request (2-я часть запроса), возникли ошибки:")
                print ("Тип:", Type, "Значение:", Value)
                print ("Выполнение будет продолжено")
                result = None
            else:
                # сохранить ответ
                smev.write_file(result, name)
    # если не нашли статус ACCEPT, то сразу попадаем сюда
    con.close()
    return result


def error_data_409(IS):
    # Образец для ошибка в дате
    good_error1 = {"pfr:code": "ERR_LOAD_REQUEST_DATA",
                   "pfr:message": "Ошибка во входных данных: В birthDate содержатся неправильные данные 1962-24-18. Дата должна быть в формате dd.MM.yyyy"}
    result = service_409(open('Шаблоны/409-ERR1_Request.xml', mode='r', encoding="utf8").read(), IS, '409_err_data')
    error = 0
    if result == None:
        # пришел пустой
        error += 1
        print ("Тест Error1. Пришел пустой ответ")
    else:
        # не пустой, анализируем его
        for key in good_error1.keys():
            bad = parseString(result).getElementsByTagName(key)[0].firstChild.nodeValue
            if good_error1[key] != bad:
                print ("Образец: Ключ=%s, значение=%s" % (key, good_error1[key]))
                print ("Получено: Ключ=%s, значение=%s" % (key, bad))
                error += 1
    if error > 0:
        print ("!!!  Тест Error Data. Ошибка!")
    else:
        print ("Тест Error Date. Ошибок нет")
    return error


def error_guid_409(IS):
    # Образец для нет GUID
    good_error2 = {"pfr:code": "ERR_SMEV_FLK",
                   "pfr:message": "Ответ на асинхронный запрос c message.OriginRequestIdRef = 23a02b99-fcc0-441d-9c24-89e0a2dc0525 не найден в системе"}

    result = service_409(open('Шаблоны/409-ERR2_Request.xml', mode='r', encoding="utf8").read(), IS, '409_err_guid')
    error = 0
    if result == None:
        # пришел пустой
        error += 1
        print ("Тест Error GUID. Пришел пустой ответ")
    else:
        # не пустой, анализируем его
        for key in good_error2.keys():
            try:
                bad = parseString(result).getElementsByTagName(key)[0].firstChild.nodeValue
            except:
                print('Ошибка при получении примеры с ошибкой в GUID')
                error += 1
            else:
                if good_error2[key] != bad:
                    print ("Образец: Ключ=%s, значение=%s" % (key, good_error2[key]))
                    print ("Получено: Ключ=%s, значение=%s" % (key, bad))
                    error += 1
    if error > 0:
        print ("!!!  Тест Error GUID. Ошибка!")
    else:
        print ("Тест Error GUID. Ошибок нет")
    return error


def nofound_409(IS):
    # Образец Даные не доступны
    good_error3 = {"pfr:code": "2",
                   "pfr:message": "Данные по запросу недоступны"}

    result = service_409(open('Шаблоны/409-NOFOUND_Request.xml', mode='r', encoding="utf8").read(), IS, '409_nofound')
    error = 0
    if result == None:
        # пришел пустой
        error += 1
        print ("Тест Даные не доступны. Пришел пустой ответ")
    else:
        # не пустой, анализируем его
        for key in good_error3.keys():
            bad = parseString(result).getElementsByTagName(key)[0].firstChild.nodeValue
            if good_error3[key] != bad:
                print ("Образец: Ключ=%s, значение=%s" % (key, good_error3[key]))
                print ("Получено: Ключ=%s, значение=%s" % (key, bad))
                error += 1
    if error > 0:
        print ("!!!  Тест Даные не доступны. Ошибка!")
    else:
        print ("Тест Даные не доступны. Ошибок нет")
    return error


def ok_409(IS):
    # Образец выплат
    good_error4 = [("Субсидия на оплату электроэнергии", "1", "2011-03-01", "300,00"),
                   ("Субсидия на холодную воду", "1", "2011-03-01", "500,00"),
                   ("Субсидия на газ", "1", "2011-04-01", "200,00"),
                   ("Субсидия на отопление", "1", "2011-05-01", "1000,00"),
                   ("Ежем.денеж.комп.чл. семьи погибшего(умершего)вслед.воен.травмы", "1", "2012-05-01", "31612,91"),
                   ("Ежем.денеж.комп.чл. семьи погибшего(умершего)вслед.воен.травмы", "1", "2012-06-01", "903,22"),
                   ("Ежем.денеж.комп.в возмещение вреда здоровью инвал. 3гр.вслед.воен.травмы", "1", "2012-10-01",
                    "2800,00"),
                   ("Ежем.денеж.комп.чл. семьи погибшего(умершего)вслед.воен.травмы", "1", "2013-01-01", "87612,96"),
                   ("Льготы по налогам", "1", "2013-05-01", "2000,00"),
                   ("Ежем.денеж.комп.чл. семьи погибшего(умершего)вслед.воен.травмы", "1", "2013-07-01", "49500,00")
    ]

    result = service_409(open('Шаблоны/409-OK_Request.xml', mode='r', encoding="utf8").read(), IS, '409_ok')
    error = 0
    if result == None:
        # пришел пустой
        error += 1
        print ("Тест Даные результаты. Пришел пустой ответ")
    else:
        # не пустой, анализируем его
        typesoc = parseString(result).getElementsByTagName("typeSoc")
        sign = parseString(result).getElementsByTagName("sign")
        datesoc = parseString(result).getElementsByTagName("dateSoc")
        size = parseString(result).getElementsByTagName("size")
        bad = []
        for j in range(0, typesoc.length):
            bad.append((
                typesoc.item(j).firstChild.nodeValue, sign.item(j).firstChild.nodeValue,
                datesoc.item(j).firstChild.nodeValue, size.item(j).firstChild.nodeValue))

        if bad != good_error4:
            error += 1
            if len(bad) != len(good_error4):
                print ("Кол-во выплат в образце и полученно не совпадает")
                print ("Результат:")
                print_res(bad)
                print ("Образец:")
                print_res(good_error4)
            else:
                for a in range(0, len(bad)):
                    if len(bad[a]) != len(good_error4[a]):
                        print ("Кол-во атрибутов не совпадает с образцом, для выплаты - ", bad[a][0])

                    else:
                        for b in range(0, len(bad[a])):
                            if bad[a][b] != good_error4[a][b]:
                                print ("**** В выплате:", good_error4[a][0])
                                print ("получено=%s \nобразец =%s" % (bad[a][b], good_error4[a][b]))

    if error > 0:
        print ("!!!  Тест результаты. Ошибка!")
    else:
        print ("Тест результаты. Ошибок нет")
    return error


def test_409(IS):
    err = 0
    start = time.time()
    print("Автоматическое тестирование 409 сервиса")
    print("********************************************")

    err += smev.get_wsdl(IS, url=IS['url']+'SMEV/SocPayments256.ashx', name='409.wsdl')
    err += ok_409(IS)
    err += nofound_409(IS)
    err += error_data_409(IS)
    err += error_guid_409(IS)
    print("")
    post = {
        "date": datetime.datetime.now(),
        "name": "Тестирование 409 сервиса",
        "comment": IS['comment'],
        "version": IS['version'],
        "data":
            {
                "Итого": time.time() - start
            },
        "errors": err,
        "address": 'http://%s:%s%sSMEV/SocPayments256.ashx' % (IS['adr'], IS['port'], IS['url'])
        }
    return post
