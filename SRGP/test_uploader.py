'''
Created on 30 Nov 2014

@author: julian
'''

from encodings.base64_codec import base64_encode
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
                'type': 'people',  # voter fails (Julian 27-nov-2014) member fails Julian 27-nov-2014
                'is_overwritable': True,
              }}  
        self.data_json = json.dumps(self.data)
          
        self.csv = b'a,b,c,d,e,f\n0,1,2,3,4,5\n6,7,8,9,10,11\n'
        (self.file_b64, length) = base64_encode(self.csv)
        self.file_b64_ascii = str(self.file_b64, encoding='ascii')
        self.data['import']['file'] = self.file_b64_ascii
        self.data_json = json.dumps(self.data)

        self.filename = '/tmp/test_nbapi.csv'
        csv_str = 'a,b,c,d,e,f\n0,1,2,3,4,5\n6,7,8,9,10,11\n'
        with open(self.filename, 'w') as fh:
            fh.write(csv_str)        
        self.uploader = Uploader(self.filename)
        self.response_post = MagicMock()
        self.response_post.text = '''{
                          "import": {
                            "id": 5,
                            "type": "people",
                            "status": {
                              "name": "queued"
                            }
                          }
                        }
                        '''
        self.response_get = MagicMock()        
        self.response_get.text = '''{
                      "import": {
                        "id": 5,
                        "type": "people",
                        "status": {
                          "name": "finished",
                          "processed": 100,
                          "total": 198
                            }
                          },
                      "result": {
                        "rows_updated": 44,
                        "rows_succeeded": 267,
                        "rows_failed": 54,
                        "failure_csv": "[Base 64 encoded error csv file]"
                          }                    
                      }                        
                     '''
        self.response_get.text0 = '{"import":{"id": 5,}}'
        self.failure_csv='self.failure_csv'
        
    def test_assemble_url(self):
        endpoint_parts = ('a', 'b', 'c',)
        actual = self.uploader.assemble_url(endpoint_parts)
        expected = 'https://' + self.slug + self.endpoint + '/a/b/c' + '?access_token=' + self.token
        self.assertEqual(actual, expected)
        
    @skip
    def test_download_failure_csv(self):
        actual=self.uploader.download_failure_csv('failure_csv_name')
        expected=self.failure_csv
        self.assertEqual(actual, expected)
        
    def test_upload(self):
        requests = uploader.requests
        requests.post = MagicMock(return_value=self.response_post)
        self.uploader.get_upload_status = MagicMock(return_value=['working', 'completed'])
        requests.get = MagicMock(return_value=self.response_get)
        #
        url = self.uploader.assemble_url(())        
        self.uploader.upload(url, period=3)        
        requests.post.assert_called_once_with(url, headers=self.headers, data=self.data_json)
        #        
        url_status = self.uploader.assemble_url(('5',))
#         self.uploader.get_upload_status.assert_called_once_with(url_status, headers=self.headers)
        #        
        url_status = self.uploader.assemble_url(('5', 'result',))
        requests.get.assert_called_with(url_status, headers=self.headers)        
    
    def test_get_upload_status_working(self):
        self.response_get.text = self.response_get.text.replace('finished', 'working')
        return_value = self.response_get
        # Mocks
        requests = uploader.requests
        requests.get = MagicMock(return_value=return_value)
        # Call
        result = next(self.uploader.get_upload_status(5))
        # Assert   
        self.assertEqual(result, 'working')     
        url_status = self.uploader.assemble_url(('5',))
        requests.get.assert_called_with(url_status, headers=self.headers)        
        requests.get.assert_called_with(url_status, headers=self.headers)  
      
    def test_get_upload_status_finished(self):
        '''get_upload_status is a generator. So we use the generator 
        in a loop and exit at end of first iteration 
        '''
        return_value = self.response_get
        # Mocks
        requests = uploader.requests
        requests.get = MagicMock(return_value=return_value)
        # Call
        result = next(self.uploader.get_upload_status(5))
        # Assert   
        self.assertEqual(result, 'finished')     
        url_status = self.uploader.assemble_url(('5',))
        requests.get.assert_called_with(url_status, headers=self.headers)        
        requests.get.assert_called_with(url_status, headers=self.headers)
    
    def test_Uploader(self):
        self.assertIsInstance(self.uploader, Uploader)
    
    def test_Uploader_file_b64(self):
        actual = self.uploader.file_b64
        expected = self.file_b64
        self.assertEqual(actual, expected)
    
    def test_Uploader_file_b64_ascii(self):
        actual = self.uploader.file_b64_ascii
        expected = self.file_b64_ascii
        self.assertEqual(actual, expected)
    
    def test_Uploader_data(self):
        actual = self.uploader.data
        expected = self.data
        self.assertDictEqual(actual, expected)
    
    def test_Uploader_data_json(self):
        actual = self.uploader.data_json
        expected = self.data_json
        self.assertEqual(actual, expected)
        
    def test_csvread2base64(self):
        actual = self.uploader.csvread2base64(self.filename)
        expected = self.file_b64
        self.assertEqual(actual, expected)
        
    def test_json_extractor(self):
        json_str = '{"a":{"b":{"c":3}}}'
        actual = self.uploader.json_extractor(json_str, ('a', 'b', 'c',))
        expected = 3
        self.assertEqual(actual, expected)
        

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
