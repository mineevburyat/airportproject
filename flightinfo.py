from xml.etree.ElementTree import parse
from http.client import HTTPConnection
import time

class TxtFlightInfo(list):
    '''Info about air flight. Structure: [
                                            {'FLY': '  ', #код авиакомпании и номер рейса
                                             'AIRCRAFT': '  ' #тип воздушного судна,
                                             'PUNKTDIST': '  ', #пункты назначения
                                             'PORTDIST': '   ', #аэропорты назначения
                                             'CARRNAME': '   ', #название перевозчика
                                             'TPLAN': '   ', #время по плану
                                             'DPLAN': '   ', #дата по плану
                                             'TEXP': '', # время расчетное (когда вылетел с аэропорта отправления - ?)
                                             'DEXP': '', # дата расчетное
                                             'TFACT': '', # время фактическое
                                             'DFACT': '', # дата фактическое
                                             'STATUS': '', # статус рейса
                                             'TIMEFACT': '', # время UNIX фактическое
                                             'TIMEPLAN': '  ', # время UNIX по плану
                                             'TIMEEXP': ''}, # время UNIX расчетное
                                             {...}, ...
                                        ]
    '''
    def __init__(self, server, port, request):
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
                if ReiseElem.tag == 'AD':
                    continue
                if ReiseElem.tag.find('PORTDIST') != -1:
                    if ReiseElem.text is not None:
                        airportdist = airportdist + ReiseElem.text
                    continue
                if ReiseElem.tag.find('PUNKTDIST') != -1:
                    if ReiseElem.text is not None:
                        distinetion = distinetion + ReiseElem.text
                    continue
                reiseInfo.setdefault(ReiseElem.tag, ReiseElem.text)
            reiseInfo['PORTDIST'] = airportdist
            reiseInfo['PUNKDIST'] = distinetion
            reiseInfo['TIMEPLAN'] = time.mktime(time.strptime(reiseInfo['DPLAN'] + ' ' + reiseInfo['TPLAN'], '%d.%m.%Y %H:%M'))
            if reiseInfo['TEXP'] == '' or reiseInfo['DEXP'] == '':
                reiseInfo['TIMEEXP'] = None
            else:
                reiseInfo['TIMEEXP'] = time.mktime(time.strptime(reiseInfo['DEXP'] + ' ' + reiseInfo['TEXP'], '%d.%m.%Y %H:%M'))
            if reiseInfo['TFACT'] == '' or reiseInfo['DFACT'] == '':
                reiseInfo['TIMEFACT'] = None
            else:
                reiseInfo['TIMEFACT'] = time.mktime(time.strptime(reiseInfo['DFACT'] + ' ' + reiseInfo['TFACT'], '%d.%m.%Y %H:%M'))
            self.append(reiseInfo)
            reiseInfo = {}

    def __str__(self):
        st = ''
        for elem in self:
            st += elem + '/n'
        return st

    def converttoHTML(self, template, namepage=None):
        '''get and dileved template and return string in HTML. Where template is name of file. Template is frie parts: start
        , body whith data and end'''
        partlines = ''
        parts = []
        fdiscript = open(template, 'r')
        for line in fdiscript:
            if line.find('<:separator:/>') == -1:
                partlines += line
            else:
                parts.append(partlines)
                partlines = ''
        if len(parts) != 3:
            print('Error')
        if namepage:
            parts[0] = parts[0].format(Title=namepage)
        st = ''
        for flight in self:
            st += parts[1].format(flight)
        parts[1] = st
        st = ''.join(parts)
        return st


#class BinFlightInfo(list):
#    '''Structure:'''
#    def __init__(self, textflightinfo):
#        info = {}
#        for flight in textflightinfo:
#            info['TIMEPLAN'] = time.mktime(time.strptime(flight['DPLAN'] + ' ' + flight['TPLAN'], '%d.%m.%Y %H:%M'))
#            info['TIMEEXP'] = time.mktime(time.strptime(flight['DEXP'] + ' ' + flight['TEXP'], '%d.%m.%Y %H:%M'))
#            info['TIMEFACT'] = time.mktime(time.strptime(flight['DFACT'] + ' ' + flight['TFACT'], '%d.%m.%Y %H:%M'))
#            for key in flight:
#                if not key.startswith('T') or not key.startswith('D'):
#                    info[key] = flight[key]
#            self.append(info)
#            info = {}

if __name__ == 'main':
    reqarrivalsall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:1,3"
    reqdeparturesall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:0,3"
    arrivels = TxtFlightInfo("93.157.148.58", 7777, reqarrivalsall)
    depatures = TxtFlightInfo("93.157.148.58", 7777, reqdeparturesall)
    print(arrivels)
    print(depatures)