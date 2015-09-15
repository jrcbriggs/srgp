# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class SearchMods(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://my.greenparty.org.uk/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_search_mods(self):
        driver = self.driver
        driver.get(self.base_url + "/")
        driver.find_element_by_id("edit-submit").click()
        driver.find_element_by_link_text("CiviCRM").click()
        driver.find_element_by_xpath("//ul[@id='civicrm-menu']/li[3]").click()
        driver.find_element_by_css_selector("li.active > div.menu-item > a").click()
        # ERROR: Caught exception [unknown command [sleep(2)]]
        driver.find_element_by_id("changeLog").click()
        driver.find_element_by_id("CIVICRM_QFID_1_log_date").click()
        Select(driver.find_element_by_id("log_date_relative")).select_by_visible_text("Last 7 days")
        driver.find_element_by_id("_qf_Advanced_refresh").click()
        driver.find_element_by_id("CIVICRM_QFID_ts_all_10").click()
        Select(driver.find_element_by_id("task")).select_by_visible_text("Export Contacts")
        driver.find_element_by_id("Go").click()
        driver.find_element_by_id("_qf_Select_next-bottom").click()
    
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
