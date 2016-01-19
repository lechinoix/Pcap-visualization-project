<?php

namespace PcapViewer\Pcap;

class Session
{
    /**
     * Session id.
     *
     * @var integer
     */
    private $id;

    /**
     * Sessions protocole.
     *
     * @var string
     */
    private $protocole;

    /**
     * Sessions portSrc.
     *
     * @var string
     */
    private $portSrc;
    
    /**
    * Sessions portDest.
    *
    * @var string
    */    
    private $portDest;

    /**
    * Sessions IpSrc.
    *
    * @var string
    */
    private $ipSrc;
    
    /**
    * Sessions portDest.
    *
    * @var string    
    */    
    private $portDest;
        

    public function getId() {
        return $this->id;
    }

    public function setId($id) {
        $this->id = $id;
    }

    public function getProtocole() {
        return $this->protocole;
    }

    public function setProtocole($protocole) {
        $this->protocole = $protocole;
    }

    public function getPortSrc() {
        return $this->portSrc;
    }

    public function setPortSrc($portSrc) {
        $this->portSrc = $portSrc;
    }
    public function getPortDest() {
    	return $this->portDest;
    }
    
    public function setPortDest($portDest) {
    	$this->portSrc = $portDest;
    }
    public function getIpSrc() {
    	return $this->ipSrc;
    }
    
    public function setIpSrc($ipSrc) {
    	$this->portSrc = $ipSrc;
    }
    public function getIpDest() {
    	return $this->ipDest;
    }
    
    public function setIpDest($ipDest) {
    	$this->portSrc = $ipDest;
    }
}