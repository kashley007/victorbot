from globalconsts import *
import api
from slackbot import Bot
import time

def main():
	
	READ_WEBSOCKET_DELAY = 1
	VictorBot = Bot()
	slack_client = VictorBot.client

	if slack_client.rtm_connect():
		print("VictorBot is connected and running!")
		while True:
			command, channel = VictorBot.parse_slack_output(slack_client.rtm_read())
			if command and channel:
				VictorBot.handle_command(command, channel)
			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print("Connection failed. Possible invalid Slack token or botID")

if __name__ == "__main__":
	main()