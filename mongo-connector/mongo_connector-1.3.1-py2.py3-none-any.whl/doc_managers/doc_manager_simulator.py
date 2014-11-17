# Copyright 2013-2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A class to serve as proxy for the target engine for testing.

Receives documents from the oplog worker threads and indexes them
into the backend.

Please look at the Solr and ElasticSearch doc manager classes for a sample
implementation with real systems.
"""

import itertools

from mongo_connector.errors import OperationFailed
from mongo_connector.doc_managers import DocManagerBase


class DocManager(DocManagerBase):
    """BackendSimulator emulates both a target DocManager and a server.

    The DocManager class creates a connection to the backend engine and
    adds/removes documents, and in the case of rollback, searches for them.

    The reason for storing id/doc pairs as opposed to doc's is so that multiple
    updates to the same doc reflect the most up to date version as opposed to
    multiple, slightly different versions of a doc.
    """

    def __init__(self, url=None, unique_key='_id', **kwargs):
        """Creates a dictionary to hold document id keys mapped to the
        documents as values.
        """
        self.unique_key = unique_key
        self.doc_dict = {}
        self.removed_dict = {}
        self.url = url

    def stop(self):
        """Stops any running threads in the DocManager.
        """
        pass

    def update(self, doc, update_spec):
        """Apply updates given in update_spec to the document whose id
        matches that of doc.

        """
        document = self.doc_dict[doc["_id"]]
        updated = self.apply_update(document, update_spec)
        updated[self.unique_key] = updated.pop("_id")
        self.upsert(updated)
        return updated

    def upsert(self, doc):
        """Adds a document to the doc dict.
        """

        # Allow exceptions to be triggered (for testing purposes)
        if doc.get('_upsert_exception'):
            raise Exception("upsert exception")

        doc_id = doc["_id"]
        self.doc_dict[doc_id] = doc
        if doc_id in self.removed_dict:
            del self.removed_dict[doc_id]

    def remove(self, doc):
        """Removes the document from the doc dict.
        """
        doc_id = doc["_id"]
        try:
            del self.doc_dict[doc_id]
            self.removed_dict[doc_id] = {
                '_id': doc_id,
                'ns': doc['ns'],
                '_ts': doc['_ts']
            }
        except KeyError:
            raise OperationFailed("Document does not exist: %s" % str(doc))

    def search(self, start_ts, end_ts):
        """Searches through all documents and finds all documents that were
        modified or deleted within the range.

        Since we have very few documents in the doc dict when this is called,
        linear search is fine. This method is only used by rollbacks to query
        all the documents in the target engine within a certain timestamp
        window. The input will be two longs (converted from Bson timestamp)
        which specify the time range. The start_ts refers to the timestamp
        of the last oplog entry after a rollback. The end_ts is the timestamp
        of the last document committed to the backend.
        """
        docs = itertools.chain(self.doc_dict.values(),
                               self.removed_dict.values())
        for doc in docs:
            ts = doc['_ts']
            if ts <= end_ts or ts >= start_ts:
                yield doc

    def commit(self):
        """Simply passes since we're not using an engine that needs commiting.
        """
        pass

    def get_last_doc(self):
        """Searches through the doc dict to find the document that was
        modified or deleted most recently."""
        docs = itertools.chain(self.doc_dict.values(),
                               self.removed_dict.values())
        return max(docs, key=lambda x: x["_ts"])

    def _search(self):
        """Returns all documents in the doc dict.

        This function is not a part of the DocManager API, and is only used
        to simulate searching all documents from a backend.
        """

        ret_list = []
        for doc in self.doc_dict.values():
            ret_list.append(doc)

        return ret_list

    def _delete(self):
        """Deletes all documents.

        This function is not a part of the DocManager API, and is only used
        to simulate deleting all documents from a backend.
        """
        self.doc_dict = {}
