"""
Module Author
-
Rodrigo Elias Sanchez

Description
-
Code created to populate the strapi database the admin still needs to be created and the roles in the datbase for the tables need to be set to public. This was created because heroku wipes sqlite databases every couple of hours. To solve this permantly strapi has to be migrated to a postgre database.    

Date Created
-
09/06/2021

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
import requests
import json

api_url = "https://handsin-bot-database.herokuapp.com/"

class Database:
	"""
		Description
		--
		Class responsible for populating the database. 

		Authors
		--
		Rodrigo Elias Sanchez

		Last changed by
		--
		Rodrigo Elias Sanchez

		Last changed date
		--
		15/06/2021
	"""
	def __init__(self,api_url):
			"""
			Description
			-------
			Builder function sets the data to be inserted into the database and the url of the Database
			Args:
				params (list of python dictionaries, parameter): list of dictionaries contaning data to be inserted into the database
				api_url (string, parameter): string representing the datbase http address
			"""
			file = open('data_config.json')
			self.api_url = api_url 
			self.params= json.load(file)
			file.close() 

	def create(self, parameter):
		"""
			Description
			-------
			Function in charge of inserting data into the strapi database. 
			Args:
				parameter (python dictionary, parameter): contains the details of the data to be entered into the database
				self.api_url (string, input): class variable containing the datbase http address
		"""
		url = self.api_url + parameter.pop("table")
		header = {'Content-Type': 'application/json'}
		requests.post(url,
									data= json.dumps(parameter),
									headers= header)


	def update(self, start, end):
		entry_ids = list(range(start,end+1))
		header = {'Content-Type': 'application/json'}
		for entry in entry_ids:
			url = self.api_url + "answers/" + str(entry)
			requests.put(url,
								data=json.dumps({'clients': 1}),
								headers= header)


	def populate(self):
		"""
			Description
			-------
			Function in charge of calling the create function for all data entries to be inserted into the database. 
			Args:
				self.params (python dictionary, input): class variable containing all data entries to be inserted into the database 
		"""
		for param in self.params:
			self.create(param)

	
	