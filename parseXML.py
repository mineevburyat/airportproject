'''Parse XML flyte plane'''
from xml.etree.ElementTree import parse

#get xml file

#parse and store
departure = {}
tree = parse('/home/mineev/test.xml')
for fly in tree.findall('FLY'):
    reise = fly.attrib['number']
    for ReiseElem in fly.getchildren():
        if ReiseElem.tag == 'AIRCRAFT':
            aircraft = ReiseElem.text
        if ReiseElem.tag == 'PORTDIST':
            portdist = ReiseElem.text
        if ReiseElem.tag == 'PUNKTDIST':
            disten = ReiseElem.text
        if ReiseElem.tag == 'CARRNAME':
            aviacomp = ReiseElem.text
        if ReiseElem.tag == 'DPLAN':
            dataPlan = ReiseElem.text
        if ReiseElem.tag == 'TPLAN':
            timePlan = ReiseElem.text
        if ReiseElem.tag == 'DFACT':
            dataFact = ReiseElem.text
        if ReiseElem.tag == 'TFACT':
            timeFact = ReiseElem.text
        if ReiseElem.tag == 'DEXP':
            dataExp = ReiseElem.text
        if ReiseElem.tag == 'TEXP':
            timeExp = ReiseElem.text
        if ReiseElem.tag == 'STATUS':
            status = ReiseElem.text
    departure[reise] = [aviacomp, aircraft, portdist, disten, dataPlan,
                        timePlan, dataExp, timeExp, dataFact, timeFact,status]

for reis in departure.keys():
    print(reis + ': ',end=' ')
    for elem in departure[reis]:
        if elem is None:
            elem = ''
        print(elem + ', ', end=' ')
    print()
