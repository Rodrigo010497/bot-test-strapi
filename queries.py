datbase_url = "https://handsin-bot-database.herokuapp.com/"
from pprint import pprint  
import requests
import json
from pyinflect import getAllInflections, getInflection
import re
import random
import copy
from nltk.stem import PorterStemmer
from collections import OrderedDict

porter = PorterStemmer()

def isEntityUnknown(value):
	products = make_query("products?product_value_name="+value)
	services = make_query("services?service_value_name="+value)
	return not(products != [] or services != [])

def get_price(service):
	price = make_query("services?service_value_name="+service)
	return price[0].get("price")

def make_query(query):
	return(requests.get(datbase_url+query).json()) 
def GeneralRetrievalQuery(resp,client_id,recipient,intent,answer=None):
	if answer == None:
		answer_id  = get_answer_id(resp,intent)
	else:
		answer_id = answer

	print(answer_id)
	query = datbase_url + "responses?answer_id=" + answer_id + "&_where[client.sendr_id]="+str(client_id)
	answer =	build_answer(query,resp)
	answer = substituter(answer,resp,recipient)
	return answer





def build_answer(query,resp):
	print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
	print(query)
	r = requests.get(query)
	if r != []:
				answer = [data.get("text") for data in r.json()]	
				answer = random.choice(answer)
	else:
			answer = "What do you mean by " + resp.get("text") + "?"
	return answer

def variate_answer_with_user_input(resp,entity_key,modify_word=None):
	word = "placeholder"
	# Only process entities if they exist in the message
	if entity_key in resp.get("entities").keys():
		entity = resp.get("entities").get(entity_key)
		#check if the word used by the user is an english word if not use the default value retrieved by the wit.ai bot
		body  = entity[0].get("body")
		if body.isalpha():
			#if it is a word pick at random either the user value or the default value to substitute in the answer
			word = random.choice([entity[0].get("body"), entity[0].get("value")])
		else:
				word = entity[0].get("value")

		#format word so it is in it's basic form exampel "repaired" becomes "repair"
		new_word = porter.stem(word)
		#apply one of the formatations bellow to the word
		#TODO get rid of all these if's
		if modify_word == "past":
			new_word = getInflection(new_word,"VBN")
			if new_word != None:
				word = new_word[0]
		elif(modify_word == "plural"):
			new_word =  getInflection(word, "NNS")
			if new_word != None:
				word = new_word[0]
		else:
			word = new_word
	return word

def listServices(product):
	string = "\n"
	if product == "all":
		products = make_query("products")
		products = [product.get("product_value_name") for product in products]
	else:
		products = make_query("products?product_value_name="+product)
		products = [products[0].get("product_value_name")]
	for product in products:
		string += product.upper() +"\n"
		services = make_query("services?_where[products.product_value_name]="+product)
		services = [service.get("service_value_name")+"\n" for service in services]
		string += "".join(services)
	return string
		
def substituter(answer,resp,recipient,ent=None):
	entities = resp.get("entities")
	price = "placeholder"
	value = "placeholder"
	if "productAction:productAction" in entities.keys():
		price = get_price(entities.get("productAction:productAction")[0].get("value"))
		print("*"*10)
		print("price",price)
		print("*"*10)
	if "product:product" in entities.keys():
			value = entities.get("product:product")[0].get("value")
	#list of key value pairs the keys are to be substituted in the template answers by the values
	values = [
            [r"\bPRODUCT_VALUE\b",variate_answer_with_user_input(resp,"product:product")],
            [r"\bPRODUCT_VALUE_PLURAL\b",variate_answer_with_user_input(resp,"product:product","plural")],
            [r"\bPRODUCT_SERVICES\b",listServices(value)],
            [r"\bALL_PRODUCT_VALUES_SERVICES\b",listServices("all")], 
						[r"\bPRODUCT_ACTION_VALUE_PAST_TENSED\b",variate_answer_with_user_input(resp,"ProductAction:ProductAction","past")],
						[r"\bPRODUCT_ACTION_VALUE\b",variate_answer_with_user_input(resp,"productAction:productAction")],
						[r"\bNAME\b", recipient.get("first_name") ],
						[r"\bPRODUCT_SERVICE_RATE\b",price],
						[r"\bPRICE\b",price],
					]
	new_answer = copy.deepcopy(answer)
	if "ALL_PRODUCT_VALUES_SERVICES" in answer:
		new_answer = "Idon't know what do you mean by " + resp.get("text") + " but...\n" + new_answer 
	for value in values:
			new_answer = re.sub(value[0], value[1], new_answer)
	return new_answer

def sanitizeKey(entities_list,entities,key):
	new_key = copy.deepcopy(key)
	for entity in entities_list:
		value = entities.get((entity + ":"+ entity).replace("|",""))[0].get("value")
		check = isEntityUnknown(value)
		print(check)
		if check:
			new_key = new_key.replace("|"+ entity,"")
	print(new_key)
	return new_key

def get_answer_id(resp,intent):
	entities = resp.get("entities")
	entities_list = sorted(list(OrderedDict.fromkeys([i.split(":")[0]+"|" for i in entities])), key=len)
	entities_list[-1] = entities_list[-1].replace("|","")
	entities_key = "".join(entities_list)
	key = sanitizeKey(entities_list,entities,intent + "|" + entities_key)
	return key

def requestServices(resp,client_id,recipient,intent):
	template_answer = GeneralRetrievalQuery(resp,client_id,recipient,intent)
	return template_answer

def ourServices(resp,client_id,recipient,intent):
	if intent == "NONE":
		template_answer =	GeneralRetrievalQuery(resp,client_id,recipient,intent,"ourServices|NONE")
	else:
		template_answer = GeneralRetrievalQuery(resp,client_id,recipient,intent)
	return template_answer

queries = {
	"ourServices":ourServices,
	"NONE":ourServices,
	"requestServices":requestServices
}


def call_query(intent,resp,client_id,recipient):
	query = queries.get(intent)
	return query(resp,client_id,recipient,intent)