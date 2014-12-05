#!/usr/bin/python3
'''
Created on 23 Nov 2014

@author: julian

srgp.nationbuilder.com/api/v1/imports?access_token=9c285c1ec7debb2d5cee02b6b9762d4b7e198697d63dcaa76b90a639f646e1c0
{"import": {"is_overwritable": true, "type": "people", "file": "ZXh0ZXJuYWxfaWQsZmlyc3RfbmFtZSxsYXN0X25hbWUKMTIzNDU2NyxKYW1lcyxCcm93bgo=\n"}}
    filename = '/home/julian/Desktop/SRGP/register_mini.csv'
    fh = open(filename, 'r')
    csv = fh.read()
'''
from encodings.base64_codec import base64_encode
import json
import requests
from sys import argv
from time import sleep

class Uploader(object):
    endpoint_base = '/api/v1/imports'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', }
    slug = 'srgp.nationbuilder.com'
    token = '9c285c1ec7debb2d5cee02b6b9762d4b7e198697d63dcaa76b90a639f646e1c0'
    data = {'import': {
                'file': None,
                'type': 'people',  # voter fails (Julian 27-nov-2014) member fails Julian 27-nov-2014
                'is_overwritable': True,
              }}    
    response_id=None    
  
    def __init__(self, filename):
        '''Read in csv. Prepare json for upload.'''
        self.file_b64 = self.csvread2base64(filename)
        self.file_b64_ascii = str(self.file_b64, encoding='ascii')
        self.data['import']['file'] = self.file_b64_ascii
        self.data_json = json.dumps(self.data)
        url_upload = self.assemble_url((self.endpoint_base,))
        self.upload(url_upload)
        
    def assemble_url(self, endpoint_parts):
        endpoint = '/'.join(endpoint_parts)
        return "https://" + self.slug + endpoint + '?access_token=' + self.token

    def csvread2base64(self, filename):
        with open(filename, 'rb') as fh:
            csv = fh.read()        
            (file_b64, unused) = base64_encode(csv)
            return file_b64
    
    def get_import_result(self, url_result):
        response = requests.get(url_result, headers=self.headers)
        return json.loads(response.text)['result']
    
    def get_import_status(self, url_status):
        response = requests.get(url_status, headers=self.headers)
        response_dict = json.loads(response.text)
        return {'id':response_dict['import']['id'],
                'status_name':response_dict['import']['status']['name']}
    
    def upload(self, url_upload, period=1):
        for status_name in self._upload_helper(url_upload):
            print (status_name)
            if status_name in ('completed', 'finished'):
                break
        
        # Examine result of import
        url_result = self.assemble_url((self.endpoint_base, str(self.response_id), 'result',))
        result = self.get_import_result(url_result)
        print (result)

    def _upload_helper(self, url_upload, period=1):
        '''A generator which posts an import then yields the status name of successive status queries'''
        #Post import
        response = requests.post(url_upload, headers=self.headers, data=self.data_json)
        self.response_id = json.loads(response.text)['import']['id']
        
        #Get import status
        url_status = self.assemble_url((self.endpoint_base, str(self.response_id),))
        while True:
            status_name = self.get_import_status(url_status)['status_name']
            if status_name in ('completed', 'finished'):
                break
            else:
                yield status_name  
                sleep(period)
        yield status_name  
        
if __name__ == "__main__":
    for filename in argv[1:]:  # skip scriptname in argv[0] 
        uploader = Uploader(filename)
