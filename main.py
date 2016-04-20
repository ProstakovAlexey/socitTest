#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'Prostakov Alexey'

import os, glob
import test_373
import test_409
import test_510
import test_PGU
import test_1003
import test_1004
import test_1005
import test_1007
import test_1009
import test_web
from pymongo import MongoClient
import sys
import configparser
import smev
import logging

"""
Описание
**********************

Входные данные
**********************

Выходные данные
**********************

"""
logging.basicConfig(filename='tester.log', filemode='a', level=logging.INFO,
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
                IS['373'] = i.get('373', fallback='no')
                IS['409'] = i.get('409', fallback='no')
                IS['510'] = i.get('510', fallback='no')
                IS['PGU'] = i.get('PGU', fallback='no')
                IS['1003'] = i.get('1003', fallback='no')
                IS['1004'] = i.get('1004', fallback='no')
                IS['1005'] = i.get('1005', fallback='no')
                IS['1007'] = i.get('1007', fallback='no')
                IS['1009'] = i.get('1009', fallback='no')
                IS['web'] = i.get('web', fallback='no')
                IS['protocol'] = i.get('protocol', fallback='no')
                ISList.append(IS)
            # это про подсоединение к БД
            elif section == 'BD':
                BD['adr'] = i.get('address', fallback='')
                BD['port'] = i.get('port', fallback='27017')
                BD['BD'] = i.get('dataBase', fallback='')
                BD['collection'] = i.get('collection', fallback='')
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

    # очистка папки Результаты
    for file in glob.glob('Результаты/*'):
        os.remove(file)
    logging.info("Очищена папка результаты")

    # соединяемся с БД для записи протокола
    try:
        client = MongoClient(BD['adr'], int(BD['port']))
        db = client[BD['BD']]
        collection = db[BD['collection']]
        collProt = db[BD['protocol']]
    except:
        logging.critical("Ошибка при соединении с БД. Программа остановлена")
        Type, Value, Trace = sys.exc_info()
        logging.critical("""Тип ошибки: %s
Текст: %s""" % (Type, Value))
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
        # тест для 373
        if IS['373'] == 'yes':
            print()
            post = test_373.test_373(IS)
            err += post['errors']
            printTest(post)
            collection.insert_one(post)
            print(post)
        # тест для 409
        if IS['409'] == 'yes':
            print()
            post = test_409.test_409(IS)
            err += post['errors']
            printTest(post)
            print(post)
            #collection.insert_one(post)
        # тест для 510
        if IS['510'] == 'yes':
            print()
            post = test_510.test_510(IS)
            err += post['errors']
            printTest(post)
            collection.insert_one(post)
            print(post)
        # тест для ПГУ
        if IS['PGU'] == 'yes':
            print()
            post = test_PGU.test_PGU(IS)
            err += post['errors']
            print(post)
            printTest(post)
            collection.insert_one(post)
        # тест для 1003
        if IS['1003'] == 'yes':
            print()
            post = test_1003.test_1003(IS)
            err += post['errors']
            printTest(post)
            collection.insert_one(post)
            print(post)
        # для 1004
        if IS['1004'] == 'yes':
            print()
            post = test_1004.test_1004(IS)
            err += post['errors']
            printTest(post)
            collection.insert_one(post)
            print(post)
        # Тест для 1005
        if IS['1005'] == 'yes':
            print()
            post = test_1005.test_1005(IS)
            err += post['errors']
            printTest(post)
            collection.insert_one(post)
            print(post)
        # Тест для 1007
        if IS['1007'] == 'yes':
            print()
            post = test_1007.test_1007(IS)
            err += post['errors']
            printTest(post)
            collection.insert_one(post)
            print(post)
        # Тест для 1009
        if IS['1009'] == 'yes':
            print()
            post = test_1009.test_1009(IS)
            err += post['errors']
            printTest(post)
            collection.insert_one(post)
            print(post)
        # тест для веб-интерфейса
        if IS['web'] == 'yes':
            print()
            post, err1 = test_web.test_web(IS)
            if  err1 == 0:
                logging.info("Выполнено успешно за %s" % post['data']['Итого'])
                printTest(post)
            else:
                print(" Возникли ошибки!!!")
                err += err1
                logging.error('Тесты веб-интерфейса для %s выполненны с ошибками'% IS['comment'])
                logging.debug('Строка для записи в БД: %s' % post)
            # печать и запись
            #print(post)
            collection.insert_one(post)

        print ('--------------')
        print ('кол-во ошибок:', err)
        if err:
            logging.error('Тесты для %s выполненны с общим кол-во ошибок: %s'
                % (IS['comment'],err))
        else:
            logging.info('Тесты для %s выполненны без ошибок.' % IS['comment'])
    # закрывает соединения с БД
    client.close()
    exit(0)
