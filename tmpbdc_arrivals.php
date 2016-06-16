<?php header("Content-Type: text/html;charset=windows-1251"); ?>
<html>
<head>
<style>
   html { overflow:  hidden; }
     body {
	background:#1560bd;
	cursor: none;
   }
    H15 {
    font-family: "Arial", Times, serif; /* Ãàðíèòóðà òåêñòà */
    font-size: 22px; /* Ðàçìåð øðèôòà â ïðîöåíòàõ */
	color: #003399;
	font-weight:bold
   }
    H14 {
    font-family: "Arial", Times, serif; /* Ãàðíèòóðà òåêñòà */
    font-size: 22px; /* Ðàçìåð øðèôòà â ïðîöåíòàõ */
	color: white;
	font-weight:bold
   }
    H16 {
    font-family: "Arial", Times, serif; /* Ãàðíèòóðà òåêñòà */
    font-size: 26px; /* Ðàçìåð øðèôòà â ïðîöåíòàõ */
	color: #f7f21a;
	font-weight:bold
   }
   tr:nth-child(2n+1) {
    background: #333;
   }
   td:nth-child(1) {
    background: #1560bd;
   }
  </style>
 </head>
<body >

<TABLE>
<!-- separator -->
    <TR>
      <TD WIDTH=120 ><h14><center><img src='logo/1.jpg' width='100px' height='45px' style='border-radius: 5px;'></center></h14></TD>
      <TD WIDTH=120 BGCOLOR='#f7f21a' style='border-radius: 5px;'><h15><center>{FLY}</center></h15></TD>
      <TD WIDTH=310><h14><center>{PORTDIST}</center></h14></TD>
	  <TD WIDTH=90 ><h16><center>{TPLAN}</center></h16></TD>
	  <TD WIDTH=240 ><h14><center>{STATUS}</center></h14></TD>
	</TR>
<!-- separator -->
</TABLE>
</body>
</html>

