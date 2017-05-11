<?php


$DB_NAME = "clryd";
$DB_HOST = "localhost";
$DB_USER = "clryd";
$DB_PASS = "0347";

$db = new mysqli($DB_HOST, $DB_USER, $DB_PASS, $DB_NAME);

$groupid = intval($db->real_escape_string($_GET['groupid']));
$messagetype = intval($db->real_escape_string($_GET['messagetype']));

if (mysqli_connect_errno()) {
  printf("Connect failed: %s\n", mysqli_connect_error());
  exit();
 }


$sql = "SELECT ts,groupid,message FROM messages WHERE messagetype = '".$messagetype."'";
//$sql = "SELECT ts,groupid,message FROM messages WHERE messagetype = '1'";
//echo $sql."<br/>";
if($result = $db->query($sql)){
  while($row = $result->fetch_row()) {
    echo $row[0].";".$row[1].";".$row[2]."\n";
  }
}else{
  echo "FAIL";
}

