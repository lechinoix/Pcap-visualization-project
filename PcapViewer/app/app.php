<?php
// /app/app.php
require_once __DIR__.'/bootstrap.php';

use Symfony\Component\HttpFoundation\Response;

$app = new Silex\Application();

$app->get('/', function() {
	return new Response('Welcome to my new Silex app');
});

$app->run();
