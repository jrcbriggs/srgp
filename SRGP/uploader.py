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
from gi.overrides import keysyms

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
  
    def __init__(self, filename):
        '''Read in csv. Prepare json for upload.'''
        self.file_b64 = self.csvread2base64(filename)
        self.file_b64_ascii = str(self.file_b64, encoding='ascii')
        self.data['import']['file'] = self.file_b64_ascii
        self.data_json = json.dumps(self.data)
        
    def assemble_url(self, endpoint_parts):
        endpoint = '/'.join((self.endpoint_base,) + endpoint_parts)
        return "https://" + self.slug + endpoint + '?access_token=' + self.token

    def csvread2base64(self, filename):
        with open(filename, 'rb') as fh:
            csv = fh.read()        
            (file_b64, unused) = base64_encode(csv)
            return file_b64

    def get_upload_status(self, response_id):
        '''Generator which yields the status name of successive status queries'''
        url_status = self.assemble_url((str(response_id),))
        status_name = None
        while status_name not in ('completed', 'finished'):
            response = requests.get(url_status, headers=self.headers)
            status_name = self.json_extractor(response.text, ('import', 'status', 'name',))
            yield status_name  
    
    def json_extractor(self, json_str, keys):
        v = json.loads(json_str)
        for k in keys:
            v = v.get(k)
        return v
    
    def upload(self, url_upload, period=1):
        # Post import
        response = requests.post(url_upload, headers=self.headers, data=self.data_json)
        response_id = self.json_extractor(response.text, ('import', 'id',))

        # Repeatedly check status until finished
        status_name = None
        for status_name in self.get_upload_status(response_id):
            sleep(period)
            print (status_name)
        
        # Examine result of import
        url_result = self.assemble_url((str(response_id), 'result',))
        response = requests.get(url_result, headers=self.headers)
        result = self.json_extractor(response.text, ('result',))
        return sorted(result.items())

        
if __name__ == "__main__":
    for filename in argv[1:]:  # skip scriptname in argv[0] 
        uploader = Uploader(filename)
        url_upload = uploader.assemble_url(())
        print (uploader.upload(url_upload))
