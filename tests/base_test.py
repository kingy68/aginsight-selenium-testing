import os
import unittest
import sys
import new
import time
from selenium import webdriver
from sauceclient import SauceClient
from PageObjects import Page
from UIComponentObjects import Tour, Footer, Header, Highlights, LeftPanel, RightPanel, CommodityDrawer

'''All test modules inherit from the BaseTest class.'''

# Specify which OS/Browser combinations to test on
browsers = [{
    "platform": "Windows 7",
    "browserName": "chrome",
    "version": "51.0",
    "screenResolution": "1920x1200",
    "recordVideo": False,
    "recordScreenshots": True,
    "captureHTML": False,
    "videoUploadOnPass": False,
    "recordLogs": True
}]


# This decorator is required to iterate over browsers
def on_platforms(platforms):
    def decorator(base_class):
        module = sys.modules[base_class.__module__].__dict__
        for i, platform in enumerate(platforms):
            d = dict(base_class.__dict__)
            d['desired_capabilities'] = platform
            name = "%s_%s" % (base_class.__name__, i + 1)
            module[name] = new.classobj(name, (base_class,), d)

    return decorator


class BaseTest(unittest.TestCase):
    username = None
    access_key = None
    selenium_port = None
    selenium_host = None
    upload = True
    tunnel_id = None
    build_tag = None

    # setUp runs before each test case
    def setUp(self):
        self.desired_capabilities['name'] = self.id()

        if BaseTest.tunnel_id:
            self.desired_capabilities['tunnel-identifier'] = BaseTest.tunnel_id
        if BaseTest.build_tag:
            self.desired_capabilities['build'] = BaseTest.build_tag

        self.driver = webdriver.Remote(
                command_executor="http://%s:%s@%s:%s/wd/hub" %
                                 (BaseTest.username,
                                  BaseTest.access_key,
                                  BaseTest.selenium_host,
                                  BaseTest.selenium_port),
                desired_capabilities=self.desired_capabilities)

        # Open the website in the BaseTest, this can now be used in multiple tests, without
        # having to reload the page. Otherwise, individual tests can still reload the page
        # if they require it.
        time.sleep(2)
        self.driver.get('http://www.aginsight.sa.gov.au')

        time.sleep(2)

        self.splash = Page.SplashPage(self.driver)
        self.tour = Tour.Tour(self.driver)
        self.footer = Footer.Footer(self.driver)
        self.header = Header.Header(self.driver)
        self.highlights = Highlights.Highlights(self.driver)
        self.leftpanel = LeftPanel.LeftPanel(self.driver)
        self.rightpanel = RightPanel.RightPanel(self.driver)
        self.comdrawer = CommodityDrawer.CommodityDrawer(self.driver)

    # tearDown runs after each test case
    def tearDown(self):
        self.driver.quit()
        sauce_client = SauceClient(BaseTest.username, BaseTest.access_key)
        status = (sys.exc_info() == (None, None, None))
        sauce_client.jobs.update_job(self.driver.session_id, passed=status)
        # test_name = "%s_%s" % (type(self).__name__, self.__name__)
        # with(open(test_name + '.testlog', 'w')) as outfile:
        #     outfile.write("SauceOnDemandSessionID=%s job-name=%s\n" % (self.driver.session_id, test_name))

    @classmethod
    def setup_class(cls):
        cls.build_tag = os.environ.get('BUILD_TAG', None)
        cls.tunnel_id = os.environ.get('TUNNEL_IDENTIFIER', None)
        cls.username = os.environ.get('SAUCE_USERNAME', None)
        cls.access_key = os.environ.get('SAUCE_ACCESS_KEY', None)

        cls.selenium_port = os.environ.get("SELENIUM_PORT", None)
        if cls.selenium_port:
            cls.selenium_host = "localhost"
        else:
            cls.selenium_host = "ondemand.saucelabs.com"
            cls.selenium_port = "80"
