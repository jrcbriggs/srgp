'''
Created on 30 Nov 2014

@author: julian
'''
from encodings.base64_codec import base64_encode
import json
import unittest

from uploader import Uploader


class Test(unittest.TestCase):


    def setUp(self):
        self.endpoint = '/api/v1/imports'
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', }
        self.slug = 'srgp.nationbuilder.com'
        self.token = '9c285c1ec7debb2d5cee02b6b9762d4b7e198697d63dcaa76b90a639f646e1c0'
        self.url = "https://" + self.slug + self.endpoint + '?access_token=' + self.token
        self.data = {'import': {
                'file': None,
                'type': 'people',  # voter fails (Julian 27-nov-2014) member fails Julian 27-nov-2014
                'is_overwritable': True,
              }}  
          
        self.csv = b'a,b,c,d,e,f\n0,1,2,3,4,5\n6,7,8,9,10,11\n'
        (self.file_b64, length) = base64_encode(self.csv)
        self.file_b64_ascii = str(self.file_b64, encoding='ascii')
        self.data['import']['file'] = self.file_b64_ascii
        self.data_json = json.dumps(self.data)

        self.filename = '/tmp/test_nbapi.csv'
        csv_str = 'a,b,c,d,e,f\n0,1,2,3,4,5\n6,7,8,9,10,11\n'
        with open(self.filename, 'w') as fh:
            fh.write(csv_str)        
        self.nbapi = Uploader(self.filename)

    def testNbApi(self):
        self.assertIsInstance(self.nbapi, Uploader)
    
    def testNbApi_file_b64(self):
        actual=self.nbapi.file_b64
        expected=self.file_b64
        self.assertEqual(actual, expected)
    
    def testNbApi_file_b64_ascii(self):
        actual=self.nbapi.file_b64_ascii
        expected=self.file_b64_ascii
        self.assertEqual(actual, expected)
    
    def testNbApi_data(self):
        actual=self.nbapi.data
        expected=self.data
        self.assertDictEqual(actual, expected)
    
    def testNbApi_data_json(self):
        actual=self.nbapi.data_json
        expected=self.data_json
        self.assertEqual(actual, expected)
    
    def test_csvread2base64(self):
        actual = self.nbapi.csvread2base64(self.filename)
        expected = self.file_b64
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
