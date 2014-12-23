'''
Created on 23 Dec 2014

@author: ph1j
'''

from splinter.browser import Browser
from time import sleep


class Scrape(object):

    def __init__(self, username, password, url):
        #         browsername = 'chrome'
        #         browsername = 'zope.testbrowser'
        browsername = 'firefox'
        with Browser(browsername) as b:
            b.visit(url)
            # Find the username form and fill it with the defined username
            b.find_by_id('edit-name').first.fill(username)

            # Find the password form and fill it with the defined password
            b.find_by_id('edit-pass').first.fill(password)
            b.find_by_id('edit-submit').first.click()
            b.click_link_by_text('Officers')
            b.find_by_value('Export to CSV').first.click()
#             with b.get_prompt() as prompt:
#                 prompt.accept()
            sleep(9)


if __name__ == '__main__':
    username = 'j.briggs@phonecoop.coop'
    password = 'KewGr33n'
    slug = 'my.greenparty.org.uk/civicrm'
    url = 'https://{}'.format(slug)  # , password, slug)
    s = Scrape(username, password, url)
