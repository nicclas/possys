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

  echo "<h1>All stored messages</h1>";
  echo "Note: All messages are cleared every day at midnight.<br/>";
  echo "<a href=\"clear_messtable.php\">Click here</a> to clear all messages of all types now! Warning, all messages for all groups will be cleared immediately!<br/><br/>";

echo "Current messages, for all groups and all types are:<br>";
$sql = "SELECT ts,groupid,messagetype,message FROM messages";
echo "<table><tr><th>Date</th><th>Group ID</th><th>Message type</th><th>Message</th></tr>";
if($result = $db->query($sql)){
  while($row = $result->fetch_row()) {
    echo "<tr>";
    echo "<td>".$row[0]."</td><td>".$row[1]."</td><td>".$row[2]."</td><td>".$row[3]."</td>\n";
    echo "<tr>";
  }
  echo "</table>";
}else{
  echo "FAIL";
}

