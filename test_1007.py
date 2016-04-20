#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'alexey'

import sys
import http.client
from xml.dom.minidom import *
import os
import configparser
import urllib.request
import time
import datetime
import smev


def readConfig(file="config_1007.ini"):
    '''
    :param file: имя файла конфигурации
    :return: список словарей с гражданами и кол-во ошибок
    '''
    err = 0
    parents = list()
    if os.access(file, os.F_OK):
        # выполняется если найден конфигурационный файл
        config_str = open(file, encoding='utf-8', mode='r').read()
        # удалить признак кодировки
        config_str = config_str.replace(u'\ufeff', '')
        Config = configparser.ConfigParser()
        Config.read_string(config_str)
        sections = Config.sections()
        # пример заполнения сведений от ИС
        for section in sections:
            i = Config[section]
            if section.count('test'):
                # Каждого гражданина мы храним в словаре
                parent = dict()
                parent['famil'] = i.get('famil', fallback="")
                parent['name'] = i.get('name', fallback="")
                parent['otch'] = i.get('otch', fallback="")
                parent['snils'] = i.get('snils', fallback="")
                parent['drog'] = i.get('drog', fallback="")
                parent['test'] = i.get('test', fallback='None')
                parent['md5'] = i.get('md5', fallback="")
                # Добавляем гражданина в список
                parents.append(parent)
    else:
        print("Ошибка! Не найден конфигурационный файл")
        err = 1
    return parents, err


def service_1007(req, IS, name='1007'):
    '''Получает ответ от сервиса
    req: строка запроса
    numer: (обязательный, номер для образования имени)
    IS: обязательный, словарь.
    '''
    # сохранить запрос
    smev.write_file(req, name)
    # соединяется с веб-сервисом
    con = http.client.HTTPConnection(IS['adr'], IS['port'])
    # пытаемся отправить 1-ю часть и получить guid
    headers = {"Content-Type": "text/xml; charset=utf-8",
               "SOAPAction": "http://socit.ru/veteranWork"}
    try:
        con.request("POST", IS['url']+"SMEV/VeteranWork.ashx", req.encode('utf-8'), headers=headers)
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


def test_1007(IS):
    err = 0
    terr = 0
    # Выполняется если файл запускается как программа
    print("Получение документации 1007-сервиса (Ветеран)")
    print("*******************************************")

    Parents, Errors = readConfig('config_1007.ini')
    if Errors == 0:
        print("Загрузили конфигурационный файл")
    else:
        print("При загрузке конфигурационного файла возникли ошибки")
        exit(1)
    start = time.time()
    # Перебираем всех тестовых родителей
    shablon = open('Шаблоны/Request_1007.xml', mode='r', encoding='utf-8').read()
    smev.get_wsdl(IS, IS['url']+"SMEV/VeteranWork.ashx", '1007.wsdl')

    for parent in Parents:
        req = smev.change(shablon, parent)
        req = smev.change(req, IS)
        print ("Отрабатываем пример", parent['test'])
        res = service_1007(req, IS, parent['test'])
        # проверяем результат
        if parent['md5']:
            err = smev.check(res, parent['test'], parent['md5'])
            if err > 0:
                print('Ошибка!!! Не совпадает контрольная суммму блока smev:MessageData.')
        terr += err
    post = {
            "date": datetime.datetime.now(),
            "name": "Тестирование 1007 сервиса",
            "comment": IS['comment'],
            "version": IS['version'],
            "data":
                {
                    "Итого": time.time() - start
                },
            "errors": terr,
            "address": 'http://%s:%s%sSMEV/VeteranWork.ashx' % (IS['adr'], IS['port'], IS['url'])
        }
    return post
