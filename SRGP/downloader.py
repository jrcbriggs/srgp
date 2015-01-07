#!/usr/bin/python3
'''
Created on 23 Dec 2014

@author: ph1j
'''

from glob import glob
import os
from os.path import join
from posix import rename
from splinter.browser import Browser
from time import sleep
class Downloader(object):

    def __init__(self, download_dir):
        self.ffpp = {
            'browser.download.folderList': 2,
            'browser.download.manager.showWhenStarting': False,
            'browser.download.dir': download_dir,
            'browser.helperApps.neverAsk.saveToDisk': 'text/csv', }

    def download(self, params, url):
        with Browser('firefox', profile_preferences=self.ffpp) as b:
            b.visit(url)
            b.fill_form(params)
            b.find_by_id('edit-submit').first.click()

            for label in ('Officers', 'Supporters', 'Volunteers',):  # ,'Search'
                b.click_link_by_text(label)
                sleep(5)
                b.find_by_value('Export to CSV').first.click()
                yield self.rename_file(download_dir, prefix='Report', label='SRGP_' + label)

    def rename_file(self, download_dir, prefix, label):
        pathname_glob = join(download_dir, prefix + '*.csv')
        pathname = glob(pathname_glob)[0]
        pathname_new = pathname.replace(prefix, label)
        rename(pathname, pathname_new)
        return'Downloaded: ' + pathname_new


if __name__ == '__main__':
    params = {'name': 'j.briggs@phonecoop.coop', 'pass': os.environ.get('GP_PASSWORD'), }
    url = 'https://my.greenparty.org.uk/civicrm'
    download_dir = os.path.join(os.environ.get('HOME'), 'Downloads')
    downloader = Downloader(download_dir)
    for response in downloader.download(params, url):
        print(response)
