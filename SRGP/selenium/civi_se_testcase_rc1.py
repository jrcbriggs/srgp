# -*- coding: utf-8 -*-
from selenium import selenium
import unittest, time, re

class civi_se_testcase_rc1(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "https://my.greenparty.org.uk/civicrm")
        self.selenium.start()
    
    def test_civi_se_testcase_rc1(self):
        sel = self.selenium
        sel.open("/user/login?destination=civicrm/report/instance/35%3Freset%3D1")
        sel.click("id=edit-submit")
        sel.wait_for_page_to_load("30000")
        sel.click("//ul[@id='civicrm-menu']/li[4]")
        sel.click("css=li.active > div.menu-item > a")
        sel.wait_for_page_to_load("30000")
        sel.click("id=_qf_GPDetail_submit_csv")
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
