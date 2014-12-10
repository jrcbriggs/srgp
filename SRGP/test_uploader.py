'''
Created on 30 Nov 2014

@author: julian
'''

from base64 import b64encode, b64decode
import json
import unittest
from unittest.case import skip
from unittest.mock import MagicMock
from uploader import Uploader
import uploader


class Test(unittest.TestCase):

    def setUp(self):
        self.endpoint = '/api/v1/imports'
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', }
        self.slug = 'srgp.nationbuilder.com'
        self.token = '9c285c1ec7debb2d5cee02b6b9762d4b7e198697d63dcaa76b90a639f646e1c0'
        self.url = "https://" + self.slug + self.endpoint + '?access_token=' + self.token
        self.data = {'import': {
            'file': None,
            # voter fails (Julian 27-nov-2014) member fails Julian 27-nov-2014
            'type': 'people',
            'is_overwritable': True,
        }}
        self.data_json = json.dumps(self.data)

        self.csv = b'a,b,c,d,e,f\n0,1,2,3,4,5\n6,7,8,9,10,11\n'
        self.file_b64 = b64encode(self.csv)
        self.file_b64ascii = str(self.file_b64, encoding='ascii')
        self.data['import']['file'] = self.file_b64ascii
        self.data_json = json.dumps(self.data)

        self.filename = '/tmp/test_uploader.csv'
        self.err_filename = '/tmp/test_uploader_errors.csv'
        csv_str = 'a,b,c,d,e,f\n0,1,2,3,4,5\n6,7,8,9,10,11\n'
        with open(self.filename, 'w') as fh:
            fh.write(csv_str)
        self.uploader = Uploader(self.filename, self.err_filename)
        self.response_post = MagicMock()
        self.response_post.text = '{"import":{"id":5}}'
        self.response_get0 = MagicMock()
        self.response_get0.text = '{"import":{"status":{"name":"working"}}}'
        self.response_get1 = MagicMock()
        self.response_get1.text = '{"import":{"status":{"name":"finished"}}}'
        self.response_get2 = MagicMock()

        # Test get csv from results failure_csv
        self.csv = b'Col0,Col1,Col2,Col3,Col4,Col5\na,b,c,d,e,f\n0,1,2,3,4,5\n6,7,8,9,10,11\n'
        self.csv_b64 = b64encode(self.csv)
        self.csv_b64_ascii = str(self.csv_b64, encoding='ascii')
        result = {'result': {'failure_csv': self.csv_b64_ascii}}
        self.response_get2.text = json.dumps(result)
        self.failure_csv = 'self.failure_csv'

    def test_Uploader(self):
        self.assertIsInstance(self.uploader, Uploader)

    def test_Uploader_data(self):
        actual = self.uploader.data
        expected = self.data
        self.assertDictEqual(actual, expected)

    def test_Uploader_data_json(self):
        actual = self.uploader.data_json
        expected = self.data_json
        self.assertEqual(actual, expected)

    def test_csvread2base64(self):
        actual = self.uploader.csvread2base64ascii(self.filename)
        expected = self.file_b64ascii
        self.assertEqual(actual, expected)

    def test_base64_2csvfile(self):
        with open(self.err_filename, 'wb') as fh:
            pass
        self.uploader.err_filename = self.err_filename
        heading = ''
        self.uploader.base64_2csvfile(self.csv_b64_ascii, heading)
        with open(self.err_filename, 'br') as fh:
            actual = fh.read()
            expected = self.csv
            self.assertEqual(actual, expected)

    def test_json_extractor(self):
        json_str = '{"a":{"b":{"c":3}}}'
        actual = self.uploader.json_extractor(json_str, ('a', 'b', 'c',))
        expected = 3
        self.assertEqual(actual, expected)

    def test_upload_status_get_finished(self):
        '''upload_status_get is a generator. Here we just pull the first value.'''
        return_value = self.response_get1
        # Mocks
        requests = uploader.requests
        requests.get = MagicMock(return_value=return_value)
        # Call
        result = next(self.uploader.upload_status_get(5))
        # Assert
        self.assertEqual(result, 'finished')
        url_status = self.uploader.url_join(('5',))
        requests.get.assert_called_with(url_status, headers=self.headers)

    def test_upload_status_get_working(self):
        '''upload_status_get is a generator. Here we just pull the first value.'''
        # Mocks
        requests = uploader.requests
        requests.get = MagicMock()
        # Return on consecetive calls: working, finished
        requests.get.side_effect = [self.response_get0, self.response_get1, ]
        # Call 1
        result = next(self.uploader.upload_status_get(5))
        # Assert
        self.assertEqual(result, 'working')
        # Call 2
        result = next(self.uploader.upload_status_get(5))
        # Assert
        self.assertEqual(result, 'finished')
        url_status = self.uploader.url_join(('5',))
        requests.get.assert_called_with(url_status, headers=self.headers)

    def test_upload(self):
        requests = uploader.requests
        requests.post = MagicMock(return_value=self.response_post)

        # Return on 3 concequetive calls: working, finished, result
        requests.get = MagicMock()
        requests.get.side_effect = [self.response_get0, self.response_get1, self.response_get2, ]
        #
        url = self.uploader.url_join(())
        self.uploader.upload(url, period=3)
        requests.post.assert_called_once_with(url, headers=self.headers, data=self.data_json)
        #
#         url_status = self.uploader.url_join(('5',))
#         requests.get.assert_called_with(url_status, headers=self.headers)
        #
        url_status = self.uploader.url_join(('5', 'result',))
        requests.get.assert_called_with(url_status, headers=self.headers)

    def test_url_join(self):
        endpoint_parts = ('a', 'b', 'c',)
        actual = self.uploader.url_join(endpoint_parts)
        expected = 'https://' + self.slug + self.endpoint + '/a/b/c' + '?access_token=' + self.token
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
