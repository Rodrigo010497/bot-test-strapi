"""
Module Author
-
Rodrigo Elias Sanchez

Description
-
Api for connecting Wit.ai to the Facebook page and those to the strapi database in heroku

Date Created
-
05/06/2021

Date Last Updated
-
15/06/2021

Last changes made by
-
Rodrigo Elias Sanchez

Date of Last Review
-
dd/mm/yyyy

Reviewer
-
name
"""

import os
import flask
import requests
from wit import Wit
from pprint import pprint
import populate_database
from pymessenger.bot import Bot
from flask import render_template
import queries
import facebook


database = populate_database.Database(populate_database.api_url)
pprint(database)
#database.update(35,50)
#database.populate()

client = Wit(os.environ["WIT_CLIENT_ACCESS_TOKEN"])
FB_ACESS_TOKEN = os.environ["FBTOKEN"]
graph = facebook.GraphAPI(FB_ACESS_TOKEN)

app = flask.Flask(__name__)
sess = requests.Session()
datbase_url = "https://handsin-bot-database.herokuapp.com/"

def isValidReponse(response):
	"""
	Description
	-------
	checks if the response received by the webhook is valid for doing wit.ai related processing
	Args:
		response (python dictionary, parameter): Wit.ai response  
	Returns
	-------
	valid_message : boolean
		true or false flag depending if intents and entities are present on the response or not
	"""
	entities_exist = bool(response.get("entities"))
	intents_exist = bool(response.get("intents"))
	return entities_exist and intents_exist

def get_answer(resp,client_id,recipient):
	"""
Description
-------
This function will decide which query to make based on the intent
and utilize the Wit.ai response to build the query

Args:
   resp (python dictionary, parameter): Wit.ai response 
   intent (string, input): Intent identified by Wit.ai 

Returns
-------
query : string or boolean
   final query to be made to the database or a False booolean indicating the query is unkown to the database
"""
	#check if the bot understood the message received basically a null check
	response = ""
	check = isValidReponse(resp)
	if check:
		intent = resp.get("intents")[0].get("name")
		response = queries.call_query(intent,resp,client_id,recipient)
	else:
		intent = "NONE"
		response = queries.call_query(intent,resp,client_id,recipient)
		# elif intent == "make_list":
		# 		query = datbase_url + list(resp.get("entities").values())[0][0].get("value")
		
	return response

@app.route('/')
def index():
    return render_template('index.html')

def postWitMessage(message, client_id, recipient):
	"""
Description
-------
Function responsible for reading the Wit.ai client message, identifying the intent,
generating the database query based on the intent and response taken from the message
and finally retrieving querying the database and printing the queried data. 

Args:
   message (python dictionary, parameter): message sent by the Wit.ai client 
       """
	 
	resp = client.message(message)
	#checks if the initial response is valid for extracting intents and entities
	print("Wit Response")
	print("======================================")
	pprint(resp)
	print("======================================")
	response = get_answer(resp,client_id,recipient)
	print(response)
	# if query:
	# 	r = requests.get(query)
	# 	pprint(r)
	# 	response = [data.get("response") for data in r.json()]
	# 	response = "".join([word+"\n" for word in response])
	# else:
	# 	response = "What do you mean by " + resp.get("text") + "?"
	return(response)

def postToMessenger(message,client_id,recipient):
	"""
Description
-------
There are 2 ways of sending a message back to messenger.
By using pymessenger or just doing a post request with requests
in both cases you will need the fb page access token and the recipient (on this case the sender) id. 
When just doing a post request the url will always be as shown bellow with the slight difference of teh version of the api being used to find your API's version just look through the version of the webhooks in your facebook developer app page.

 r = requests.post("https://graph.facebook.com/v11.0/me/messages?access_token="+FB_ACESS_TOKEN,
	 				data= json.dumps({
	 					"recipient":{"id":recipient},
	 					"message":{"text":fb_answer},
	 					'messaging_type': 'RESPONSE'
	 				}),
	 				headers={
	 				'Content-Type': 'application/json'
	 				})

Recommend using pymessenger as it does the url automatically. 
Args:
   message (python dictionary, parameter): message sent back to the user chat in messenger 
	 recipient (string, parameter): id of the chat which sent the message to wit.ai
	 FB_ACESS_TOKEN (string, enviroment variable): access token for the facebook page
	"""
	fb_answer = str(postWitMessage(message,client_id,graph.get_object(recipient)))
	bot = Bot(FB_ACESS_TOKEN)
	print(fb_answer)
	bot.send_text_message(recipient,fb_answer)

@app.route("/webhook", methods=["GET", "DELETE"])
def webook():
	# keep alive with facebook 
	x = flask.request.args
	print(x['hub.challenge'])
	return x['hub.challenge'], 200 

@app.route("/webhook", methods=["POST"])
def post_webhook():
	"""
Description
-------
Webhook responsible for listening for the messages sent by wit.ai container
function which is in charge of maintaining the connection alive, initial formatting of teh message and calling the postWitMessage function.   
	"""
	#receive data in json format which is equivalent to python dict
	print("Message Recieved")
	resp= flask.request.json
	print("Wit response")
	print("-"*40)
	pprint(resp)
	print("-"*40)

	#keeps connection with facebook alive
	if resp.get("object") == "user":
		print("facebook keep alive?")
		return "ok" , 200
	
	#get the message received from wit.ai through messenger extract the contents and the sender id
	print("client id")
	print("-"*10)
	print(resp.get("entry")[0].get("id") == "103836428003921")
	print("-"*10)
	messaging = resp.get("entry")[0].get("messaging")[0]
	message = messaging.get("message").get("text")
	recipient = messaging.get("sender").get("id")
	client_id = messaging.get("recipient").get("id")
	print("=====================================")
	pprint(graph.get_object(recipient))
	print("-"*10)
	print("Message:", "\t" + message)
	print("-"*10)

	#send a message back based on the wit.ai message
	print("Posting it to wit ")
	postToMessenger(message,client_id,recipient)
			
	return "ok" , 200 

app.run("0.0.0.0")