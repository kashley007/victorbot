from slackclient import SlackClient
from globalconsts import *
import requests
import json
import time
import datetime as dt

""" 
	This module creates connections to both the Slack and VictorOps(vo) APIs.
	The API call to GET a team's on call schedule and build a proper SlackBot
	response are also handled here
"""

def slack_connect(slack_token):
	connection = SlackClient(slack_token)
	return connection


def json_timestamp_format(item):
	return str(item).split('T')[0], str(item).split('T')[1]


def determine_shift(team_member, time_start, time_end):
	
	if (int(time_start[:2]) == int(OPS_DAY_START) and int(time_end[:2]) == int(OPS_DAY_END) ):
		return { team_member: str(OPS_DAY_START) + 'am - ' + str(OPS_DAY_END - 12) + 'pm' }
	elif(int(time_start[:2]) == int(OPS_NIGHT_START) and int(time_end[:2]) == int(OPS_NIGHT_END) ):
		return { team_member: str(OPS_NIGHT_START - 12) + 'pm - ' + str(OPS_NIGHT_END) + 'am' }
	elif(int(time_start[:2]) == int(DEV_DAY_START) and int(time_end[:2]) == int(DEV_DAY_END) ):
		return { team_member: str(DEV_DAY_START) + 'am - ' + str(DEV_DAY_END - 12) + 'pm' }
	elif(int(time_start[:2]) == int(DEV_NIGHT_START) and int(time_end[:2]) == int(DEV_NIGHT_END) ):
		return { team_member: str(DEV_NIGHT_START) + 'am - ' + str(DEV_NIGHT_END) + 'am' }
	else:
		return 'No one is on call'


def vo_get_oncall_schedule(api_id, api_key, team):
	"""Make a VictorOps API GET call to retrieve the on call schedule for a team"""
	url = 'https://api.victorops.com/api-public/v1/team/'+ team + '/oncall/schedule'
	params = {'daysForward': '1'}
	headers = { 'X-VO-Api-Id': api_id,
				'X-VO-Api-Key': api_key}
	request = requests.get(url, params=params, headers=headers)

	if request.status_code == 200:
		json_ops = request.json()
		if team == 'Ops':
			contents = json.dumps(json_ops, sort_keys=True, indent=4, separators=(',', ': '))
			file = open('schedule', 'w')
			file.write(contents)
			file.close()
	else:
		print("Could not connect to VO -- Status code: " + str(request.status_code))
		json_ops = ""
	return json_ops


def vo_build_oncall_response(json_data):
	"""Parse the json response from VictorOps API for a team's
		on call schedule and build a proper slack response string for VictorBot
	"""
	oncall = {}
	response = ""
	date_now = time.strftime("%Y-%m-%d")
	time_now = dt.datetime.now().hour

	for item in json_data["schedule"]:
		for roll in item["rolls"]:
			date_start, time_start = json_timestamp_format(roll['change'])
			date_end, time_end = json_timestamp_format(roll['until'])	
			if ((date_now == date_start) or (date_now > date_start and date_now < date_end) or \
				(date_now == date_end and int(time_now) < int(OPS_DAY_START))):
				if 'overrideOnCall' in item:
					oncall.update(determine_shift(item.get('overrideOnCall'), time_start, time_end))
				else:
					oncall.update(determine_shift(roll['onCall'], time_start, time_end))				
	for person in oncall:
		response = response + "\n" + oncall.get(person) + ": " + person 
	return response
