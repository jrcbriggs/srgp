# -*- coding: utf-8 -*-
from selenium import selenium
import unittest, time, re

class civi_se_testcase_remote_control(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "https://my.greenparty.org.uk/civicrm")
        self.selenium.start()
    
    def test_civi_se_testcase_remote_control(self):
        sel = self.selenium
        sel.open("/civicrm")
        sel.click("//ul[@id='civicrm-menu']/li[4]")
        sel.click("css=li.active > div.menu-item > a")
        sel.wait_for_page_to_load("30000")
        sel.click("id=_qf_GPDetail_submit_csv")
        sel.wait_for_page_to_load("30000")
        sel.click("//ul[@id='civicrm-menu']/li[3]")
        sel.click("css=li.active > div.menu-item > a")
        sel.wait_for_page_to_load("30000")
        sel.click("//ul[@id='civicrm-menu']/li[3]")
        sel.click("css=div.menu-item > a")
        sel.wait_for_page_to_load("30000")
        sel.click("id=_qf_Basic_refresh")
        sel.wait_for_page_to_load("30000")
        sel.click("id=CIVICRM_QFID_ts_all_4")
        sel.select("id=task", "label=Export Contacts")
        sel.click("id=Go")
        sel.wait_for_page_to_load("30000")
        sel.click("id=_qf_Select_next-top")
        sel.wait_for_page_to_load("30000")
        sel.click("link=Logout")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
