from xml.etree.ElementTree import parse
from http.client import HTTPConnection

class TxtFlightInfo(list):
    '''Info about air flight. Structure: [
                                            {'FLY': '  ',
                                             'AIRCRAFT': '  ',
                                             'PUNKTDIST': '  ',
                                             'PORTDIST': '   ',
                                             'CARRNAME': '   ',
                                             'TPLAN': '   ',
                                             'DPLAN': '   ',
                                             'TEXP': '',
                                             'DEXP': '',
                                             'TFACT': '',
                                             'DFACT': '',
                                             'STATUS': ''},
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
                #if ReiseElem.text is None:
                #    tmp = ''
                #else:
                reiseInfo.setdefault(ReiseElem.tag, ReiseElem.text)
                #reiseInfo.append(tmp)
            reiseInfo['PORTDIST'] = airportdist
            reiseInfo['PUNKDIST'] = distinetion
            #print(reiseInfo)
            self.append(reiseInfo)
            reiseInfo = {}

    #def __str__(self):
    #    for elem in self:
    #        return str(elem) + '/n'

reqarrivalsall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:1,3"
reqdeparturesall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:0,3"
arrivels = TxtFlightInfo("93.157.148.58", 7777, reqarrivalsall)
depatures = TxtFlightInfo("93.157.148.58", 7777, reqdeparturesall)
print(arrivels)
print(depatures)