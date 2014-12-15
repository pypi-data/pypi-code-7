#!/usr/bin/python

import pymongo
from bson.objectid import ObjectId
from pymongo import MongoClient

#  Singleton pattern
# class Singleton:
#   def __init__(self, klass):
#     self.klass = klass
#     self.instance = None
#   def __call__(self, *args, **kwds):
#     if self.instance == None:
#       self.instance = self.klass(*args, **kwds)
#     return self.instance


# @Singleton
class MongoHandler:

    def __init__(self, connectionDetails, db, collection):

        self.connectionDetails = connectionDetails
        self.client = MongoClient(self.connectionDetails)
        self.db = self.client[db]
        self.collection = self.db[collection]

#    def instance(self):
#        if self.client is None:
#        	__init__(self, connectionDetails, db, collection)
#        return self

#    @property
#    def connectionDetails(self):

#    @connectionDetails.setter
#    def connectionDetails(self, value):

    # returns a Cursor instance, which allows to iterate over all matching documents.
    def getItems(self):

        cursor = self.collection.find()
        return cursor

    # can pass a document to find() to limit/filter the returned documents
    # returns a Cursor instance, which allows to iterate over all matching documents.
    def getItemsWithQuery(self, query):

        cursor = self.collection.find(query)
        return cursor

    # Inserts a document or documents into a collection.
    def insert(self, document):

        return self.collection.insert(document)

    # Unordered bulk write operations are batched and sent to the server in arbitrary order where they may be executed in parallel.
    # Any errors that occur are reported after all operations are attempted.
    def bulkInsertUnordered(self, documentsList):

        bulk = self.collection.initialize_unordered_bulk_op()
        for document in documentsList:
            bulk.insert(document)
        try:
            result = bulk.execute()
        except BulkWriteError as bwe:
            pprint(bwe.details)
        return result

    # Ordered bulk write operations are batched and sent to the server in the order provided for serial execution.
    # The return value is a document describing the type and count of operations performed.
    def bulkInsertOrdered(self, documentsList):

        bulk = self.collection.initialize_ordered_bulk_op()
        for document in documentsList:
            bulk.insert(document)
        try:
            result = bulk.execute()
        except BulkWriteError as bwe:
            pprint(bwe.details)
        return result

    # an update conditions document to match the documents to update,
    # an update operations document to specify the modification to perform, and
    # an options document.
    def update(self, updateConditionsDocument, updateOperationsDocument, optionsDocument=None):

        if optionsDocument is None:
            return self.collection.update(updateConditionsDocument, updateOperationsDocument)
        else:
            return self.collection.update(updateConditionsDocument, updateOperationsDocument, optionsDocument)

    # To remove the documents that match a deletion criteria, call the remove() method with the <query> parameter.
    # To remove a single document, call the remove() method with the multiFlag parameter set to true or 1.
    def remove(self, removeConditionDocument, multiFlag=None):

        if multiFlag is None:
            return self.collection.remove(removeConditionDocument)
        else:
            return self.collection.remove(removeConditionDocument, multiFlag)
