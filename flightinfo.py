# -*- coding: utf-8 -*-
from xml.etree.ElementTree import parse
from http.client import HTTPConnection
import datetime as DT
from ftplib import FTP

class FlightInfo(list):
    '''Info about air flight. Structure:
    [
      {'AD': ' ', FLY': '  ', 'AIRCRAFT': '  ', 'PUNKTDIST': '  ',
      'PORTDIST': '   ', 'CARRNAME': '   ', 'TPLAN': '   ', 'DPLAN': '   ',
      'TEXP': '', 'DEXP': '', 'TFACT': '', 'DFACT': '', 'STATUS': '', #this is xml data
      'TIMEFACT': '', 'TIMEPLAN': '  ', 'TIMEEXP': '' # datatime formats
      },
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
                            reiseInfo['STATUS'] = 'Вылет по расч. времени ' + reiseInfo['TEXP']
                        elif reiseInfo['TIMEEXP'] - DT.timedelta(seconds=7200) >= DT.datetime.now() >= reiseInfo['TIMEEXP'] - DT.timedelta(seconds=2400):
                            reiseInfo['STATUS'] = 'Регистрация пассажиров и багажа'
                        elif reiseInfo['TIMEEXP'] - DT.timedelta(seconds=2400) > DT.datetime.now() >= reiseInfo['TIMEEXP']:
                            reiseInfo['STATUS'] = 'Посадка пассажиров на борт'
                        else:
                            reiseInfo['STATUS'] = ''
                #arrivels
                else:
                    if reiseInfo['TIMEEXP'] is None:
                        reiseInfo['STATUS'] = 'Прилет ожидается по плану'
                    else:
                        reiseInfo['STATUS'] = 'Прилет по расч. времени ' + reiseInfo['TEXP']
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

    def savetofile(self, filename, template, codepage='utf-8'):
        f = open(filename, 'w', encoding=codepage)
        f.write(self.converttoHTML(template))
        f.close()

def sendfiletoftp(filename, server, username=None, password=None):
    ftp = FTP(server, username, password)
    file = open(filename, 'rb')
    ftp.storlines('STOR '+filename, file)
    file.close()
    ftp.close()

def getflighttime(flight):
    return flight['TIMEPLAN']

if __name__ == '__main__':
    #astrahan
    # reqarrivalsall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:1,3"
    # reqdeparturesall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:0,3"
    #internal apex server 93.157.148.58
    reqarrivalsreg = "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,0"
    reqarrivalschart = "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,1"
    reqdeparturesreg = "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,0"
    reqdepartureschart = "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,1"
    arrivels = FlightInfo()
    arrivels.getfromserver("172.17.10.2", 7777, reqarrivalsreg)
    arrivels.getfromserver("172.17.10.2", 7777, reqarrivalschart)
    depatures = FlightInfo()
    depatures.getfromserver("172.17.10.2", 7777, reqdeparturesreg)
    depatures.getfromserver("172.17.10.2", 7777, reqdepartureschart)

    depatures.sort(key=getflighttime)
    arrivels.sort(key=getflighttime)

    arrivels.today().savetofile('online_arrivals.php', 'tmponline_arrivals.php', 'cp1251')
    depatures.today().savetofile('online_departure.php', 'tmponline_departure.php', 'cp1251')
    sendfiletoftp('online_arrivals.php', '93.170.129.93', 'airport_upload', '7xXS2VZA')
    sendfiletoftp('online_departure.php', '93.170.129.93', 'airport_upload', '7xXS2VZA')

    arrivels.savetofile('bdc_arrivals.php', 'templatebdc.php', 'cp1251')
    depatures.savetofile('bdc_departure.php', 'templatebdc.php', 'cp1251')
    sendfiletoftp('bdc_arrivals.php', '93.170.129.93', 'airport_upload', '7xXS2VZA')
    sendfiletoftp('bdc_departure.php', '93.170.129.93', 'airport_upload', '7xXS2VZA')

    arrivels.today().savetofile('arrivals.php', 'templatebdc.php', 'cp1251')
    depatures.today().savetofile('departure.php', 'templatebdc.php', 'cp1251')
    sendfiletoftp('arrivals.php', '172.17.10.120', 'admin', '34652817')
    sendfiletoftp('departure.php', '172.17.10.120', 'admin', '34652817')
