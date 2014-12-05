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

class Csv2Nb(object):
    endpoint_imports = '/api/v1/imports'
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', }
    slug = 'srgp.nationbuilder.com'
    token = '9c285c1ec7debb2d5cee02b6b9762d4b7e198697d63dcaa76b90a639f646e1c0'
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
        
    def assemble_url(self, endpoint):
        return "https://" + self.slug + endpoint + '?access_token=' + self.token

    def csvread2base64(self, filename):
        with open(filename, 'rb') as fh:
            csv = fh.read()        
            (file_b64, length) = base64_encode(csv)
            return file_b64
    
    def get_import_result(self, url_result):
        response = requests.get(url_result, headers=self.headers)
        return json.loads(response.text)['result']
    
    def get_import_status(self, url_status):
        response = requests.get(url_status, headers=self.headers)
        response_dict = json.loads(response.text)
        return {'id':response_dict['import']['id'],
                'status_name':response_dict['import']['status']['name']}
    
    def upload(self, url_upload):
        response = requests.post(url_upload, headers=self.headers, data=self.data_json)
        return json.loads(response.text)['import']['id']  # Return the import id
    
    def wait_for_import_finished(self, url_status, period=1, ntries=99):
        status_name = None
        for i in range(ntries):
            status_name = self.get_import_status(url_status)['status_name']
            print (status_name)
            if status_name in ('completed', 'finished'):
                break
            sleep(period)
        return status_name  

if __name__ == "__main__":
    for filename in argv[1:]:  # skip scriptname in argv[0] 
        
        # Upload csv
        nbapi = Csv2Nb(filename)
        url_upload = nbapi.assemble_url(nbapi.endpoint_imports)
        response_id = nbapi.upload(url_upload)
        print ('response_id:', response_id)
        
        # Wait until finished
        url_status = nbapi.assemble_url('/'.join((nbapi.endpoint_imports, str(response_id),)))
        print(url_status)
        status_name = nbapi.wait_for_import_finished(url_status)
        
        # Examine result of import
        url_result = nbapi.assemble_url('/'.join((nbapi.endpoint_imports, str(response_id), 'result',)))
        print(url_result)
        result = nbapi.get_import_result(url_result)
        print (result)
