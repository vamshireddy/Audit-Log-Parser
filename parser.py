# This program will generate the log files, parse the log files and store them on the mongoDB.

import os
import time
import re
import json
import pymongo
from pymongo import MongoClient

output_events_file = "events.log"
output_stats_file = "stats_json.log"
unified_log_file_name = "newnslog.ppe.0"
offset = 0
db_name = "auditlog-db"
col_name = "col"

def generateAuditLog():
	""" This function invokes the command nsconmsg to generate the events in LOG format"""
	os.system("./nsconmsg -K "+unified_log_file_name+" -d auditlog >"+output_events_file)

def generateStatsJSON():
	""" This function invokes the command nsconmsg to generate the Stats in JSON format"""
	os.system("./nsconmsg -K "+unified_log_file_name+" -d auditlog >"+output_stats_file)

def parseAuditLogToJSON(col):
	""" 
	Regex:(\d+\/\d+\/\d+:\d+:\d+:\d+)\s+(\S+)?\s+(\S+)?\s+(\S+)\s+(\S+)\s+:\s+([a-zA-Z0-9_ ]+)\s+([a-zA-Z0-9_ ]+)\s+(\d+)\s+(\d+)\s+:\s+(.+) 	"""
	# Read the audit log file line by line into buffer, match the re with the current line
	file_obj = open(output_events_file, "r")
	global offset
	if file_obj == None :
		print "File can't be opened"
		sys.exit(243)
	file_obj.seek(offset, 0)
	while True:
		line = file_obj.readline()
		print line
		if line == "" :
			print "Done"
			offset = file_obj.tell()
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


def insertToDB(json, col):
	""" Insert the json into database """
	col.insert_one(json)

# Setup pymongo
client = MongoClient()
db = client[db_name]
collection = db[col_name]

while True:
	# Create log files
	generateAuditLog()
	# generateStatsJSON()
	# Parse the log files
	parseAuditLogToJSON(collection)
	time.sleep(60)
