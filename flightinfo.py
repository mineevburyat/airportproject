# -*- coding: utf-8 -*-
from xml.etree.ElementTree import parse
from http.client import HTTPConnection
import datetime as DT
from ftplib import FTP

class FlightInfo(list):
    '''Info about air flight. Structure: [
                                            {'AD': 'вылет или прилет
                                             'FLY': '  ',
                                             'AIRCRAFT': '  '
                                             'PUNKTDIST': '  ',
                                             'PORTDIST': '   ',
                                             'CARRNAME': '   ',
                                             'TPLAN': '   ',
                                             'DPLAN': '   ',
                                             'TEXP': '',
                                             'DEXP': '',
                                             'TFACT': '',
                                             'DFACT': '',
                                             'STATUS': '',
                                             'TIMEFACT': '',
                                             'TIMEPLAN': '  ',
                                             'TIMEEXP': ''},
                                             {...}, ...
                                        ]
    '''

    def __init__(self):
        self = []

    def getfromserver(self, server, port, request):
        '''запросить xml и сохранить в файл'''
        filename = "tmpxmlstructure.xml"
        conector = HTTPConnection(server, port)
        conector.request("GET", request)
        result = conector.getresponse()
        file = open(filename, "w")
        file.write(result.read().decode("utf-8"))
        file.close()
        conector.close()
        '''начать парсить xml файл в удобную структуру'''
        reiseInfo = {}
        tree = parse(filename)
        for fly in tree.findall('FLY'):
            reiseInfo['FLY'] = fly.attrib['number']
            airportdist = ''
            distinetion = ''
            for ReiseElem in fly.getchildren():
                if ReiseElem.tag.find('PORTDIST') != -1:
                    if ReiseElem.text is not None:
                        if airportdist == '':
                            airportdist = ReiseElem.text
                        else:
                            airportdist += ' - ' + ReiseElem.text
                    continue
                if ReiseElem.tag.find('PUNKTDIST') != -1:
                    if ReiseElem.text is not None:
                        if distinetion == '':
                            distinetion = ReiseElem.text
                        else:
                            distinetion +=  ' - '+ ReiseElem.text
                    continue
                reiseInfo.setdefault(ReiseElem.tag, ReiseElem.text)
            reiseInfo['PORTDIST'] = airportdist
            reiseInfo['PUNKTDIST'] = distinetion
            #перевести время
            if reiseInfo['TPLAN'] is None or reiseInfo['DPLAN'] is None:
                reiseInfo['TIMEPLAN'] = None
            else:
                reiseInfo['TIMEPLAN'] = DT.datetime.strptime(reiseInfo['DPLAN'] + ' ' + reiseInfo['TPLAN'], '%d.%m.%Y %H:%M')
            if reiseInfo['TEXP'] is None or reiseInfo['DEXP'] is None:
                reiseInfo['TIMEEXP'] = None
            else:
                reiseInfo['TIMEEXP'] = DT.datetime.strptime(reiseInfo['DEXP'] + ' ' + reiseInfo['TEXP'], '%d.%m.%Y %H:%M')
            if reiseInfo['TFACT'] is None or reiseInfo['DFACT'] is None:
                reiseInfo['TIMEFACT'] = None
            else:
                reiseInfo['TIMEFACT'] = DT.datetime.strptime(reiseInfo['DFACT'] + ' ' + reiseInfo['TFACT'], '%d.%m.%Y %H:%M')
            if reiseInfo['STATUS'] is None:
                #departure
                if reiseInfo['AD'] == '0':
                    if reiseInfo['TIMEEXP'] is None:
                        reiseInfo['STATUS'] = 'Вылет по плану'
                    else:
                        if reiseInfo['TIMEEXP'] - DT.timedelta(seconds=7200) > DT.datetime.now():
                            reiseInfo['STATUS'] = 'Вылет по расчетному времени'
                        elif reiseInfo['TIMEEXP'] - DT.timedelta(seconds=7200) >= DT.datetime.now() >= reiseInfo['TIMEEXP'] - DT.timedelta(seconds=2400):
                            reiseInfo['STATUS'] = 'Регистрация пассажиров и багажа'
                        elif reiseInfo['TIMEEXP'] - DT.timedelta(seconds=2400) > DT.datetime.now() >= reiseInfo['TIMEEXP']:
                            reiseInfo['STATUS'] = 'Посадка пассажиров на борт'
                #arrivels
                else:
                    if reiseInfo['TIMEEXP'] is None:
                        reiseInfo['STATUS'] = 'Прилет ожидается по плану'
                    else:
                        reiseInfo['STATUS'] = 'Прилет по расчетному времени'
            self.append(reiseInfo)
            reiseInfo = {}

    def __str__(self):
        st = ''
        for elem in self:
            st += str(elem) + '\n'
        return st

    def today(self):
        result = FlightInfo()
        for flight in self:
            if flight['TIMEFACT'] is not None:
                if flight['TIMEFACT'].date() == DT.datetime.today().date():
                    result.append(flight)
                continue
            else:
                if flight['TIMEEXP'] is not None:
                    if flight['TIMEEXP'].date() == DT.datetime.today().date():
                        result.append(flight)
                    continue
                else:
                    if flight['TIMEPLAN'].date() == DT.datetime.today().date():
                        result.append(flight)
        return result

    def yesterday(self):
        result = FlightInfo()
        for flight in self:
            if flight['TIMEFACT'] is not None:
                if flight['TIMEFACT'].date() == DT.datetime.today().date() - DT.timedelta(days=1):
                    result.append(flight)
                continue
            else:
                if flight['TIMEEXP'] is not None:
                    if flight['TIMEEXP'].date() == DT.datetime.today().date() - DT.timedelta(days=1):
                        result.append(flight)
                    continue
                else:
                    if flight['TIMEPLAN'].date() == DT.datetime.today().date() - DT.timedelta(days=1):
                        result.append(flight)
        return result

    def tomorrow(self):
        result = FlightInfo()
        for flight in self:
            if flight['TIMEFACT'] is not None:
                if flight['TIMEFACT'].date() == DT.datetime.today().date() + DT.timedelta(days=1):
                    result.append(flight)
                continue
            else:
                if flight['TIMEEXP'] is not None:
                    if flight['TIMEEXP'].date() == DT.datetime.today().date() + DT.timedelta(days=1):
                        result.append(flight)
                    continue
                else:
                    if flight['TIMEPLAN'].date() == DT.datetime.today().date() + DT.timedelta(days=1):
                        result.append(flight)
        return result

    def converttoHTML(self, template):
        '''get and dileved template and return string in HTML. Where template is name of file. Template is frie parts: start
        , body whith data and end'''
        partlines = ''
        parts = []
        fdiscript = open(template, 'r')
        for line in fdiscript:
            if line.find('<!-- separator -->') != -1:
                parts.append(partlines)
                partlines = ''
            else:
                partlines += line
        parts.append(partlines)
        fdiscript.close()
        if len(parts) != 3:
            print('Error - !')
        st = ''
        for flight in self:
            st += parts[1].format(**flight)
        parts[1] = st
        st = ''.join(parts)
        return st

    def savetofile(self, filename, template, filterfunc=None):
        f = open(filename, 'w')
        if filterfunc:
            f.write(self.filterfunc().converttoHTML(template))
        else:
            f.write(self.converttoHTML(template))
        f.close()

if __name__ == '__main__':
    #astrahan
    # reqarrivalsall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:1,3"
    # reqdeparturesall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:0,3"
    #internal apex server 93.157.148.58
    reqarrivalsall = "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,3"
    reqdeparturesall = "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,3"
    arrivels = FlightInfo()
    arrivels.getfromserver("172.17.10.2", 7777, reqarrivalsall)
    depatures = FlightInfo()
    depatures.getfromserver("172.17.10.2", 7777, reqdeparturesall)
    #print(arrivels)
    arrivels.savetofile('online_arrivals.php', 'tmponline_arrivals.php')
    depatures.savetofile('online_departure.php', 'tmponline_departure.php')
    ftp = FTP('93.170.129.93')
    ftp.login(user='airport_upload', passwd='7xXS2VZA')
    filename = 'online_departure.php'
    f = open(filename,'r')
    ftp.storbinary('STOR ' + filename, f)
    f.close()
    filename = 'online_arrivals.php'
    f = open(filename, 'r')
    ftp.storbinary('STOR ' + filename, f)
    f.close()
    ftp.close()


    #f = open('arrivalBDC.html', 'w')
    #f.write(arrivels.converttoHTML('HTMLtamplateBDC.html'))
    #f.close()
    #f = open('departureBDC.html', 'w')
    #f.write(depatures.converttoHTML('HTMLtamplateBDC.html'))
    #f.close()