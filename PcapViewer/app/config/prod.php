<?php

// Doctrine (db)
$app['db.options'] = array(
		'driver'   => 'pdo_pgsql',
		'charset'  => 'utf8',
		'host'     => 'localhost',
		'port'     => '5432',
		'dbname'   => 'PcapViewer',
		'user'     => 'postgres',
		'password' => 'seenappse',
);