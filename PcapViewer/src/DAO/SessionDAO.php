<?php
namespace PcapViewer\DAO;

use Doctrine\DBAL\Connection;
use PcapViewer\Pcap\Session;

class SessionDAO
{
	
	/**
	* Database connection
	*
	* @var \Doctrine\DBAL\Connection
	*/
	private $db;

	
	/**
	* Constructor
	*
	* @param \Doctrine\DBAL\Connection The database connection object
	*/
	public function __construct(Connection $db) {
		$this->db = $db;
	}

	
	/**
	* Return a list of all articles, sorted by date (most recent first).
	*
	* @return array A list of all articles.
	*/
	public function findAll() {
		$sql = "select * from session order by id desc";
		$result = $this->db->fetchAll($sql);

		// Convert query result to an array of domain objects
		$sessions = array();
		foreach ($result as $row) {
			$sessionId = $row['id'];
			$sessions[$sessionId] = $this->buildSession($row);
		}
		return $sessions;
	}

	/**
	* Creates a Session object based on a DB row.
	*
	* @param array $row The DB row containing Session data.
	* @return \PcapViewer\Pcap\Session
	*/
	private function buildSession(array $row) {
		$session = new Session();
		$session->setId($row['id']);
		$session->setProtocole($row['protocole']);
		$session->setPortSrc($row['portSrc']);
		$session->setPortDest($row['portDest']);
		$session->setIpSrc($row['ipSrc']);
		$session->setIpDest($row['ipDest']);
		return $session;
	}
}