#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'alexey'

import smev
import sys
import configparser
from xml.dom.minidom import *
import datetime
import  time
import http.client


def service_510(req, IS, name='510'):
    """Получает ответ от 510 сервиса
    req: строка запроса (обязательный,в нем меняется время, наименование ИС, КОД, ОКТМО)
    numer: (обязательный, номер для образования имени)
    IS: обязательный, словарь. Наименование ИС, мнемоника, ОКТМО
    ответ сервера в строке или None в случае ошибки
    """
    # проводим замены
    s = smev.change(req, IS)
    # сохранить запрос
    smev.write_file(s, name)
    # соединяется с веб-сервисом
    con = http.client.HTTPConnection(IS['adr'], IS['port'])
    # пытаемся отправить 1-ю часть и получить ответ
    headers = {"Content-Type": "text/xml; charset=utf-8",
               "SOAPAction": "queryLongServicePension"}
    try:
        con.request("POST", IS['url']+"/SMEV/GosPension256.ashx", s.encode('utf-8'), headers=headers)
        result = con.getresponse().read()
        result = result.decode('utf-8')
    except:
        Type, Value, Trace = sys.exc_info()
        print("Не удалось обратится к методу Request (1-я часть запроса), возникли ошибки:")
        print("Тип:", Type, "Значение:", Value)
        print("Выполнение будет продолжено")
        result = None
    else:
        # проверим, нет ли ошибки в 1-й части
        smev.write_file(result, name)
    con.close()
    return result


def ok_510(IS):
    result = service_510(open('Шаблоны/510-OK.xml', mode='r', encoding="utf8").read(), IS, '510_ok')
    error = 0
    if result == None:
        # пришел пустой
        error += 1
        print ("510 Тест ОК - ошибка . Пришел пустой ответ")
    else:
        try:
            status = parseString(result).getElementsByTagName('smev:Status')[0].firstChild.nodeValue
        except:
            status = 'ERROR'
        if status == u"RESULT":
            good_result = dict(presenceOfTheStatusOfThe="Лица, замещающие госдолжности",
                               law="111 от 27.10.2008 О МЕРАХ СОЦИАЛЬНОЙ ПОДДЕРЖКИ СЕМЬИ И ДЕТЕЙ  В МОСКОВСКОЙ ОБЛАСТИ",
                               dateStart="2009-01-14",
                               termPension="бессрочно",
                               AuthorityPresentedData="Комитет социальной защиты населения Администрации Ярославского района")
            for key in good_result.keys():
                bad = parseString(result).getElementsByTagName(key)
                if bad :
                    # не пустой
                    bad = bad[0].firstChild.nodeValue
                    if good_result[key] != bad:
                        print("Образец: Ключ=%s, значение=%s" % (key, good_result[key]))
                        print("Получено: Ключ=%s, значение=%s" % (key, bad))
                        error += 1
                else:
                    print("510 Тест ОК - ошибка. Не найден тег", key)
                    error +=1
        else:
            print ("510 Тест ОК - ошибка . Пришел ответ co статусом %s, ожидаем RESULT" % status)
            error += 1
    if error == 0:
            print("510 ОК пример получен успешно")
    return error


def err_510(IS):
    result = service_510(open('Шаблоны/510-ERR.xml', mode='r', encoding="utf8").read(), IS, '510_err')
    error = 0
    if result == None:
        # пришел пустой
        error += 1
        print ("510 Тест ERROR - ошибка . Пришел пустой ответ")
    else:
        try:
            status = parseString(result).getElementsByTagName('smev:Status')[0].firstChild.nodeValue
        except:
            status = 'ERROR'
        if status == u"REJECT":
            good_result = dict(errorCode="-1",
                               errorMessage="ERR_LOAD_REQUEST_DATA: Ошибка загрузки данных из запроса к СМЭВ-сервису: Ошибка загрузки DataOnTheCitizen: Ошибка загрузки даты рождения: в DataOnTheCitizen.birthdate дата должна быть в формате dd.MM.yyyy")
            for key in good_result.keys():
                bad = parseString(result).getElementsByTagName(key)
                if bad :
                    # не пустой
                    bad = bad[0].firstChild.nodeValue
                    if good_result[key] != bad:
                        print("Образец: Ключ=%s, значение=%s" % (key, good_result[key]))
                        print("Получено: Ключ=%s, значение=%s" % (key, bad))
                        error += 1
                else:
                    print("510 Тест ERROR - ошибка. Не найден тег", key)
                    error +=1
        else:
            print ("510 Тест ERROR - ошибка . Пришел ответ co статусом %s, ожидаем REJECT" % status)
            error += 1
    if error == 0:
            print("510 ERROR пример получен успешно")
    return error


def nofound_510(IS):
    result = service_510(open('Шаблоны/510-NOFOUND.xml', mode='r', encoding="utf8").read(), IS, '510_NOFOUND')
    error = 0
    if result == None:
        # пришел пустой
        error += 1
        print ("510 Тест NOFOUND - ошибка . Пришел пустой ответ")
    else:
        try:
            status = parseString(result).getElementsByTagName('smev:Status')[0].firstChild.nodeValue
        except:
            status = 'ERROR'
        if status == u"RESULT":
            good_result = dict(errorCode="2",
                               errorMessage="Гражданин не найден в БД")
            for key in good_result.keys():
                bad = parseString(result).getElementsByTagName(key)
                if bad :
                    # не пустой
                    bad = bad[0].firstChild.nodeValue
                    if good_result[key] != bad:
                        print("Образец: Ключ=%s, значение=%s" % (key, good_result[key]))
                        print("Получено: Ключ=%s, значение=%s" % (key, bad))
                        error += 1
                else:
                    print("510 Тест NOFOUND - ошибка. Не найден тег", key)
                    error +=1
        else:
            print ("510 Тест NOFOUND - ошибка . Пришел ответ co статусом %s, ожидаем RESULT" % status)
            error += 1
    if error == 0:
            print("510 NOFOUND пример получен успешно")
    return error


def test_510(IS):
    err = 0
    start = time.time()
    print("Автоматическое тестирование 510 сервиса")
    print("********************************************")
    err += smev.get_wsdl(IS, url=IS['url']+'SMEV/GosPension256.ashx', name='510.wsdl')
    err += ok_510(IS)
    err += err_510(IS)
    err += nofound_510(IS)
    print("")
    post = {
        "date": datetime.datetime.now(),
        "name": "Тестирование 510 сервиса",
        "comment": IS['comment'],
        "version": IS['version'],
        "data":
            {
                "Итого": time.time() - start
            },
        "errors": err,
        "address": 'http://%s:%s%sSMEV/GosPension256.ashx' % (IS['adr'], IS['port'], IS['url'])
        }
    return post


