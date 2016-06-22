# -*- coding: utf-8 -*-
import sys
from xml.etree.ElementTree import parse
import datetime as DT
from ftplib import FTP
import pickle
if int(sys.version_info[0]) == 3:
    from http.client import HTTPConnection
else:
    raise Exception("Version python less then 3")

class FlightsInfo(dict):
    '''Structure: {'FLY': {STATUSCHECKIN: , STATUSBOARD: , STATUSBAG,
                            CHECKIN: '', GATE: '', BAGGAGE: '' '''
    def __init__(self):
        self = {}

    def updatefromflightes(self, flights):
        flynewinfo = {'STATCHECKIN': False, 'STATBOARD': False, 'STATBAGG': False,
                  'CHECKINS': '', 'GATE': '', 'BAGGAGE': ''}
        for flight in flights:
            fly = flight['FLY']
            if fly in self:
                continue
            else:
                self.setdefault(fly, flynewinfo)
        currentflylst = []
        for flight in flights:
            currentflylst.append(flight['FLY'])
        for fly in self:
            if fly not in currentflylst:
                self.pop(fly)

    def __str__(self):
        st = ''
        for flightinfo in self:
            st += str(flightinfo) + ': ' + str(self[flightinfo]) + '\n'
        return st

    def save(self, filename):
        f = open(filename, 'wb')
        pickle.dump(self, f)

    def load(self, filename):
        try:
            f = open(filename, 'rb')
        except FileNotFoundError:
            return False
        self = pickle.load(f)
        return True

    def getflightstatus(self, fly, param):
        '''param mast be STATCHECIN, STATBAGG, STATBOARD, GATE, CHECKINS, BAGGAGE'''
        params = ['STATCHECKIN', 'STATBOARD', 'STATBAGG', 'CHECKINS', 'GATE', 'BAGGAGE']
        if param not in params:
            raise Exception('Parametr not in permissions list')
        if fly in self:
            return self[fly][param]
        else:
            return None

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
            flightinfo['FLY'] = fly.attrib['number']
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

    def handlenullstatus(self, flightsinfo):
        HOUR2 = DT.timedelta(seconds=7200)
        MIN40 = DT.timedelta(seconds=2400)
        MIN20 = DT.timedelta(seconds=1200)
        DEPARTPLAN = 'Вылет по плану'
        DEPARTTIMEEXP = 'Вылет по расч. времени '
        STARTCHEKIN = 'Начинается регистрация пассажиров и багажа'
        CHECKIN = 'Регистрация. Стойки: '
        BETWEENCHECKBOARD = 'Регистрация закончена. Загрузка багажа'
        BOARDING = 'Посадка пассажиров'
        UPDATETIMEDEPART = 'Уточнение времени вылета'
        ARRIVEPLAN = 'Прилет ожидается по плану'
        ARRIVEEXP = 'Прилет по расч. времени '
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
                        if now < timeexp - HOUR2 \
                                and not flightsinfo.getflightstatus(fly, 'STATCHECKIN'):
                            flight['STATUS'] = DEPARTTIMEEXP + flight['TEXP']
                        elif now < timeexp - HOUR2 \
                                and flightsinfo.getflightstatus(fly, 'STATCHECKIN'):
                            flight['STATUS'] = CHECKIN + flightsinfo.getflightstatus(fly, 'CHECKIN')
                        elif timeexp - HOUR2 <= now <= timeexp - MIN40 \
                                and not flightsinfo.getflightstatus(fly, 'STATCHECKIN'):
                            flight['STATUS'] = STARTCHEKIN
                        elif timeexp - HOUR2 <= now <= timeexp - MIN40 \
                                and flightsinfo.getflightstatus(fly, 'STATCHECKIN'):
                            flight['STATUS'] = CHECKIN + flightsinfo.getflightstatus(fly, 'CHECKIN')
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
    '''arrivalxmlreqreg = ('93.157.148.58', 7777, '/pls/apex/f?p=1511:1:0:::NO:LAND,VID:0,0')
    arrivalxmlfile = 'arrivals.xml'
    getxmlfromserver(arrivalxmlfile, *arrivalxmlreqreg)
    arrivals = Flights()
    arrivals.getfromxml(arrivalxmlfile)

    flightsinfo = FlightsInfo()
    flightsinfo.updatefromflightes(arrivals)
    arrivals.handlenullstatus(flightsinfo)
    if arrivals.isdifferent('arrivals.pkl'):
        savetofile(arrivals.converttoHTML('templatebdc.php'), 'test.php')
    print(flightsinfo)
    flightsinfo.save('arrivalsinfo.pkl')
    flightsinfo.load('arrivalsinfo.pkl')
    #for flightinfo in flightsinfo:
    print(arrivals)
    '''
    xmlfile = 'xmldata.xml'
    arrivals = Flights()
    arrivalxmlreqreg = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,0")
    arrivalxmlreqchart = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:1,1")
    getxmlfromserver(xmlfile, *arrivalxmlreqreg)
    arrivals.getfromxml(xmlfile)
    getxmlfromserver(xmlfile, *arrivalxmlreqchart)
    arrivals.getfromxml(xmlfile)
    departures = Flights()
    departxmlreqreg = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,0")
    departxmlreqchart = ('172.17.10.2', 7777, "/pls/apex/f?p=1515:1:0:::NO:LAND,VID:0,1")
    getxmlfromserver(xmlfile, *departxmlreqreg)
    departures.getfromxml(xmlfile)
    getxmlfromserver(xmlfile, *departxmlreqchart)
    departures.getfromxml(xmlfile)
    departures.sort(key=getflighttime)
    arrivals.sort(key=getflighttime)

    departinfo = FlightsInfo()
    arrivalinfo = FlightsInfo()
    departinfo.updatefromflightes(departures)
    arrivalinfo.updatefromflightes(arrivals)
    departures.handlenullstatus(departinfo)
    arrivals.handlenullstatus(arrivalinfo)
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
    now = DT.datetime.now().time()
    MIDNIGHT = DT.time(0, 0, 0)
    MIDNIGHT5MIN = DT.time(0, 5, 0)
    if departures.isdifferent(departurepicklefile) or (MIDNIGHT < now <= MIDNIGHT5MIN):
        departures.save(departurepicklefile)
        savetofile(departures.today().converttoHTML(templdeparttablo), fsitedepart, 'cp1251')
        savetofile(departures.converttoHTML(templbdc), fbdcdepart, 'cp1251')
        savetofile(departures.today().converttoHTML(templbdc), ftablodepart, 'cp1251')
        sendfilestoftp([ftablodepart], *internalftp)
        sendfilestoftp([fbdcdepart, fsitedepart], *externalftp)
        print('Send departure')
    else:
        print('No diff on departure')
    if arrivals.isdifferent(arrivalspicklefile) or (MIDNIGHT < now <= MIDNIGHT5MIN):
        arrivals.save(arrivalspicklefile)
        savetofile(arrivals.today().converttoHTML(templarrivaltablo), fsitearrive, 'cp1251')
        savetofile(arrivals.converttoHTML(templbdc), fbdcarrive, 'cp1251')
        savetofile(arrivals.today().converttoHTML(templbdc),ftabloarrive, 'cp1251')
        sendfilestoftp([ftabloarrive], *internalftp)
        sendfilestoftp([fsitearrive, fbdcarrive], *externalftp)
        print('Send arrivals')
    else:
        print('No diff on arrivals')

