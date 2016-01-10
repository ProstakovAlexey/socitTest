# coding=utf8
__author__ = 'Prostakov Alexey'
"""
Описание
**********************

Входные данные
**********************

Выходные данные
**********************

"""
import sys
from selenium import webdriver
import time
import datetime

def test_web(IS):
    """
    :param base_url: ссылка на ТИ которую надо протестировать, по умолчанию ТУ
    :return: структура к записи, кол-во ошибок
    """
    err = 0
    base_url = 'http://%s:%s%s' % (IS['adr'], IS['port'], IS['url'])
    print("Выполняется тест для веб-интерфейса ТИ")
    print('********************************************')
    try:
        driver = webdriver.Firefox()
        driver.implicitly_wait(30)
        runTime = list()

        # запуск теста
        runTime.append(time.time())
        # заходим и останавливает очередь запросов (если она запущена)
        driver.get(base_url + "ATN/Login.aspx")
        driver.find_element_by_id("tbLogin").clear()
        driver.find_element_by_id("tbLogin").send_keys("Prostakov")
        driver.find_element_by_id("tbPassw").clear()
        driver.find_element_by_id("tbPassw").send_keys("fish13")
        driver.find_element_by_css_selector("img").click()
        driver.find_element_by_css_selector("#ml_SMEV > span.atn-btn-label").click()
        driver.find_element_by_id("mr_SMEV_OUTPUT").click()
        driver.find_element_by_css_selector("#SMEV_REQUEST77_FirstPage > img").click()
        driver.find_element_by_id("lbAction_SMEV_REQUEST").click()
        driver.find_element_by_id("listact77_SMEV_REQUEST77_2").click()
        driver.find_element_by_css_selector("#lbExit > span.atn-btn-label").click()
        driver.find_element_by_css_selector("img").click()
        runTime.append(time.time())

        # запуск очереди запросов
        driver.find_element_by_id("tbLogin").clear()
        driver.find_element_by_id("tbLogin").send_keys("Prostakov")
        driver.find_element_by_id("tbPassw").clear()
        driver.find_element_by_id("tbPassw").send_keys("fish13")
        driver.find_element_by_css_selector("span.atn-btn-label").click()
        driver.find_element_by_id("mr_SMEV_OUTPUT").click()
        driver.find_element_by_css_selector("#lbAction_SMEV_REQUEST > span.atn-btn-label").click()
        driver.find_element_by_id("listact77_SMEV_REQUEST77_0").click()
        runTime.append(time.time())

        # получение скриншота
        driver.find_element_by_id("lbAction_SMEV_REQUEST").click()
        driver.find_element_by_id("listact77_SMEV_REQUEST77_3").click()
        driver.get_screenshot_as_file('Очередь.png')
        driver.find_element_by_css_selector("#popupLBClose > img").click()

        # просмотр СМЭВ запросов
        driver.find_element_by_css_selector("#SMEV_REQUEST77_NextPage > img").click()
        driver.find_element_by_css_selector("#SMEV_REQUEST77_NextPage > img").click()
        driver.find_element_by_css_selector("#SMEV_REQUEST77_NextPage > img").click()
        driver.find_element_by_css_selector("#SMEV_REQUEST77_NextPage > img").click()
        driver.find_element_by_id("SMEV_REQUEST77_InpNum").clear()
        driver.find_element_by_id("SMEV_REQUEST77_InpNum").send_keys("20")
        driver.find_element_by_css_selector("#SMEV_REQUEST77_NextPage > img").click()
        driver.find_element_by_id("lbExit").click()
        runTime.append(time.time())

        # просмотр заявок ПГУ
        driver.find_element_by_id("ml_PGU").click()
        driver.find_element_by_id("mr_REQUEST").click()
        driver.find_element_by_css_selector("#ESERVICE_REQUEST77_FirstPage > img").click()
        driver.find_element_by_css_selector("#ESERVICE_REQUEST77_NextPage > img").click()
        driver.find_element_by_css_selector("#ESERVICE_REQUEST77_NextPage > img").click()
        driver.find_element_by_css_selector("#ESERVICE_REQUEST77_NextPage > img").click()
        driver.find_element_by_id("lbExit").click()
        driver.find_element_by_id("mr_USLUGI").click()
        driver.find_element_by_css_selector("#ESERVICE_SOCIAL77_NextPage > img").click()
        driver.find_element_by_css_selector("#ESERVICE_SOCIAL77_NextPage > img").click()
        driver.find_element_by_id("lbExit").click()
        runTime.append(time.time())

        # просмотр протокола ошибок
        driver.find_element_by_css_selector("#ml_LOGS > span.atn-btn-label").click()
        driver.find_element_by_id("mr_ID2").click()
        driver.find_element_by_css_selector("#ESERVICE_ERRORS77_FirstPage > img").click()
        driver.find_element_by_css_selector("#ESERVICE_ERRORS77_NextPage > img").click()
        driver.find_element_by_css_selector("#ESERVICE_ERRORS77_NextPage > img").click()
        driver.find_element_by_css_selector("#lbExit > span.atn-btn-label").click()
        driver.find_element_by_id("mr_ID3").click()
        runTime.append(time.time())

        # просмотр протокола событий
        driver.find_element_by_css_selector("#PROTOCOL77_FirstPage > img").click()
        driver.find_element_by_css_selector("#PROTOCOL77_NextPage > img").click()
        driver.find_element_by_css_selector("#PROTOCOL77_NextPage > img").click()
        driver.find_element_by_css_selector("#PROTOCOL77_NextPage > img").click()
        driver.find_element_by_css_selector("#lbExit > span.atn-btn-label").click()
        runTime.append(time.time())

        # просмотр входящих СМЭВ запросов
        driver.find_element_by_css_selector("#ml_SMEV > span.atn-btn-label").click()
        driver.find_element_by_id("mr_SMEV_INPUT").click()
        driver.find_element_by_css_selector("#SMEV_FOIVLOG77_NextPage > img").click()
        driver.find_element_by_css_selector("#SMEV_FOIVLOG77_NextPage > img").click()
        driver.find_element_by_css_selector("#SMEV_FOIVLOG77_NextPage > img").click()
        driver.find_element_by_css_selector("#SMEV_FOIVLOG77_NextPage > img").click()
        driver.find_element_by_css_selector("#SMEV_FOIVLOG77_LastPage > img").click()
        driver.find_element_by_css_selector("#SMEV_FOIVLOG77_PrevPage > img").click()
        driver.find_element_by_css_selector("#SMEV_FOIVLOG77_PrevPage > img").click()
        driver.find_element_by_css_selector("#SMEV_FOIVLOG77_FirstPage > img").click()
        driver.find_element_by_id("lbExit").click()
        runTime.append(time.time())

        # остановка СМЭВ запросов
        driver.find_element_by_id("ml_SMEV").click()
        driver.find_element_by_id("mr_SMEV_OUTPUT").click()
        driver.find_element_by_css_selector("#lbAction_SMEV_REQUEST > span.atn-btn-label").click()
        driver.find_element_by_id("listact77_SMEV_REQUEST77_2").click()
        driver.find_element_by_css_selector("#lbExit > span.atn-btn-label").click()
        driver.find_element_by_css_selector("img").click()
        runTime.append(time.time())

        driver.find_element_by_id("tbLogin").clear()
        driver.find_element_by_id("tbPassw").clear()
        driver.close()

        print('''Остановка очереди запросов: %s сек
        Запуск очереди запросов: %s сек
        Просмотр СМЭВ запросов: %s сек
        Просмотр заявлений ПГУ: %s сек
        Просмотр протокола ошибок: %s сек
        Просмотр протокола событий: %s сек
        Просмотр входящих СМЭВ запросов: %s сек
        Остановка очереди запросов: %s сек
        -----------------
        Итого: %s сек''' % (runTime[1] - runTime[0],
                            runTime[2] - runTime[1],
                            runTime[3] - runTime[2],
                            runTime[4] - runTime[3],
                            runTime[5] - runTime[4],
                            runTime[6] - runTime[5],
                            runTime[7] - runTime[6],
                            runTime[8] - runTime[7],
                            runTime[8] - runTime[0]))
        post = {
            "date": datetime.datetime.now(),
            "name": "Тестирование веб-интерфейса ТИ",
            "comment": IS['comment'],
            "version": IS['version'],
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
        }
    except:
        print("Во время выполнения теста для ТИ возникли ошибки")
        Type, Value, Trace = sys.exc_info()
        print ("Ошибка Тип:", Type, "Значение:", Value, "Трассировка:", Trace)
        err += 1
        post = {
            "date": datetime.datetime.now(),
            "name": "Тестирование веб-интерфейса ТИ",
            "comment": IS['comment'],
            "version": IS['version'],
            "errors": err,
            "address": base_url
            }
        driver.close()
    return post, err
