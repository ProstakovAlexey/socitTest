#!/usr/bin/python3.4
# -*- coding: utf-8 -*-
__author__ = 'alexey'

import smev
import configparser
from xml.dom.minidom import *
import datetime
import  time
import http.client


def pguChange(req, IS, SERVICE_CODE=None, CASE_NUM='1231231666', SNILS='111-111-111 11'):
    if SERVICE_CODE is None:
        SERVICE_CODE = IS['servicecode']
    req = req.replace("#SERVICE_CODE#", SERVICE_CODE)
    req = req.replace("#CASE_NUM#", CASE_NUM)
    req = req.replace("#SNILS#", SNILS)
    return smev.change(req, IS)


def pgu_send(IS, req, pre='pgu', soapaction="GetSettings", url=r"pgu/RequestAllowanceServiceSOAP256.ashx"):
    '''Получает ответ от сервиса ПГУ
    req: строка запроса
    pre: необязательный, для образования имени
    adr: адрес сервиса (необяз., по умолчанию service_adr)
    port: порт (необяз., по умолчанию =service_port)
    ответ сервера в строке или None в случае ошибки'''
    url = IS['url']+url
    # сохранить запрос
    smev.write_file(req, soapaction, pre)
    # соединяется с веб-сервисом
    con = http.client.HTTPConnection(IS['adr'], IS['port'])
    # пытаемся отправить 1-ю часть и получить guid
    headers = {"Content-Type": "text/xml; charset=utf-8",
               "SOAPAction": soapaction}
    try:
        con.request("POST", url, req.encode('utf-8'), headers=headers)
        result = con.getresponse().read()
        result = result.decode('utf-8')
    except:
        Type, Value, Trace = sys.exc_info()
        print ("Не удалось обратится к методу %s возникли ошибки:" % soapaction)
        print ("Тип:", Type, "Значение:", Value)
        print ("Выполнение будет продолжено")
        result = None
    else:
        # проверим, нет ли ошибки в 1-й части
        if smev.write_file(result, soapaction, pre)  > 0:
            result = None
    return result


def get_settings(IS):
    err = 0
    '''Функция получает OK и ERROR пример для GetSettings'''
    # Для GetRequest берем шаблон, заполняем в нем нужные поля
    req = open('Шаблоны/GetSettings.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    response = pgu_send(IS, req, 'ok')
    if response is None:
        status = 'ERROR_TRANSFER'
    else:
        status = getStatus(response)
    if status == 'RESULT':
        print ('ОК пример для GetSetting получен')
    else:
        print ('Ошибка! ОК пример для GetSetting неполучен')
        err += 1
    # ERROR пример
    req = open('Шаблоны/GetSettings.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS, SERVICE_CODE = '0000')
    response = pgu_send(IS, req, 'err')
    if response is None:
        status = 'ERROR_TRANSFER'
    else:
        status = getStatus(response)
    if  status == 'REJECT':
        print ('ERROR пример для GetSetting получен')
    else:
        print ('Ошибка! ERROR пример для GetSetting неполучен')
        err += 1
    return err


def get_custom_control(IS):
    err = 0
    '''Получение контрольных примеров для метода GetCustomControl'''
    req = open('Шаблоны/GetCustomControl.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    response = pgu_send(IS, req, pre='ok', soapaction='GetCustomControl')
    status = getStatus(response)
    if status == 'RESULT':
        print('ОК пример для GetCustomControl получен')
    else:
        print('Ошибка! ОК пример для GetCustomControl неполучен. Ответ со статусом', status)
        err += 1
    # ERROR пример
    req = open('Шаблоны/GetCustomControl.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS, SERVICE_CODE = '0000')
    response = pgu_send(IS, req, soapaction='GetCustomControl', pre='err')
    status = getStatus(response)
    if status == 'REJECT':
        print('ERROR пример для GetCustomControl получен')
    else:
        print('Ошибка! ERROR пример для GetCustomControl неполучен. Ответ со статусом', status)
        err += 1
    return err


def getStatus(resp):
    try:
        status = parseString(resp).getElementsByTagName('smev:Status')[0].firstChild.nodeValue
    except:
        status = 'TECH_ERROR'
    return status


def set_request(IS):
    err = 0
    '''Функция получает OK, отмена заявления, ERROR пример для SetRequest'''

    # Для SetRequest берем шаблон, заполняем в нем нужные поля
    req = open('Шаблоны/SetRequest.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    response = pgu_send(IS, req, soapaction='SetRequest', pre='ok')
    status = getStatus(response)
    if status == 'ACCEPT':
        print ('ОК пример для SetRequest получен')
    else:
        print ('Ошибка! ОК пример для SetRequest неполучен')
        err += 1

    # ERROR пример
    req = open('Шаблоны/GetSettings.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS, SERVICE_CODE = '0000')
    response = pgu_send(IS, req, soapaction='SetRequest', pre='err')
    status = getStatus(response)
    if  status == 'REJECT':
        print ('ERROR пример для SetRequest получен')
    else:
        print ('Ошибка! ERROR пример для SetRequest неполучен')
        err += 1

    # Пример для CANCEL
    req = open('Шаблоны/SetRequest_cancel.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    response = pgu_send(IS, req, soapaction='SetRequest', pre='cancel')
    status = getStatus(response)
    if status == 'ACCEPT':
        print ('ОК пример для SetRequest(Cancel) получен')
    else:
        print ('Ошибка! ОК пример для SetRequest(Cancel) неполучен')
        err += 1

    # Пример ошибки для CANCEL
    # Еще раз пытаемся удалить уже удаленное заявление
    response = pgu_send(IS, req, soapaction='SetRequest', pre='cancel_err')
    status = getStatus(response)
    if status == 'REJECT':
        print ('ERROR пример для SetRequest(Cancel) получен')
    else:
        print ('Ошибка! ERROR пример для SetRequest(Cancel) неполучен')
        err += 1
    return err


def get_sprav(IS):
    err = 0
    '''Получает КП для метода GetSprav: список ОСЗН, банков и ошибку'''

    # Список ОСЗН
    req = open('Шаблоны/GetSprav_oszn.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    response = pgu_send(IS, req, soapaction='GetSprav', pre='oszn')
    status = getStatus(response)
    if status == 'RESULT':
        print ('Пример для GetSprav  Список ОСЗН получен')
    else:
        print ('Ошибка! Пример для GetSprav  Список ОСЗН не получен, пришел статус', status)
        err += 1

    # Список банков
    req = open('Шаблоны/GetSprav_bank.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    response = pgu_send(IS, req, soapaction='GetSprav', pre='bank')
    status = getStatus(response)
    if status == 'RESULT':
        print ('Пример для GetSprav  Список банков получен')
    else:
        print ('Ошибка! Пример для GetSprav  Список банков не получен, пришел статус', status)
        err += 1

    # Ошибка при получении списка банков
    req = open('Шаблоны/GetSprav_bank.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS, SERVICE_CODE = '0000')
    response = pgu_send(IS, req, soapaction='GetSprav', pre='bank_err')
    status = getStatus(response)
    if status == 'REJECT':
        print ('Пример c ошибкой для GetSprav  Список банков получен')
    else:
        print ('Ошибка! Пример c ошибкой для GetSprav  Список банков не получен, пришел статус', status)
        err +=1
    return err


def get_req_doc(IS):
    '''Получает КП для метода GetRequiredDocuments, возвращает ОК ответ сервера, чтобы потом из него достать ID документа'''

    # ERROR
    req = open('Шаблоны/GetReqDocuments.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS, SERVICE_CODE='0000')
    response = pgu_send(IS, req, soapaction='GetRequiredDocuments', pre='err')
    status = getStatus(response)
    if status == 'REJECT':
        print('Пример REJECT для GetRequiredDocuments получен')
    else:
        print('Ошибка! REJECT для GetRequiredDocuments не получен, пришел статус', status)

    # OK
    req = open('Шаблоны/GetReqDocuments.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    response = pgu_send(IS, req, soapaction='GetRequiredDocuments', pre='ok')
    status = getStatus(response)
    if status == 'RESULT':
        print('Пример OK для GetRequiredDocuments получен')
    else:
        print('Ошибка! Пример ОК для GetRequiredDocuments не получен, пришел статус', status)
    return(response)


def get_doc_by_id(doc_id, IS):
    '''Получает КП для метода GetDocById, получает ID документа'''
    # OK
    err = 0
    req = open('Шаблоны/GetDocByID.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    # добавляем ID документа
    req = req.replace ('#ID_DOC#', doc_id)
    response = pgu_send(IS, req, soapaction='GetDocById', pre='ok')
    status = getStatus(response)
    if status == 'RESULT':
        print('Пример OK для GetDocById получен')
    else:
        print('Ошибка! Пример ОК для GetDocById не получен, пришел статус', status)
        err +=1

    # error
    req = open('Шаблоны/GetDocByID.xml', mode='r', encoding="utf8").read()
    req = pguChange(req, IS)
    # добавляем ID документа
    req = req.replace ('#ID_DOC#', 'ERROR_ID')
    response = pgu_send(IS, req, soapaction='GetDocById', pre='err')
    status = getStatus(response)
    if status == 'REJECT':
        print('Пример REJECT для GetDocById получен')
    else:
        print('Ошибка! Пример REJECT для GetDocById не получен, пришел статус', status)
        err +=1
    return err

# Описание ИС: Наименование, мнемоника, ОКТМО
#
#IS = ('Информационная система для предоставления государственных социальных услуг в Тюменской области', '926701721', '71000000') # Тюменская область
#IS = ('Адресная социальная помощь', '109101371', '24000000') # Ивановская область
#IS = ('ИС Адресная социальная помощь', '918801651', '64000000') #Сахалин
 # Рязань


def test_PGU(IS):
    err = 0
    start = time.time()
    print("Автоматическая документация на веб-сервис интеграции в ПГУ")
    print("********************************************")
    print("Тестирование будет выполнено по услуге с кодом %s." % IS['servicecode'])
    err += smev.get_wsdl(IS, url=IS['url']+'pgu/RequestAllowanceServiceSOAP256.ashx', name='pgu.wsdl')
    err += get_settings(IS)
    err += get_custom_control(IS)
    err += set_request(IS)
    err += get_sprav(IS)
    # Особая фукция, возвращает ответ в XML
    response = get_req_doc(IS)
    # Извлекаем из него первый ID документа
    doc_id = None
    try:
        for node in parseString(response).getElementsByTagName('AttachIdRef'):
            if node.firstChild:
                # первый непустой тег
                doc_id = node.firstChild.nodeValue
                break
    except:
        print('Не удалось найти ID документа')
    # вызываем функцию получения документа, передаем ID
    if doc_id:
        err += get_doc_by_id(doc_id, IS)
    else:
        print("Ошибка! OK пример для GetDocById не получен")
        err +=1
    post = {
        "date": datetime.datetime.now(),
        "name": "Тестирование ПГУ сервиса",
        "comment": IS['comment'],
        "version": IS['version'],
        "data":
            {
                "Итого": time.time() - start
            },
        "errors": err,
        "address": 'http://%s:%s%sSMEV/pgu/RequestAllowanceServiceSOAP256.ashx' % (IS['adr'], IS['port'], IS['url'])
        }
    return post

