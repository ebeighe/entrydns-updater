#!/usr/bin/python3
'''
entrydns-updater.py ~ ajclarkson.co.uk

Updater for Dynamic DNS on EntryDNS Domains
Performs an update for each given domain access token in
the hosts.json file.
'''
import json
from urllib.request import urlopen
import requests
import os
from time import strftime

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__)) +"/"

def get_cached_ip():
	'''
	Retrieve Cached IP From File, cuts down on API requests to EasyDNS if
	IP Address hasn't changed.

	Returns: 
		cached_ip: Cached IP or 0 to force refresh of public IP
	'''
	try:
		cached_file = open(SCRIPT_PATH + '.entrydns-cachedip', 'r')
		cached_ip = cached_file.read()
		cached_file.close()
		return cached_ip
	except IOError:
		return "0"

def set_cached_ip(ip):
	'''
	Stores IP Address in the Cached

	Args:
		ip: Address to be Cached
	'''
	try:
		cached_file = open(SCRIPT_PATH + '.entrydns-cachedip', 'w')
		cached_file.write(ip)
		cached_file.close()
	except IOError as e:
		print (e)

def get_ip():
	'''
	Retrieves public IP (from httpbin) with cached IP and returns import

	Returns:
		Public IP as a string
	'''
	public_ip = json.load(urlopen('http://httpbin.org/ip'))['origin']
	return public_ip

def load_hosts():
	'''
	Loads the hosts.json file containing access tokens for EasyDNS

	Returns: 
		A dictionary of hosts and access tokens, e.g 

		{'example-host':'678dxjvid928skf',
		 'example-host2':'8299fd0as88fd8d'}
	'''
	try:
		hosts_file = open(SCRIPT_PATH + 'hosts.json', 'r')
		hosts_data = json.load(hosts_file)
		return hosts_data
	except IOError as e:
		print (e)

def update_host(token, current_ip):
	'''
	Formulate and Execute an Update request on EntryDNS API for a given access token / IP

	Args:
		token: (string) Access Token for an EntryDNS Domain
		current_ip: (string) IP to point EasyDNS Domain to

	Returns: 
		Status (Either OK, or Error + Code)
	'''
	url = 'https://entrydns.net/records/modify/%s' % token
	payload = 'ip=%s' % current_ip
	response = requests.post(url, data=payload)
	if response.status_code == requests.codes.ok:
		return "OK"
	else:
		return "ERROR: Code %s" % response.status_code

current_ip = get_ip()
cached_ip = get_cached_ip()
if cached_ip != current_ip:
	set_cached_ip(current_ip)
	hosts = load_hosts()
	for host in hosts:
		result = update_host(hosts[host], current_ip)
		print ( "%s -- Updating %s: %s" % (strftime("%Y-%m-%d %H:%M:%S"),host, result) )
else:
	print ( "%s -- Public IP Matches Cache (%s), Nothing to Do..." % (strftime("%Y-%m-%d %H:%M:%S"), current_ip) )
