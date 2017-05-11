<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

$DB_NAME = "clryd";
$DB_HOST = "localhost";
$DB_USER = "clryd";
$DB_PASS = "0347";

$db = new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);

$groupid = intval($db->real_escape_string($_GET['groupid']));
$messagetype = intval($db->real_escape_string($_GET['messagetype']));
$message = $db->real_escape_string($_GET['message']);

if (mysqli_connect_errno()) {
  printf("Connect failed: %s\n", mysqli_connect_error());
  exit();
}

$sql = "INSERT INTO messages (groupid, messagetype, message) VALUES (".$groupid.",".$messagetype.",'".$message."') ON DUPLICATE KEY UPDATE message = '".$message."', ts = now()";

//echo $sql."<br>";

if($result = $db->query($sql)){
  echo "OK";
}else{
  echo "FAIL";
}

?>