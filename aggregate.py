from pymongo import MongoClient
import csv

client = MongoClient()
db = client.csvtomongo