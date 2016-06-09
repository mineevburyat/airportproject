# airportproject
request the daily plan:
http://<server >:<port>/pls/apex/f?p=1515:1:0:::NO:LAND,VID:<landing_set>,<reys_vid>
where landing_set : 0 - get departures and 1 - get arrivels
reys_vid - 0 - regular flights, 1 - charter flights, 2 - other flights, 3 - all flights
get xml file from apix:
<?xml version="1.0" encoding="UTF-8"?>
<REPORT type="SPP">
	<FLY number="ЮТ2201">
		<AD>0</AD>
		<PORTDIST>Тюмень</PORTDIST>
		<PORTDIST2>Москва(Внуково)</PORTDIST2>
		<PORTDIST3/>
		<CARRNAME>ЮТэйр</CARRNAME>
		<DPLAN>22.01.2013</DPLAN>
		<TPLAN>10:00</TPLAN>
		<DEXP>22.02.2013</DEXP>
		<TEXP>12:55</TEXP>
		<DFACT/>
		<TFACT/>
		<STATUS>Вылет задержан по метеоусловиям Тюмени</STATUS>
	</FLY>
</REPORT>
request for get season schedule:
http://<server>:<port>/pls/apex/f?p=1516:1:0:::NO:LAND,DATE,VID:{direction, 0 - out airport (departure), 1 - in airport(arrival},
{from data visualised in format ddmmyyyy},{vid} where vid 0-regular flights, 1-charter flights, 2-other flights, 3-all flights.
get xml file from apix:
<?xml version="1.0" encoding="UTF-8"?>
<FLY number="N4-8817"> #code and flight number
    <AD>0</AD> #1 arrival 0 departure
    <AIRCRAFT>Б-737</AIRCRAFT> #type of aircraft
    <PORTDIST>ХУРГАДА</PORTDIST> #name of airport
    <PUNKTDIST>Хургада</PUNKTDIST> #name of punkt distanation
    <PORTTRANS></PORTTRANS> #транзитный аэропорт
    <PUNKTTRANS></PUNKTTRANS> #
    <CARRNAME>ЮТэйр</CARRNAME> 
    <DS>21.03.2015</DS> #Дата начала навигации
    <DE>21.03.2015</DE> #Дата окончания навигации
    <WEEK>1234567</WEEK> #Частота
    <TW>23:05</TW>
    <TP>03:05</TP>
</FLY>
<SUT>+1</SUT>
</REPORT>
