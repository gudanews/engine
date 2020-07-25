from builtins import object
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.remote.command import Command
from selenium.webdriver.common.action_chains import ActionChains


class Scripts(object):
    HOVER = (
        "var event = document.createEvent('MouseEvents');"
        "event.initEvent('mouseover', true, false);"
        "arguments[0].dispatchEvent(event);"
    )
    BLUR = "arguments[0].blur();"
    SCROLL = "arguments[0].scrollIntoView();"


PATCHED_BROWSERS = ["internet explorer"]


class WebElementMonkeyPatches(object):
    # pylint: disable=E1101
    WebElement._base_size = WebElement.size
    WebElement._base_location = WebElement.location

    @property
    def value(self):
        """This element's `value` property."""
        return self.get_attribute("value")

    @property
    def text(self):
        """This element's `value` property."""
        return self._base_text.strip()

    @property
    def title(self):
        """This element's `title` property."""
        return self.get_attribute("title")

    @property
    def size(self):
        """The size of the element."""
        if self._parent.capabilities["browserName"] == "MicrosoftEdge":
            height = float(self.value_of_css_property("height").split("px")[0])
            width = float(self.value_of_css_property("width").split("px")[0])
            return {"height": height,
                    "width": width}
        else:
            return self._base_size

    @property
    def location(self):
        """The location of the element"""
        if self._parent.capabilities["browserName"] == "Safari":
            return self.location_once_scrolled_into_view
        else:
            return self._base_location

    def set_text(self, text):
        """Sets text to the element"""
        self.clear()
        self.send_keys(text)

    def has_class(self, class_):
        """Returns True if element has class otherwise False"""
        return class_ in self.get_attribute("class")

    def hover(self):
        """Sets value to the element"""
        if self._parent.capabilities["browserName"] in PATCHED_BROWSERS:
            self._execute_script(Scripts.HOVER)
        else:
            ActionChains(self._parent).move_to_element(self).perform()
        return self

    def blur(self):
        """Triggers onBlur event to the element"""
        self._execute_script(Scripts.BLUR)

    def scroll_to(self):
        """Scrolls to the element"""
        return self._execute_script(Scripts.SCROLL)["value"]

    def get_automation_attribute(self, name):
        """Returns a data automation attribute"""
        return self.get_attribute("data-automation-%s" % name)

    def _execute_script(self, script):
        """Executes script on the element

        :param script: a javascript script
        """
        if self._w3c:
            command = Command.W3C_EXECUTE_SCRIPT
        else:
            command = Command.EXECUTE_SCRIPT
        return self._execute(
            command, {"script": script, "args": [self]}
        )

    WebElement._base_text = WebElement.text
    WebElement._execute_script = _execute_script
    WebElement.text = text
    WebElement.has_class = has_class
    WebElement.set_text = set_text
    WebElement.value = value
    WebElement.size = size
    WebElement.location = location
    WebElement.title = title
    WebElement.hover = hover
    WebElement.blur = blur
    WebElement.scroll_to = scroll_to
    WebElement.get_automation_attribute = get_automation_attribute


