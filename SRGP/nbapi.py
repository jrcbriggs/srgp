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
from encodings import idna

class Csv2Nb(object):
    endpoint = '/api/v1/imports'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', }
    slug = 'srgp.nationbuilder.com'
    token = '9c285c1ec7debb2d5cee02b6b9762d4b7e198697d63dcaa76b90a639f646e1c0'
    url = "https://" + slug + endpoint + '?access_token=' + token
    data = {'import': {
                'file': None,
                'type': 'people',  # voter fails (Julian 27-nov-2014) member fails Julian 27-nov-2014
                'is_overwritable': True,
              }}        
  
    def __init__(self, filename):
        self.file_b64 = self.csvread2base64(filename)
        self.file_b64_ascii = str(self.file_b64, encoding='ascii')
        self.data['import']['file'] = self.file_b64_ascii
        self.data_json = json.dumps(self.data)

    def csvread2base64(self, filename):
        with open(filename, 'rb') as fh:
            csv = fh.read()        
            (file_b64, length) = base64_encode(csv)
            return file_b64
    
    def upload(self):
        self.response = requests.post(self.url, headers=self.headers, data=self.data_json)
        self.status_code = self.response.status_code
        self.response_text = self.response.text
        self.response_dict = json.loads(self.response_text)
        self.response_id = self.response_dict['import']['id']
        
    def get_import_status(self, id):
        endpoint = '/api/v1/imports/'
        url = 'https://' + self.slug + endpoint + str(id) + '?access_token=' + self.token
        self.status = requests.post(url, headers=self.headers)
        return self.status

if __name__ == "__main__":
    for filename in argv[1:]:  # skip scriptname in argv[0] 
        nbapi = Csv2Nb(filename)
        nbapi.upload()
        print ('status_code:', nbapi.status_code)
        print ('response_text:', nbapi.response_text)
        print ('response_dict:', nbapi.response_dict)
        print ('response_id:', nbapi.response_id)
        status = nbapi.get_import_status(nbapi.response_id)
        print('status', status)
