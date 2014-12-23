'''
Created on 23 Dec 2014

@author: ph1j
'''

from splinter.browser import Browser
from time import sleep


class Scrape(object):

    def __init__(self, url, params):
        with Browser('firefox') as b:
            b.visit(url)
            b.fill_form(params)
            b.find_by_id('edit-submit').first.click()
            for label in ('Officers', 'Supporters', 'Volunteers',): # ,'Search'
                b.click_link_by_text(label)
                b.find_by_value('Export to CSV').first.click()
                sleep(9)


if __name__ == '__main__':
    params = {'name': 'j.briggs@phonecoop.coop', 'pass': 'KewGr33n', }
    url = 'https://my.greenparty.org.uk/civicrm'
    s = Scrape(url, params)
