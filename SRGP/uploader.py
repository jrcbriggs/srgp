#!/usr/bin/python3
'''
Created on 23 Nov 2014

@author: julian

srgp.nationbuilder.com/api/v1/imports?access_token=9c285c1ec7debb2d5cee02b6b9762d4b7e198697d63dcaa76b90a639f646e1c0
{"import": {"is_overwritable": true, "type": "people", "file":
"ZXh0ZXJuYWxfaWQsZmlyc3RfbmFtZSxsYXN0X25hbWUKMTIzNDU2NyxKYW1lcyxCcm93bgo=\n"}}
    filename = '/home/julian/Desktop/SRGP/register_mini.csv'
    fh = open(filename, 'r')
    csv = fh.read()
'''
from base64 import b64encode, b64decode
from datetime import datetime
import json
from os import path
from os.path import dirname, basename
from pprint import pprint
import requests
from sys import argv
import sys
from time import sleep

from configurations import nbslug, nbtoken


class Uploader(object):

    '''Upload (NB format) csv file to NB.
    1. Upload
    2. Check status repeatedly
    3. Download results (which may include error_csv
    4. Append results (if any) to upload_errors file
    '''
    endpoint_base = '/api/v1/imports'
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json', }
    data = {'import': {
            'file': None,
            'type': 'people',
            'is_overwritable': True,
            }}

    def __init__(self, filename, err_filename):
        '''Read in csv. Prepare json for upload. Prepare header for log file'''
        self.err_filename = self.get_err_filename(
            filename, err_filename)  # file to writer errors to
        #
        self.data['import']['file'] = self.csvread2base64ascii(filename)
        self.data_json = json.dumps(self.data)
        self.heading = '\nUploaded file: {} at {}\n'.format(
            filename, str(datetime.now()))

    def get_err_filename(self, csv_filename, err_filename):
        '''Create logfile name'''
        return path.join(dirname(csv_filename), basename(err_filename))

    def csvread2base64ascii(self, filename):
        '''Read and encode csv file contents as base64 ascii encoded'''
        with open(filename, 'rb') as fh:
            csv = fh.read()
            file_b64 = b64encode(csv)
            return str(file_b64, encoding='ascii')

    def base64_2csvfile(self, csv_b64_ascii, heading):
        '''Decode base64 ascii encoded string and append to csv file
        Prepend date and filename of csv upload'''
        csv = b''
        if csv_b64_ascii:
            csv_b64 = bytearray(csv_b64_ascii, 'ascii')
            csv = b64decode(csv_b64)
        with open(self.err_filename, 'a') as fh:
            fh.write(heading)
        with open(self.err_filename, 'ab') as fh:
            fh.write(csv)

    def json_extractor(self, data, keys):
        '''Extract a value from nested dict encoded as json string'''
        v = data
        for k in keys:
            v = v.get(k)
        return v

    def upload_status_get(self, response_id):
        '''Generator yielding the status name of successive status queries'''
        url_status = self.url_join(nbslug, (str(response_id),), nbtoken)
        status_name = None
        while status_name not in ('completed', 'finished'):
            response = requests.get(url_status, headers=self.headers)
            status_name = self.json_extractor(response.json(),
                                              ('import', 'status', 'name',))
            yield status_name

    def upload(self, url_upload, period=1):
        '''Upload csv file to NB:
        1. Upload
        2. Check status repeatedly
        3. Download results (which may include error_csv
        4. Append results (if any) to upload_errors file
        '''
        # Post import
        response = requests.post(url_upload, headers=self.headers,
                                 data=self.data_json)
        
        data = response.json()
        upload_id = self.json_extractor(data, ('import', 'id',))

        # Repeatedly check status until finished
        status_name = None
        for status_name in self.upload_status_get(upload_id):
            yield status_name
            sleep(period)

        # Examine result of import
        url_result = self.url_join(
            nbslug, (str(upload_id), 'result',), nbtoken)
        response = requests.get(url_result, headers=self.headers)
        result = self.json_extractor(response.json(), ('result',))

        # Save csv_b64_ascii if it exists
        csv_b64_ascii = self.json_extractor(response.json(),
                                            ('result', 'csv_b64_ascii',))
        self.base64_2csvfile(csv_b64_ascii, self.heading)
        yield sorted(result.items())

    def url_join(self, nbslug, endpoint_parts, nbtoken):
        '''Assemble url for upload to NB endpoint'''
        endpoint = '/'.join((self.endpoint_base,) + endpoint_parts)
        return ''.join(('https://', nbslug, endpoint, '?access_token=',
                        nbtoken))

if __name__ == "__main__":
    err_filename = 'uploader_log.csv'
    for filename in argv[1:]:  # skip scriptname in argv[0]
        print(filename)
        uploader = Uploader(filename, err_filename)
        url_upload = uploader.url_join(nbslug, (), nbtoken)
        for status in uploader.upload(url_upload):
            print(status, end=' ')
            sys.stdout.flush()
