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
from datetime import datetime
from encodings.base64_codec import base64_encode, base64_decode
from gi.overrides import keysyms
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
  
    def __init__(self, filename, err_filename):
        '''Read in csv. Prepare json for upload.'''
        self.err_filename = err_filename  # file to writer errors to
        self.file_b64 = self.csvread2base64(filename)
        self.file_b64_ascii = str(self.file_b64, encoding='ascii')
        self.data['import']['file'] = self.file_b64_ascii
        self.data_json = json.dumps(self.data)
        
 
    def csvread2base64(self, filename):
        with open(filename, 'rb') as fh:
            csv = fh.read()        
            (file_b64, unused) = base64_encode(csv)
            return file_b64

    def base64_2csvfile(self, csv_b64_ascii):
        csv_b64 = bytearray(csv_b64_ascii, 'ascii')
        (csv, unused) = base64_decode(csv_b64)
        with open(self.err_filename, 'a') as fh:
            fh.write(str(datetime.now())+'\n')        
        with open(self.err_filename, 'ab') as fh:
            fh.write(csv)        

    def json_extractor(self, json_str, keys):
        v = json.loads(json_str)
        for k in keys:
            v = v.get(k)
        return v
    
    def upload_status_get(self, response_id):
        '''Generator which yields the status name of successive status queries'''
        url_status = self.url_join((str(response_id),))
        status_name = None
        while status_name not in ('completed', 'finished'):
            response = requests.get(url_status, headers=self.headers)
            status_name = self.json_extractor(response.text, ('import', 'status', 'name',))
            yield status_name  
    
    def upload(self, url_upload, period=1):
        # Post import
        response = requests.post(url_upload, headers=self.headers, data=self.data_json)
        id = self.json_extractor(response.text, ('import', 'id',))

        # Repeatedly check status until finished
        status_name = None
        for status_name in self.upload_status_get(id):
            sleep(period)
            print (status_name)
        
        # Examine result of import
        url_result = self.url_join((str(id), 'result',))
        response = requests.get(url_result, headers=self.headers)
        result = self.json_extractor(response.text, ('result',))
        
        # Save failure_csv if it exists
        failure_csv = self.json_extractor(response.text, ('result', 'failure_csv',))
        if failure_csv:
            self.base64_2csvfile(failure_csv)
        return sorted(result.items())

    def url_join(self, endpoint_parts):
        endpoint = '/'.join((self.endpoint_base,) + endpoint_parts)
        return ''.join(('https://', self.slug, endpoint, '?access_token=', self.token))
           
if __name__ == "__main__":
    err_filename = 'uploader_errors.csv'
    for filename in argv[1:]:  # skip scriptname in argv[0] 
        uploader = Uploader(filename, err_filename)
        url_upload = uploader.url_join(())
        print (uploader.upload(url_upload))
