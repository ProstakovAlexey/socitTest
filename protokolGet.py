#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'Prostakov Alexey'

import os, glob
from pymongo import MongoClient
import sys
import configparser
import smev
import logging
import protokol

"""
Описание
**********************

Входные данные
**********************

Выходные данные
**********************

"""
logging.basicConfig(filename='tester.log', filemode='a', level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s')


def printTest(post):
    print("%s выполнено за %s сек. ошибок %s."
                % (post['name'], post['data']['Итого'], post['errors']))
    if post['errors']:
        logging.error("%s Выполнено за %s ошибок %s."
            % (post['name'], post['data']['Итого'], post['errors']))
    else:
        logging.info("%s Выполнено за %s без ошибок."
            % (post['name'], post['data']['Итого']))


def readConfig(file="config.ini"):
    '''
    :param file: имя файла конфигурации
    :return: список ИС для тестирования, словарь настроек к БД, кол-во ошибок
    '''
    err = 0
    ISList = list()
    BD = dict()
    if os.access(file, os.F_OK):
        # выполняется если найден конфигурационный файл
        config_str = open(file, encoding='utf-8', mode='r').read()
        # удалить признак кодировки
        config_str = config_str.replace(u'\ufeff', '')
        # чтение конфигурационного файла
        Config = configparser.ConfigParser()
        Config.read_string(config_str)
        sections = Config.sections()
        # читаем все секции
        for section in sections:
            i = Config[section]
            # это секция про ИС, их может быть несколько
            if section.count('IS'):
                IS = dict()
                IS['snd_name'] = i.get('name', fallback='СОЦИНФОРМТЕХ')
                IS['snd_code'] = i.get('mnemonic', fallback='SOCP01711')
                IS['oktmo'] = i.get('OKTMO', fallback='70000000')
                IS['url'] = i.get('URL', fallback='/socportal/')
                IS['adr'] = i.get('address', fallback='')
                IS['port'] = i.get('port', fallback='80')
                IS['servicecode'] = i.get('SERVICE_CODE', fallback='123456789')
                IS['SpravID'] = i.get('SpravID', fallback='1')
                IS['comment'] = i.get('comment', fallback='')
                IS['protocol'] = i.get('protocol', fallback='no')
                ISList.append(IS)
            # это про подсоединение к БД
            elif section == 'BD':
                BD['adr'] = i.get('address', fallback='')
                BD['port'] = i.get('port', fallback='27017')
                BD['BD'] = i.get('dataBase', fallback='')
                BD['protocol'] = i.get('protocol', fallback='')
        # проверим заполнение секции о БД
        if len(BD.keys()) == 0:
            print('В конфигурационном файле отсутствует обязательная секция о БД.')
            err += 1
        else:
            for key in BD.keys():
                if BD[key] == '':
                    print("Параметр %s не должен быть пустой, заполните его в конфигурационном файле %s" % (key, file))
                    err += 1
        # проверим заполнение сведений об ИС
        if len(ISList) == 0:
            print('В конфигурационном файле отсутствует обязательная секция об ИС.')
            err += 1
        else:
            for IS in ISList:
                for key in IS.keys():
                    if IS[key] == '':
                        print("В секции сведение об ИС параметр %s не должен быть пустой, заполните его в конфигурационном файле %s" % (key, file))
                        err += 1
    # нет конфигурационного файла
    else:
        print("Ошибка! Не найден конфигурационный файл")
        err = 1
    return ISList, BD, err


if __name__ == '__main__':
    logging.info("Программа запущена")
    # чтение конфигурационного файла
    ISList, BD, err = readConfig('config.ini')
    if err > 0 or ISList is None or BD is None:
        logging.critical("При чтении конфигурационного файла произошли ошибки. Программа остановлена")
        exit(1)
    else:
        logging.info("Конфигурационный файл прочитан успешно.")

    # соединяемся с БД для записи протокола
    try:
        client = MongoClient(BD['adr'], int(BD['port']))
        db = client[BD['BD']]
        collProt = db[BD['protocol']]
    except:
        logging.critical("Ошибка при соединении с БД. Программа остановлена")
        Type, Value, Trace = sys.exc_info()
        logging.critical("""Тип ошибки: %s Текст: %s""" % (Type, Value))
        exit(2)
    logging.info('Успешное соединения с БД')

    # перебираем все ИС из конф. файла
    for IS in ISList:
        err = 0
        logging.info('Обрабатываем ИС: %s' % IS['snd_name'])
        # получаем версии ПО
        IS['version'], errMsg = smev.getVersion(IS)
        if errMsg :
            logging.error(errMsg)
            continue
        if IS['protocol'] == 'yes':
            post, err1 = (protokol.getData(IS))
            err += err1
            print(post)
            if err1:
                logging.error('Получение протокола для %s не выполнено, возникли ошибки' % post['comment'])
            else:
                logging.info('Получение протокола для %s выполнено успешно' % post['comment'])
                logging.debug('Для записи подготовлено: %s' % post)
                collProt.insert_one(post)
                logging.debug('Было записано c ID=%s' % post['_id'])
    # закрывает соединения с БД
    client.close()
    exit(0)
