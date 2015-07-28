# -*- encoding: utf-8 -*-

import json
import unittest
from django.test import TestCase
from mock import MagicMock, patch
import requests
from stacksync.connection_api import Api
from stacksync.file_metadata import FileMetadata, FileMetadataHelper


class StacksyncAPIMockedTests(unittest.TestCase):
    def setUp(self):
        self.access_token = u'yH6sjP98UBwbuwpDJpE5dtI6TF2La9'
        self.access_token_secret = u'dMW3WcN8bhVtH70xeAMJnasdGgoIbL'
        self.connect = Api()

    def test_root_metadata(self):
        requests.get = MagicMock(return_value=self.fake_request_response())
        root_contents = self.connect.metadata(self.access_token, self.access_token_secret)
        self.assertEquals(len(root_contents), 3)

    def fake_metadata_contents(self):
        return {u'status': None, u'mimetype': None, u'checksum': None, u'filename': u'root', u'is_root': True,
                u'parent_id': None, u'version': None, u'is_folder': True, u'id': None,
                u'contents': [
                        {u'status': u'RENAMED', u'mimetype': u'text/x-python', u'checksum': 1249793342,
                         u'modified_at': u'2014-07-04 12:42:21.238', u'filename': u'null', u'parent_id': None,
                         u'version': 2, u'is_folder': False, u'chunks': [], u'id': 1, u'size': 968
                        },
                        {u'status': u'RENAMED', u'mimetype': u'inode/directory', u'checksum': 0, u'modified_at': u'2014-07-04 12:47:18.632',
                         u'filename': u'foldi', u'is_root': False, u'parent_id': None, u'version': 2, u'is_folder': True, u'id': 2, u'size': 0
                        },
                        {u'status': u'RENAMED', u'mimetype': u'text/plain', u'checksum': 3037139449L, u'modified_at': u'2014-07-18 13:19:09.388',
                         u'filename': u'ffff', u'parent_id': None, u'version': 2, u'is_folder': False, u'chunks': [], u'id': 6, u'size': 51}
                    ]
                , u'size': None}

    def fake_request_response(self):
        request = MagicMock()
        request.status_code = 200
        request.content = json.dumps(self.fake_metadata_contents())
        return request

    def test_shared_folder(self):
        """
        content:
        :return:
        """
        share_to = ["john.doe@yahoo.com", "walter.smith@stacksync.com"]
        # share_to = []
        folder_id = 9
        requests.post = MagicMock(return_value=self.fake_post_share_to())
        response = self.connect.share_folder(folder_id, share_to, self.access_token, self.access_token_secret)
        self.assertEquals(response.status_code, 201)

    def fake_post_share_to(self):
        response = MagicMock()
        response.content = '{"shared_to":[{"name":"joe","email":"john.doe@yahoo.com"},{"name":"walter","email":"walter.smith@stacksync.com"},{"name":"foo","email":"foo@bar.com"}]}'
        response.status_code = 201

        return response

    def test_get_members_of_shared_folder(self):
        share_to = ["al@al.com", "john.doe@yahoo.com", "walter.smith@stacksync.com", "foo@bar.com"]
        folder_id = 7

        requests.post = MagicMock(return_value=self.get_fake_members_of_folder())
        response = self.connect.get_members_of_folder(folder_id, self.access_token, self.access_token_secret)
        for user in response:
            self.assertIn(user['email'], share_to)

    def get_fake_members_of_folder(self):
        return [{u'joined_at': u'2014-07-21', u'is_owner': False, u'name': u'walter', u'email': u'walter.smith@stacksync.com'},
                {u'joined_at': u'2014-07-21', u'is_owner': True, u'name': u'al', u'email': u'al@al.com'},
                {u'joined_at': u'2014-07-21', u'is_owner': False, u'name': u'joe', u'email': u'john.doe@yahoo.com'},
                {u'joined_at': u'2014-07-21', u'is_owner': False, u'name': u'foo', u'email': u'foo@bar.com'}
        ]

    def test_unshare_a_folder(self):
        pass


class FileMetadataHelperTests(unittest.TestCase):

    def test_compute_folder_size(self):
        d = '{"id":null,"parent_id":null,"filename":"root","is_folder":true,"status":null,"version":null,"checksum":null,"size":null,"mimetype":null,"is_root":true,"contents":[{"id":1,"parent_id":null,"filename":"create consumer_oauth.txt","is_folder":false,"status":"NEW","modified_at":"2014-07-04 12:42:21.238","version":1,"checksum":1249793342,"size":968,"mimetype":"text/x-python","chunks":[]},{"id":2,"parent_id":null,"filename":"carpeta","is_folder":true,"status":"NEW","modified_at":"2014-07-04 12:47:18.632","version":1,"checksum":0,"size":0,"mimetype":"inode/directory","is_root":false},{"id":9,"parent_id":null,"filename":"aa","is_folder":true,"status":"NEW","modified_at":"2014-07-21 13:22:21.797","version":1,"checksum":0,"size":0,"mimetype":"inode/directory","is_root":false}]}'
        json_content = json.loads(d)
        file_metadata_helper = FileMetadataHelper(json_content)
        total_size = file_metadata_helper.compute_size()

        self.assertEquals(total_size, 968)
