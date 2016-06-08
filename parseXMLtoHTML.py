from xml.etree.ElementTree import parse
from http.client import HTTPConnection
import time

def requestandsave(req, filename):
    '''запросить xml и сохранить в файл'''
    conector = HTTPConnection("93.157.148.58", 7777)
    conector.request("GET",req)
    result = conector.getresponse()
    file = open(filename, "w")
    file.write(result.read().decode("utf-8"))
    file.close()
    conector.close()

def parsexml(filename):
    '''Парсинг xml файла в текстовую структуру'''
    departure = []
    reiseInfo = []
    tree = parse(filename)
    for fly in tree.findall('FLY'):
        reiseInfo.append(fly.attrib['number'])
        portdist = ''
        distenetion = ''
        for ReiseElem in fly.getchildren():
            if ReiseElem.tag == 'AD':
                continue
            if ReiseElem.tag.find('PORTDIST') != -1:
                if ReiseElem.text is not None:
                    portdist = portdist + ReiseElem.text
                continue
            if ReiseElem.tag.find('PUNKTDIST') != -1:
                if ReiseElem.text is not None:
                    distenetion = distenetion + ReiseElem.text
                continue
            if ReiseElem.text is None:
                tmp = ''
            else:
                tmp = ReiseElem.text
            reiseInfo.append(tmp)
        reiseInfo.append(portdist)
        reiseInfo.append(distenetion)
        departure.append(reiseInfo)
        reiseInfo = []
    return departure

def convertTXTlist(xmllist):
    MINDOPUSK = 15 #minut
    ret = []
    newelem = []
    for elem in xmllist:
        newelem.append(elem[0])
        newelem.append(elem[1])
        newelem.append(elem[2])
        newelem.append(time.mktime(time.strptime(elem[3] + ' ' + elem[4], '%d.%m.%Y %H:%M')))
        newelem.append(time.mktime(time.strptime(elem[5] + ' ' + elem[6], '%d.%m.%Y %H:%M')))
        if elem[7] == '' and elem[8] == '':
            newelem.append(None)
        else:
            newelem.append(time.mktime(time.strptime(elem[7] + ' ' + elem[8], '%d.%m.%Y %H:%M')))
        newelem.append(elem[9])
        newelem.append(elem[10])
        newelem.append(elem[11])
        ret.append(newelem)
        newelem = []
    return ret

reqdepart = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:1,0"
reqarrive = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:0,0"
filenamearrive = r"/tmp/tmparrive.xml"
filenamedepart = r"/tmp/tmpdepart.xml"
requestandsave(reqarrive, filenamearrive)
arrives = parsexml(filenamearrive)
requestandsave(reqdepart, filenamedepart)
departs = parsexml(filenamedepart)
