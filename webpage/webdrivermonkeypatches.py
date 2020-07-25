from builtins import object
import time
import signal
from ssl import SSLError
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.webdriver.remote.remote_connection import RemoteConnection
from selenium.webdriver.remote.command import Command
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException


TIMEOUT = 150
COMMANDS = (
    Command.FIND_ELEMENT,
    Command.FIND_ELEMENTS
)


class JavascriptError(Exception):
    pass


class RenderingNotFinishedError(Exception):
    pass


class StartSessionTimeout(Exception):
    pass


RemoteConnection.set_timeout(TIMEOUT)


class WebDriverMonkeyPatches(object):
    # pylint: disable=E1101
    RemoteWebDriver.WAIT_UNTIL_PAGE_IS_LOADED = True
    RemoteWebDriver._base_execute2 = RemoteWebDriver.execute
    RemoteWebDriver._start_session = RemoteWebDriver.start_session
    RemoteWebDriver._UI_PAGE_LOAD_TIMEOUT = TIMEOUT

    def set_ui_page_load_timeout(self, timeout):
        self._UI_PAGE_LOAD_TIMEOUT = timeout

    def execute(self, driver_command, params=None):
        if driver_command in COMMANDS:
            end_time = time.time() + self._UI_PAGE_LOAD_TIMEOUT
            while end_time > time.time():
                if not self.is_page_loading():
                    break
                time.sleep(1)
            else:
                locator = "head > title"
                title = self._find_elements(locator)
                raise RenderingNotFinishedError(
                    "Render is not finished within {0} secs on {1}".format(
                        self._UI_PAGE_LOAD_TIMEOUT, title[0].get_attribute("text")))
        return self._base_execute2(driver_command, params)

    def is_page_loading(self):
        """
        returns whether some spinners displayed on the page
        """
        if self.WAIT_UNTIL_PAGE_IS_LOADED:
            spinners_locators = [
                ".loading.plat-loading:not([style='display: none;'])",
                ".loading-area.isLoading",
                ".filter-spinner:not([style='display: none;'])",
                ".load-more-spinner:not([style='display: none;'])",
                ".busy",
                "button.validating",
                ".spinner-component.shown",
                ".vb-filter-spinner:not([style='display: none;'])",
                "div:not([class]) > .opa-spinner-container",
                "[data-automation-id='wd-LoadingPanel']",
                ".spinner-component:not([style*='display: none'])",
                "div[role='alert'][aria-busy='true']",
                "[data-automation-id='vizLoadingMessage']",
                "[data-automation-id='dataSourceFieldListItemLoader']",
                ":not([data-automation-id='catalogTableStatusSpinnerContainer'])"
                ":not([data-automation-id='tableActivityStatusSpinnerContainer'])"
                ":not([data-automation-id='tableActivitiesStatusIconContainer']) > [data-automation-id='spinner']",
            ]
            locator = ",".join(spinners_locators)
            try:
                RemoteConnection.set_timeout(5)
                spinners = self._find_elements(locator)
                return any([spinner.is_displayed() for spinner in spinners])
            except (StaleElementReferenceException, SSLError, NoSuchElementException):
                return True
            finally:
                RemoteConnection.set_timeout(TIMEOUT)

    def start_session(self, capabilities, browser_profile=None):
        """
        wraps original start session method to fix remote connection issues
        """

        def handler(s, f):
            raise StartSessionTimeout()

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(30)
        self._start_session(capabilities, None)
        signal.alarm(0)

    def wait_until_page_is_loaded(self, wait=True):
        """
        enables mechanism for page loading if True otherwise disables
        """
        self.WAIT_UNTIL_PAGE_IS_LOADED = wait

    def set_download_directory(self, path):
        """
        sets download dir for chromium
        """
        return self._base_execute2(
            "sendCommand",
            {"cmd": "Page.setDownloadBehavior",
             "params": {"behavior": "allow", "downloadPath": path}}
        )

    def _find_elements(self, locator):
        """
        finds elements without wait
        """
        return self._base_execute2(
            Command.FIND_ELEMENTS,
            {"using": By.CSS_SELECTOR, "value": locator})["value"]

    RemoteWebDriver.execute = execute
    RemoteWebDriver.start_session = start_session
    RemoteWebDriver.wait_until_page_is_loaded = wait_until_page_is_loaded
    RemoteWebDriver.set_download_directory = set_download_directory
    RemoteWebDriver.is_page_loading = is_page_loading
    RemoteWebDriver._find_elements = _find_elements
    RemoteWebDriver.set_ui_page_load_timeout = set_ui_page_load_timeout

