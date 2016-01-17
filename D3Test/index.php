<!DOCTYPE html>
<meta charset="utf-8">
<style>
	a{
		margin:10px 0px;
	}
</style>

<?php
	if(!isset($_GET["graph"])){
		include("home.php");

	}elseif($_GET["graph"] == "parallel"){
		include("graphs/parallel.php");

	}elseif($_GET["graph"] == "network"){
		include("graphs/network.php");

	}else{
		include("404.php");

	}
?>