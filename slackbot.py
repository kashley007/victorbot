from globalconsts import *
from slackclient import SlackClient
import api
import json

#Commands that a SlackBot knows
ONCALL_COMMAND = "oncall"
HELP_COMMAND = "help"


OPTIONS = {	ONCALL_COMMAND: 'The people you need to call when you have an issue',
			HELP_COMMAND: 'What you are looking at now'}

class Bot(object):

	def __init__(self):
		self.AT_BOT = "<@" + BOT_ID + ">"
		self.client = SlackClient(SLACK_BOT_TOKEN)


	def handle_command(self, command, channel):
		""" Handles commands received from a slack channel"""
		response = ""
		if command.startswith(ONCALL_COMMAND):
			for team in TEAMS:
				schedule = api.vo_get_oncall_schedule(X_VO_API_ID, X_VO_Api_Key, team)
				response = "{0}{1}".format(response,api.vo_build_oncall_response(schedule))
		elif command.startswith(HELP_COMMAND):
			count = 1
			for k, v in OPTIONS.items():
				response = "{0}\n{1}. {2}: {3}".format(response,count,k,v)
				count = count + 1
		else:
			response = "Don't waste my time. Use *{}* to see what I feel like talking about".format(HELP_COMMAND)
		self.client.api_call("chat.postMessage", channel=channel,text=response, as_user=True)

	def parse_slack_output(self, slack_rtm_output):
		""" Listens for @BOT_ID in slack channel and sends command to the command handler"""
		try:
			output_list = slack_rtm_output
			if output_list and len(output_list) > 0:
				for output in output_list:
					if (output and 'text' in output) and (self.AT_BOT in output['text']):
						return output['text'].split(self.AT_BOT)[1].strip().lower(), output['channel']
		except Exception as e:
			raise e


def get_bot_ID(slack_token, bot_name):
	"""Helper function to determine the unique ID for slackbot user"""
	slack_client = SlackClient(slack_token)
	api_call = slack_client.api_call("users.list")

	if api_call.get('ok'):
		users = api_call.get('members')
		for user in users:
			print user
			if 'name' in user and user.get('name') == bot_name:
				return user.get('id')
