# This program will generate the log files, parse the log files and store them on the mongoDB.

import sys

output_events_file = "events.log"
output_stats_file = "stats_json.log"

def generateAuditLog(unified_log_file_name):
	""" This function invokes the command nsconmsg to generate the events in LOG format"""
	system("./nsconmsg -K "+unified_log_file_name+" -d auditlog >"+output_events_file)

def generateStatsJSON(unified_log_file_name):
	""" This function invokes the command nsconmsg to generate the Stats in JSON format"""
	system("./nsconmsg -K "+unified_log_file_name+" -d auditlog >"+output_stats_file)



def parseAuditLogToJSON():
	""" Regex: (\d+\/\d+\/\d+:\d+:\d+:\d+)\s+(\S+)?\s+(\S+)?\s+(\S+)\s+(\S+)\s+:\s+([a-zA-Z0-9_ ]+)\s+([a-zA-Z0-9_ ]+)\s+(\d+)\s+(\d+)\s+:\s+(.+) """
	# Read the audit log file line by line into buffer, match the re with the current line
	
	match = re.search( r'(\d+\/\d+\/\d+:\d+:\d+:\d+)\s+(\S+)?\s+(\S+)?\s+(\S+)\s+(\S+)\s+:\s+([a-zA-Z0-9_ ]+)\s+([a-zA-Z0-9_ ]+)\s+(\d+)\s+(\d+)\s+:\s+(.+)', buff, re.M|re.I)
        if match == None:
		return None
