# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class CiviSeTestcaseWd1(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://my.greenparty.org.uk/civicrm"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_civi_se_testcase_wd1(self):
        driver = self.driver
        driver.get(self.base_url + "/user/login?destination=civicrm/report/instance/35%3Freset%3D1")
        driver.find_element_by_id("edit-submit").click()
        driver.find_element_by_xpath("//ul[@id='civicrm-menu']/li[4]").click()
        driver.find_element_by_css_selector("li.active > div.menu-item > a").click()
        driver.find_element_by_id("_qf_GPDetail_submit_csv").click()
        driver.find_element_by_xpath("//ul[@id='civicrm-menu']/li[3]").click()
        driver.find_element_by_css_selector("div.menu-item > a").click()
        driver.find_element_by_id("_qf_Basic_refresh").click()
        driver.find_element_by_id("CIVICRM_QFID_ts_all_4").click()
        Select(driver.find_element_by_id("task")).select_by_visible_text("Export Contacts")
        driver.find_element_by_id("Go").click()
        driver.find_element_by_id("_qf_Select_next-top").click()
        driver.find_element_by_link_text("Logout").click()
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
