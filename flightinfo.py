# -*- coding: utf-8 -*-
import sys
import os
from xml.etree.ElementTree import parse
import datetime as DT
from ftplib import FTP
import pickle
import configparser
if int(sys.version_info[0]) == 3:
    from http.client import HTTPConnection
else:
    raise Exception("Version python less then 3")

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

    def getfromxml(self, filename):
        '''начать парсить xml файл в удобную структуру'''
        flightinfo = {}
        tree = parse(filename)
        for fly in tree.findall('FLY'):
            flycod = fly.attrib['number']
            if flycod == '':
                continue
            flightinfo['FLY'] = flycod
            airportdist = ''
            destinetion = ''
            for flightparam in fly.getchildren():
                if flightparam.tag.find('PORTDIST') != -1:
                    if flightparam.text is not None:
                        if airportdist == '':
                            airportdist = flightparam.text
                        else:
                            airportdist += ' -<br> ' + flightparam.text
                    continue
                if flightparam.tag.find('PUNKTDIST') != -1:
                    if flightparam.text is not None:
                        if destinetion == '':
                            destinetion = flightparam.text
                        else:
                            destinetion +=  ' -<br> '+ flightparam.text
                    continue
                flightinfo.setdefault(flightparam.tag, flightparam.text)
            flightinfo['PORTDIST'] = airportdist
            flightinfo['PUNKTDIST'] = destinetion
            #перевести дату и время в удобный формат
            if flightinfo['TPLAN'] is None or flightinfo['DPLAN'] is None:
                flightinfo['TIMEPLAN'] = None
            else:
                flightinfo['TIMEPLAN'] = DT.datetime.strptime(flightinfo['DPLAN'] + ' ' + flightinfo['TPLAN'], '%d.%m.%Y %H:%M')
            if flightinfo['TEXP'] is None or flightinfo['DEXP'] is None:
                flightinfo['TIMEEXP'] = None
            else:
                flightinfo['TIMEEXP'] = DT.datetime.strptime(flightinfo['DEXP'] + ' ' + flightinfo['TEXP'], '%d.%m.%Y %H:%M')
            if flightinfo['TFACT'] is None or flightinfo['DFACT'] is None:
                flightinfo['TIMEFACT'] = None
            else:
                flightinfo['TIMEFACT'] = DT.datetime.strptime(flightinfo['DFACT'] + ' ' + flightinfo['TFACT'], '%d.%m.%Y %H:%M')
            self.append(flightinfo)
            flightinfo = {}

    def handlenullstatus(self):
        HOUR2 = DT.timedelta(seconds=7200)
        MIN40 = DT.timedelta(seconds=2400)
        MIN20 = DT.timedelta(seconds=1200)
        DEPARTPLAN = 'Вылет по плану'
        DEPARTTIMEEXP = 'Вылет в '
        STARTCHEKIN = 'Регистрация пассажиров'
        CHECKIN = 'Регистрация. Стойки: '
        BETWEENCHECKBOARD = 'Регистрация закрыта'
        BOARDING = 'Посадка пассажиров'
        UPDATETIMEDEPART = 'Посадка закрыта'
        ARRIVEPLAN = 'Ожидается по плану'
        ARRIVEEXP = 'Ожидается в '
        #отработать пустые статусы
        for flight in self:
            if flight['STATUS'] is None:
                fly = flight['FLY']
                now = DT.datetime.now()
                timeexp = flight['TIMEEXP']
                #departure
                if flight['AD'] == '0':
                    if timeexp is None:
                        flight['STATUS'] = DEPARTPLAN
                    else:
                        if now < timeexp - HOUR2:
                            flight['STATUS'] = DEPARTTIMEEXP + flight['TEXP']
                        elif timeexp - HOUR2 <= now <= timeexp - MIN40:
                            flight['STATUS'] = STARTCHEKIN
                        elif timeexp - MIN40 < now <= timeexp - MIN20:
                            flight['STATUS'] = BETWEENCHECKBOARD
                        elif timeexp - MIN20 < now <= timeexp:
                            flight['STATUS'] = BOARDING
                        else:
                            flight['STATUS'] = UPDATETIMEDEPART
                #arrivels
                else:
                    if timeexp is None:
                        flight['STATUS'] = ARRIVEPLAN
                    else:
                        flight['STATUS'] = ARRIVEEXP + flight['TEXP']

    def __str__(self):
        st = ''
        for elem in self:
            st += str(elem) + '\n'
        return st

    def timewindow(self, pastsec=21600, futuresec=61200):
        result = Flights()
        now = DT.datetime.now()
        pastdelta = DT.timedelta(seconds=pastsec)
        futuredelta = DT.timedelta(seconds=futuresec)
        for flight in self:
            flag = False
            mintime = now - pastdelta
            maxtime = now + futuredelta
            if mintime <= flight['TIMEPLAN'] <= maxtime:
                flag = True
            else:
                if flight['TIMEEXP'] is not None:
                    if mintime < flight['TIMEEXP'] < maxtime:
                        flag = True
                else:
                    if flight['TIMEFACT'] is not None:
                        if mintime < flight['TIMEFACT'] < maxtime:
                            flag = True
            if flag:
                result.append(flight)
        return result

    def today(self):
        result = Flights()
        today = DT.datetime.today().date()
        for flight in self:
            flag = False
            if flight['TIMEPLAN'].date() == today:
                flag = True
            else:
                if flight['TIMEEXP'] is not None:
                    if flight['TIMEEXP'].date() == today:
                        flag = True
                if flight['TIMEFACT'] is not None:
                    if flight['TIMEFACT'].date() == today:
                        flag = True
            if flag:
                result.append(flight)
        return result

    def yesterday(self):
        result = Flights()
        yesterday = DT.datetime.today().date() - DT.timedelta(days=1)

        for flight in self:
            if flight['TIMEPLAN'].date() == yesterday\
                    or flight['TIMEEXP'].date() == yesterday \
                    or flight['TIMEFACT'].date() == yesterday:
                result.append(flight)
        return result

    def tomorrow(self):
        result = Flights()
        tomorrow = DT.datetime.today().date() + DT.timedelta(days=1)
        for flight in self:
            if flight['TIMEPLAN'].date() == tomorrow\
                    or flight['TIMEEXP'].date() == tomorrow \
                    or flight['TIMEFACT'].date() == tomorrow:
                result.append(flight)
        return result

    def save(self, filename):
        f = open(filename, 'wb')
        pickle.dump(self, f)
        return True

    def load(self, filename):
        try:
            f = open(filename, 'rb')
        except FileNotFoundError:
            return False
        self = pickle.load(f)
        return True

    def isdifferent(self, picklefile):
        flag = False
        try:
            f = open(picklefile, 'rb')
        except FileNotFoundError:
            return True
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
        if len(parts) < 3:
            raise Exception("Separators in template less then 2. The pattern should be divided into three parts")
        if len(parts) > 3:
            raise Exception("Separators in template more then 2. The pattern should be divided into three parts")
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
        return True

def sendfilestoftp(filenamelist, server, username=None, password=None):
    for filename in filenamelist:
        ftp = FTP(server, username, password)
        file = open(filename, 'rb')
        ftp.storlines('STOR '+filename, file)
        file.close()
        ftp.close()
    return True


def getxmlfromserver(filename, server, port, request):
    '''запросить xml и сохранить в файл'''
    if int(sys.version_info[0]) == 3:
        conector = HTTPConnection(server, port)
        conector.request("GET", request)
        result = conector.getresponse()
        file = open(filename, "w")
        file.write(result.read().decode("utf-8"))
        conector.close()
        file.close()
    else:
        raise Exception("Python version less then 3")


def getflighttime(flight):
    return flight['TIMEPLAN']


if __name__ == '__main__':
    xmlfile = 'xmldata.xml'
    arrivals = Flights()
    arrivalxmlreqchart = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,0")
    getxmlfromserver(xmlfile, *arrivalxmlreqchart)
    arrivals.getfromxml(xmlfile)
    arrivals.sort(key=getflighttime)
    departures = Flights()
    departxmlreqchart = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,0")
    getxmlfromserver(xmlfile, *departxmlreqchart)
    departures.getfromxml(xmlfile)
    departures.sort(key=getflighttime)
    os.remove(xmlfile)
    departures.handlenullstatus()
    arrivals.handlenullstatus()
    departurepicklefile = 'departures.pkl'
    arrivalspicklefile = 'arrivals.pkl'
    templdeparttablo = 'tmponline_arrivals.php'
    templarrivaltablo = 'tmponline_arrivals.php'
    templbdc = 'templatebdc.php'

    fsitedepart = 'online_departure.php'
    fsitearrive = 'online_arrivals.php'
    fbdcdepart = 'bdc_departure.php'
    fbdcarrive = 'bdc_arrivals.php'
    ftablodepart = 'departure.php'
    ftabloarrive = 'arrivals.php'
    fileconf = 'config.ini'
    try:
        conf = configparser.RawConfigParser()
        conf.read(fileconf)
        internalftp = (conf.get('internalftp', 'server'), conf.get('internalftp','user'),
                   conf.get('internalftp','pass'))
        externalftp = (conf.get('externalftp', 'server'), conf.get('externalftp','user'),
                   conf.get('externalftp','pass'))
    except configparser.NoSectionError:
        print('Error in config file: ', fileconf)
        exit()
    now = DT.datetime.now().time()

    for picklefile,fly,fsite,fbdc,ftablo in [(departurepicklefile,departures,fsitedepart,fbdcdepart,ftablodepart),
                                            (arrivalspicklefile, arrivals,fsitearrive,fbdcarrive,ftabloarrive)]:
        if fly.isdifferent(picklefile) or (0 <= now.minute <= 1):
            fly.save(picklefile)
            savetofile(fly.timewindow().converttoHTML(templdeparttablo), fsite, 'cp1251')
            savetofile(fly.converttoHTML(templbdc), fbdc, 'cp1251')
            savetofile(fly.timewindow().converttoHTML(templbdc), ftablo, 'cp1251')
            try:
                sendfilestoftp([ftablo], *internalftp)
            except TimeoutError:
                print('Timeout ftp connection', internalftp[0])
                os.remove(picklefile)
            else:
                print('Send to internal ftp')
            finally:
                os.remove(ftablo)
            try:
                sendfilestoftp([fbdc, fsite], *externalftp)
            except TimeoutError:
                print('Timeout ftp connection', externalftp[0])
                os.remove(picklefile)
            else:
                print('Send to external ftp')
            finally:
                os.remove(fbdc)
                os.remove(fsite)



