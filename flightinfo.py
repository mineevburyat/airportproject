# -*- coding: utf-8 -*-
from xml.etree.ElementTree import parse
from http.client import HTTPConnection
import datetime as DT
from ftplib import FTP
import pickle

class FlightsInfo(dict):
    '''Structure: {'FLY': {STATUSCHECKIN: , STATUSBOARD: , STATUSBAG,
                            CHECKIN: '', GATE: '', BAGGAGE: '' '''
    def __init__(self):
        self = {}

    def updatefromflightes(self, flights):
        flynew = {'STATCHECKIN': False, 'STATBOARD': False, 'STATBAGG': False,
                  'CHECKINS': '', 'GATE': '', 'BAGGAGE': ''}
        for flight in flights:
            fly = flight['FLY']
            if fly in self:
                continue
            else:
                self.setdefault(fly, flynew)
        isnotflights = True
        tmplst = []
        for flight in flights:
            tmplst.append(flight['FLY'])



    def __str__(self):
        st = ''
        for flightinfo in self:
            st += str(flightinfo) + ': ' + str(self[flightinfo]) + '\n'
        return st

class Flights(list):
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
                now = DT.datetime.now()
                if reiseInfo['AD'] == '0':
                    if reiseInfo['TIMEEXP'] is None:
                        reiseInfo['STATUS'] = 'Вылет по плану'
                    else:
                        if now < reiseInfo['TIMEEXP'] - DT.timedelta(seconds=7200):
                            reiseInfo['STATUS'] = 'Вылет по расч. времени ' + reiseInfo['TEXP']
                        elif reiseInfo['TIMEEXP'] - DT.timedelta(seconds=7200) <= now <= reiseInfo['TIMEEXP'] - DT.timedelta(seconds=2400):
                            reiseInfo['STATUS'] = 'Регистрация пассажиров и багажа'
                        elif reiseInfo['TIMEEXP'] - DT.timedelta(seconds=2400) < now <= reiseInfo['TIMEEXP']:
                            reiseInfo['STATUS'] = 'Посадка пассажиров на борт'
                        else:
                            reiseInfo['STATUS'] = 'Уточнение времени вылета'
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
        result = Flights()
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
        result = Flights()
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
        result = Flights()
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
    def save(self, filename):
        f = open(filename, 'wb')
        pickle.dump(self, f)
    def isdifferent(self, picklefile):
        flag = False
        f = open(picklefile, 'rb')
        oldinfo = pickle.load(f)
        for old, new in zip(oldinfo, self):
            if old != new:
                flag = True
                break
        return flag
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

def savetofile(str, filename, codepage='utf-8'):
        f = open(filename, 'w', encoding=codepage)
        f.write(str)
        f.close()
def sendfilestoftp(filenamelist, server, username=None, password=None):
    for filename in filenamelist:
        ftp = FTP(server, username, password)
        file = open(filename, 'rb')
        ftp.storlines('STOR '+filename, file)
        file.close()
        ftp.close()
def getflighttime(flight):
    return flight['TIMEPLAN']


if __name__ == '__main__':
    arrivalxmlreqreg = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,0")
    arrivalxmlreqchart = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,1")
    arrivals = Flights()
    arrivals.getfromserver(*arrivalxmlreqreg)
    arrivals.getfromserver(*arrivalxmlreqchart)
    departures = Flights()
    departxmlreqreg = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,0")
    departxmlreqchart = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,1")
    departures.getfromserver(*departxmlreqreg)
    departures.getfromserver(*departxmlreqchart)
    departures.sort(key=getflighttime)
    arrivals.sort(key=getflighttime)
    arrivals.save('arrivals.pkl')
    departures.save('departures.pkl')
    departurepicklefile = 'departures.pkl'
    arrivalspicklefile = 'arrivals.pkl'
    internalftp = ('172.17.10.120', 'admin', '34652817')
    externalftp = ('93.170.129.93', 'airport_upload', '7xXS2VZA')
    templdeparttablo = 'tmponline_departure.php'
    templarrivaltablo = 'tmponline_arrivals.php'
    templbdc = 'templatebdc.php'
    fsitedepart = 'online_departure.php'
    fsitearrive = 'online_arrivals.php'
    fbdcdepart = 'bdc_departure.php'
    fbdcarrive = 'bdc_arrivals.php'
    ftablodepart = 'departure.php'
    ftabloarrive = 'arrivals.php'

    '''arrivalsinfo = FlightsInfo()
    arrivalsinfo.updatefromflightes(arrivals)
    print(arrivalsinfo)

    '''
    if departures.isdifferent(departurepicklefile):
        departures.save(departurepicklefile)
        savetofile(departures.today().converttoHTML(templdeparttablo), fsitedepart, 'cp1251')
        savetofile(departures.converttoHTML(templbdc), fbdcdepart, 'cp1251')
        savetofile(departures.today().converttoHTML(templbdc), ftablodepart, 'cp1251')
        sendfilestoftp([ftablodepart], *internalftp)
        sendfilestoftp([fbdcdepart, fsitedepart], *externalftp)
        print('Send departure')
    else:
        print('No diff on departure')
    if arrivals.isdifferent(arrivalspicklefile):
        arrivals.save(arrivalspicklefile)
        savetofile(arrivals.today().converttoHTML(templarrivaltablo), fsitearrive, 'cp1251')
        savetofile(arrivals.converttoHTML(templbdc), fbdcarrive, 'cp1251')
        savetofile(arrivals.today().converttoHTML(templbdc),ftabloarrive, 'cp1251')
        sendfilestoftp([ftabloarrive], *internalftp)
        sendfilestoftp([fsitearrive, fbdcarrive], *externalftp)
        print('Send arrivals')
    else:
        print('No diff on arrivals')

