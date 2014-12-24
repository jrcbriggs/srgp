'''
Created on 23 Dec 2014

@author: ph1j
'''

from glob import glob
from os.path import join
from posix import rename
from selenium import webdriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from splinter.browser import Browser
from time import sleep
from oauthlib.oauth2.rfc6749.utils import params_from_uri


class Downloader(object):

    def __init__(self, download_dir):
        self.ffpp = {
            'browser.download.folderList': 2,
            'browser.download.manager.showWhenStarting': False,
            'browser.download.dir': download_dir,
            'browser.helperApps.neverAsk.saveToDisk': 'text/csv', }

    def download(self, params, url):
#         with Browser('firefox', profile_preferences=self.ffpp) as b:
        with Browser('chrome') as b:
            b.visit(url)
            b.fill_form(params)
            b.find_by_id('edit-submit').first.click()

            for label in ():  # 'Officers', 'Supporters', 'Volunteers',):  # ,'Search'
                b.click_link_by_text(label)
                b.find_by_value('Export to CSV').first.click()
                self.rename_file(download_dir, prefix='Report', label='SRGP_' + label)

            # Members
            xpath0 = '//li[@class="menumain crm-Members"]'
            dropdown = b.find_by_xpath(xpath0)
            dropdown.first.click()
            sleep(9)
            xpath1 = xpath0 + '//li[@class="crm-Members_-_All_Members"]'
            elem = b.find_by_xpath(xpath1)
#             elem.
            elem.first.click()
#             b.click_link_by_href('https://my.greenparty.org.uk/civicrm/report/instance/19?reset=1')
#             sleep(9)
#             b.find_link_by_text('Members - All Members').first.click()
            b.find_by_value('Export to CSV').first.click()
            self.rename_file(download_dir, prefix='Report', label='SRGP_MembersAll')

    def rename_file(self, download_dir, prefix, label):
        pathname_glob = join(download_dir, prefix + '*.csv')
        pathname = glob(pathname_glob)[0]
        pathname_new = pathname.replace(prefix, label)
        rename(pathname, pathname_new)
        return'Downloaded: ' + pathname_new


if __name__ == '__main__':
    params = {'name': 'j.briggs@phonecoop.coop', 'pass': 'KewGr33n', }
    url = 'https://my.greenparty.org.uk/civicrm'
    download_dir = '/home/julian/Downloads'
    s = Downloader(download_dir).download(params, url)
