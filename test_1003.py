# -*- coding: utf-8 -*-
__author__ = 'alexey'

import sys
import http.client
from xml.dom.minidom import *
import os
import configparser
import urllib.request
import time
import hashlib
import datetime
import smev


def readConfig(file="config.ini"):
    '''
    :param file: имя файла конфигурации
    :return: словарь c гражданами и кол-во ошибок
    '''
    err = 0
    if os.access(file, os.F_OK):
        # выполняется если найден конфигурационный файл
        config_str = open(file, encoding='utf-8', mode='r').read()
        # удалить признак кодировки
        config_str = config_str.replace(u'\ufeff', '')
        Config = configparser.ConfigParser()
        Config.read_string(config_str)
        sections = Config.sections()
        # пример заполнения сведений от ИС
        parents = list()
        for section in sections:
            i = Config[section]
            if section.count('parent'):
                # Каждого гражданина мы храним в словаре
                parent = dict()
                parent['famil'] = i.get('famil', fallback= "")
                parent['name'] = i.get('name', fallback= "")
                parent['otch'] = i.get('otch', fallback= "")
                parent['snils'] = i.get('snils', fallback= "")
                parent['drog'] = i.get('drog', fallback= "")
                parent['test'] = i.get('test', fallback= 'None')
                parent['md5'] = i.get('md5', fallback="")
                # Добавляем гражданина в список
                parents.append(parent)
    else:
        print("Ошибка! Не найден конфигурационный файл")
        err = 1
    return parents, err


def service_1003(req, IS, con, name='1003'):
    '''Получает ответ от 1003 сервиса, подставляет текущую дату в
    исходный файл.
    req: строка запроса (обязательный,в нем меняется время, наименование ИС, КОД, ОКТМО)
    numer: (обязательный, номер для образования имени)
    IS: обязательный, словарь. Наименование ИС, мнемоника, ОКТМО
    ответ сервера в строке или None в случае ошибки
    con: соединение к сервису
    '''
    # проводим замены
    s = smev.change(req, IS)
    # сохранить запрос
    smev.write_file(s, name)
    # соединяется с веб-сервисом
    con = http.client.HTTPConnection(IS['adr'], IS['port'])

    # пытаемся отправить 1-ю часть и получить guid
    headers = {"Content-Type": "text/xml; charset=utf-8",
               "SOAPAction": "http://socit.ru/ManyChildren"}
    try:
        con.request("POST", IS['url']+"SMEV/ManyChildren.ashx", s.encode('utf-8'), headers=headers)
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


def test_1003(IS):
    err = 0
    print("Получение документации 1003-сервиса")
    print("*******************************************")

    Parents, Errors = readConfig('config_1003.ini')
    if Errors == 0:
        print("Загрузили конфигурационный файл")
    else:
        print("При загрузке конфигурационного файла возникли ошибки")
        exit(1)
    start = time.time()
    shablon = open('Шаблоны/Request_1003.xml', mode='r', encoding='utf-8').read()
    con = http.client.HTTPConnection(IS['adr'], IS['port'])
    smev.get_wsdl(IS, IS['url']+"SMEV/ManyChildren.ashx", '1003.wsdl')
    # Перебираем всех тестовых родителей
    for parent in Parents:
        req = smev.change(shablon, parent)
        req = smev.change(req, IS)
        print ("Отрабатываем пример", parent['test'])
        result = service_1003(req, IS, con, parent['test'])
        if parent['md5']:
            err1 = smev.check(result, parent['test'], parent['md5'])
            if err1>0:
                print('Ошибка!!! Не совпадает контрольная суммму блока smev:MessageData.')
                err += err1
    post = {
            "date": datetime.datetime.now(),
            "name": "Тестирование 1003 сервиса",
            "comment": IS['comment'],
            "version": IS['version'],
            "data":
                {
                    "Итого": time.time() - start
                },
            "errors": err,
            "address": 'http://%s:%s%sSMEV/ManyChildren.ashx' % (IS['adr'], IS['port'], IS['url'])
        }
    con.close()
    return post
