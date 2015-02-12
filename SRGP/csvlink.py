'''
Created on 2 Feb 2015

@author: julian
'''
import json
from pprint import pprint
training_filename = '/home/julian/SRGP/csvlink/training.json'

if __name__ == '__main__':
    fh = open(training_filename)
    trainings = json.load(fh)
    pprint(trainings)
