<!DOCTYPE html>
<html>

<head>
<meta charset="utf-8"/>
<title>gps tracker</title>
<meta name="description" content="">
<meta name="author" content="">

</head>
<body>
  <?php
    $lat = $_GET['lat'];
    echo ("<p><b>Breitengrad: $lat </b></p>");
    $long = $_GET['long'];
    echo ("<p><b>Längengrad: $long </b></p>");
	
	$gps_log = fopen("/var/www/html/gps.txt", "w");
	$coord = "$lat,$long";
	fwrite($gps_log, $coord);
	fclose($gps_log);
  ?>

</bod>
</html>
