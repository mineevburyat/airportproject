<?php header("Content-Type: text/html;charset=windows-1251"); ?>
<br/>
<div id="online">
<table class="table">
<tr class="tr1">
<td width=80px><center>Рейс</center></td>
<th width=200px><center>Направление</center></th>
<td width=200px><center>Дата<br>по плану</center></td>
<td width=130px><center>Время<br>по плану</center></td>
<th width=110px><center>Статус</center></th>
</tr>
<!-- separator -->
<tr>
<td ><center><b>{FLY}</b></center></td>
<td ><center>{PORTDIST}</center></td>
<td ><center>{DPLAN}</center></td>
<td ><center><b>{TPLAN}</b></center></td>
<td ><center><font color=#090>{STATUS}</font></center></td>
<!-- separator -->
</tr>
 </table>
</div>
