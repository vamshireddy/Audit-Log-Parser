# This program will generate the log files, parse the log files and store them on the mongoDB.

import os
import time
import re
import json
import pymongo
from pymongo import MongoClient
import socket
import struct

# Log files
output_events_file = "events.log"
output_stats_file = "stats.log"
unified_log_file_name = "newnslog.ppe.0"

# To keep track of the content in the log files
offset1 = 0
offset2 = 0

# MongoDB Variables
db_name = "auditlog-db"
audit_col_name = "aud_col"
monitors_col_name = "mon_col"
servers_col_name = "ser_col"
services_col_name = "svc_col"
vservers_col_name = "vser_col"

def generateAuditLog():
	""" This function invokes the command nsconmsg to generate the events in LOG format"""
	os.system("./nsconmsg -K "+unified_log_file_name+" -d auditlog 1>"+output_events_file)

def generateStatsJSON():
	""" This function invokes the command nsconmsg to generate the Stats in JSON format"""
	os.system("./nsconmsg -K "+unified_log_file_name+" -d jsondata 1>"+output_stats_file)


def extractFromJSONObj(old_json_obj, entries):
	new_json_obj = {}
	for i in entries:
		try:
			if i in ["vsvr_IPAddr", "si_public_ip"]:
				print old_json_obj[i]
				# Convert the IP long into string
				ip_str = socket.inet_ntoa(struct.pack("<I", long(old_json_obj[i])))
				new_json_obj[i] = ip_str
				print ip_str
			else:
				new_json_obj[i] = old_json_obj[i]
		except Exception:
			continue
	return new_json_obj

def parsePerfStatsJSON(services_col, servers_col, vservers_col, monitors_col):
	""" This function will parse the performance stats log in JSON for services, servers, vservers, monitors and inserts them to respe		ctive collections 
		in mongo DB
	"""
	# Read the stats log.
	file_obj = open(output_stats_file, "r")
	global offset2
	if file_obj == None :
		print "File can't be opened"
		sys.exit(243)
	file_obj.seek(offset2, 0)
	while True:
		line = file_obj.readline()
		if line == "" :
			print "Done"
			offset2 = file_obj.tell()
			break
		try:
			j = json.loads(line)
		except Exception:
			print "Not a valid JSON"
			continue
		devname = j["devname"]
		col_name = None
		json_obj = None
		if devname.find("_vserver_") != -1 :
			# Its Vserver. Store it in vservers collection
			json_obj = extractFromJSONObj(j, ["vsvr_IPAddr", "vsvr_Port", "vsvr_Protocol", "vsvr_Type"])
			col_name = vservers_col

		elif devname.find("_svc_") != -1 :
			# Its service. Store it in services collection
			json_obj = extractFromJSONObj(j,["si_cur_state", "si_cur_transport", "si_cur_servicetype", "si_public_ip", "si_public_port"])
			col_name = services_col

		elif devname.find("_vip_") != -1 :
			# Its server, Store it in servers collections
			json_obj = extractFromJSONObj(j, ["si_cur_state","si_cur_efct_state","si_cur_transport", "si_cur_servicetype"])
			col_name = servers_col

		elif devname.find("Monitor") != -1:
			# Its monitors, store it in monitors.
			json_obj = extractFromJSONObj(j,['type'])
			col_name = monitors_col
		else:
			continue

		json_obj["devname"] =  j['devname']
		json_obj["timestamp"] = j['timestamp']
		# Insert the formed JSON
		insertToDB(json_obj,col_name)
		time.sleep(0.1)
	file_obj.close()
	print "Completed parsing the perf log file"

def parseAuditLogToJSON(col):
	""" 
	Regex:(\d+\/\d+\/\d+:\d+:\d+:\d+)\s+(\S+)?\s+(\S+)?\s+(\S+)\s+(\S+)\s+:\s+([a-zA-Z0-9_ ]+)\s+([a-zA-Z0-9_ ]+)\s+(\d+)\s+(\d+)\s+:\s+(.+) 	"""
	# Read the audit log file line by line into buffer, match the re with the current line
	file_obj = open(output_events_file, "r")
	global offset1
	if file_obj == None :
		print "File can't be opened"
		sys.exit(243)
	file_obj.seek(offset1, 0)
	while True:
		line = file_obj.readline()
		print line
		if line == "" :
			print "Done"
			offset1 = file_obj.tell()
			break
		time.sleep(0.1)
		match = re.search( r'(\d+\/\d+\/\d+:\d+:\d+:\d+)\s+(\S+)?\s+(\S+)?\s+(\S+)\s+(\S+)\s+:\s+([a-zA-Z0-9_ ]+)\s+([a-zA-Z0-9_ ]+)\s+(\d+)\s+(\d+)\s+:\s+(.+)', line, re.M|re.I)
		if match == None:
			print "Not matched"
		else:
			print "Matched!"
			data = {}
			data['time'] = match.group(1)
			data['time_std'] = match.group(2)
			data['log_format'] = match.group(3)
			data['type'] = match.group(4)
			data['ppe'] = match.group(5)
			data['event_type'] = match.group(6)
			data['event_subtype'] = match.group(7)
			data['event_no'] = match.group(8)
			data['event_subno'] = match.group(9)
			data['desc'] = match.group(10)
			print data
			insertToDB(data,col)
			print "\n"
	file_obj.close()
	print "Completed the parsing of audit log file"

def insertToDB(json, col):
	""" Insert the json into database """
	col.insert_one(json)

# Setup pymongo
client = MongoClient()
db = client[db_name]
audit_col_obj = db[audit_col_name]
vservers_col_obj = db[vservers_col_name]
services_col_obj = db[services_col_name]
servers_col_obj = db[servers_col_name]
monitors_col_obj = db[monitors_col_name]


while True:
	# Create log files
	generateAuditLog()
	generateStatsJSON()
	# Parse the log files
	parseAuditLogToJSON(audit_col_obj)
	parsePerfStatsJSON(services_col_obj, servers_col_obj, vservers_col_obj, monitors_col_obj)
	print "Sleeping for 1 min"
	time.sleep(60)
