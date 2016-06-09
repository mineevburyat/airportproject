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
    '''output lists element:'''
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

def convertTXTListToHTML(xmllist):
    HTMLstartstr='''
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <style>
        html { overflow:  hidden; }
        body { background:#1560bd;
            cursor: none;  }
        H15 { font-family: "Arial", Times, serif;
              font-size: 22px;
              color: #003399;
              font-weight:bold; }
        H14 { font-family: "Arial", Times, serif;
              font-size: 22px;
              color: white;
              font-weight:bold; }
        H16 { font-family: "Arial", Times, serif;
              font-size: 26px;
              color: #f7f21a;
              font-weight:bold;}
        tr:nth-child(2n+1) {
              background: #333;}
        td:nth-child(1) {
              background: #1560bd; }
    </style>
    </head>
    <body>
    <TABLE>'''
    for elem in xmllist:
        rowstr ='''<TR>
                <TD WIDTH=120 style='border-radius: 5px;'><h15>{0}</h15></TD>
                <TD WIDTH=310><h14>{1}</h14></TD>
                <TD WIDTH=90 ><h16>{2}</h16></TD>
                <TD WIDTH=170 ><h14>{3}</h14></TD>
                <TD WIDTH=170 ><h14>{4}</h14></TD>
                </TR>'''.format(elem[0], elem[10], elem[4], elem[9], '')
        HTMLstartstr += rowstr
    HTMLstartstr += '</TABLE></body></html>'
    return HTMLstartstr

def saveHTMLblock(HTMLstring, filename):
    f = open(filename,'w')
    f.write(HTMLstring)
    f.close()

reqarrivalsall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:1,3"
reqdeparturesall = "/pls/apex/f?p=1511:1:0:::NO:LAND,VID:0,3"
filenamearrive = r"/tmp/tmparrive.xml"
filenamedepart = r"/tmp/tmpdepart.xml"

requestandsave(reqarrivalsall, filenamearrive)
arrivals = parsexml(filenamearrive)
saveHTMLblock(convertTXTListToHTML(arrivals),'arrival.html')

requestandsave(reqdeparturesall, filenamedepart)
departures = parsexml(filenamedepart)
saveHTMLblock(convertTXTListToHTML(departures),'departure.html')

#print("Прилеты:")
#for arrival in arrivals:
#    print(arrival)
#print("Вылеты:")
#for depart in departures:
#    print(depart)
