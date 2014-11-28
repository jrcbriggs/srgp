#!/usr/bin/python
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


def csvread2base64(filenameToModuleName):
    with open(filename, 'rb') as fh:
        csv = fh.read()        
        (data_b64, length) = base64_encode(csv)
        return data_b64
    
if __name__ == "__main__":
#     argv.append('electoralregister-apr2014headNB.csv') #for testing
#     
#     SRGP = '/home/ph1jb/SRGP/'
#     filename = SRGP + argv[1]
    filename = argv[1]
    token = '9c285c1ec7debb2d5cee02b6b9762d4b7e198697d63dcaa76b90a639f646e1c0'
    site_slug = 'srgp.nationbuilder.com'
    endpoint = '/api/v1/imports'
    url = "https://" + site_slug + endpoint + '?access_token=' + token
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', }
    data_b64 = csvread2base64(filename)
    data = {'import': {
                'file': data_b64,
                'type': 'people', # voter fails (Julian 27-nov-2014) member fails Julian 27-nov-2014
                'is_overwritable': True,
              }}
    data_json = json.dumps(data)
    response = requests.post(url, headers=headers, data=data_json)
#     print 'url:', url
#     print 'headers:', headers
#     print 'data_json:', data_json
    print 'response:', response.content
