from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from googletrans import Translator


def translate_to_chinese(text):
    translator = Translator()
    return translator.translate(text, dest='chinese (simplified)').text


import time

news = [
    "World Bank says ready to mobilize financing for Lebanon blast recovery",
    "Rand Paul on COVID relief spending: $5 trillion in 5 months could cost Republicans the ...",
    "Fact check: Trump makes at least 20 false claims in Fox & Friends interview",
    "Argentine industrial output falls 6.6% in June, less than feared",
    "Wonderful world of Disney earnings surprise boosts Wall Street",
    "Why they broke into their own gym defying Covid-19 rules",
    "Analysis: John Lewis' legacy at work as WNBA team protest a US senator",
    "Tel Aviv lights up its city hall with the Lebanese flag",
    "Former Colombian President Uribe tests positive for coronavirus",
    "U.S. wants to see 'untrusted' Chinese apps removed from U.S. app stores, Pompeo says",
    "Zynga raises full-year bookings forecast, buys another Turkish game-maker",
    "Ex-Atlanta cop accused of killing Rayshard Brooks sues city, mayor over firing",
    "Former US attorney says he doesn't buy Yates' testimony Comey went 'rogue' in Flynn ...",
    "Gambia imposes curfew as coronavirus cases surge 60% in a week",
    "Susan Rice has this to say about her Trump-supporting son",
]

from util.webdriver_util import ChromeDriver

MAX_ALLOWED_TEXT_LENGTH = 500


class _Translate:
    def __init__(self, driver=None, text=None, translate_source_url=None):
        self.text = text
        self.translate_source_url = translate_source_url
        self.driver = driver

    def _fetch_translation_from_website(self, text):
        self.driver.get("https://translate.google.com/#view=home&op=translate&sl=en&tl=zh-CN")  # zh-Hant
        self.driver.find_element_by_css_selector('textarea[id=source]').send_keys(text)
        WebDriverWait(driver, 100).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "span.tlid-translation.translation"))
        )
        tx = self.driver.find_element_by_css_selector('span.tlid-translation.translation').text
        return tx

    def split_large_text_into_multiple_chunks(self, text):
        li = text.split('.')
        output = []
        length = 0
        batch = ''
        for sentence in li:
            print(sentence)
            if length + len(sentence) < MAX_ALLOWED_TEXT_LENGTH:
                length += len(sentence)
                batch += sentence
                batch += '. '
            else:
                print('else')
                output.append(batch)
                batch = ''
                length = 0
        print(output, len(output))
        return output

    def translate(self):
        output = ''
        if len(self.text) < MAX_ALLOWED_TEXT_LENGTH:
            return self._fetch_translation_from_website(self.text)
        else:
            #print(self.split_large_text_into_multiple_chunks(self.text))
            #print(self.text)
            for i in self.split_large_text_into_multiple_chunks(self.text):
                #print(i)
                output += self._fetch_translation_from_website(i)
            return output


class TranslateGoogle(_Translate):
    def __init__(self):
        super(TranslateGoogle, self).__init__()


if __name__ == '__main__':
    start = time.time()
    driver = ChromeDriver()
    long = """Washington (CNN)President Donald Trump was abruptly evacuated from the White House briefing room by security on Monday after shots were fired outside the building.Trump returned to the briefing room minutes later, confirming a shooting."There was a shooting outside of the White House and it seems to be very well under control. I'd like to thank the Secret Service for doing their always quick and very effective work," Trump said when he returned.After he returned to the podium, US Secret Service tweeted: "The Secret Service can confirm there has been an officer involved shooting at 17th Street and Pennsylvania Ave. Law enforcement officials are on the scene."A senior administration official said there was an active shooter near the White House and that shooter is in custody.The incident happened just outside of the White House grounds close to Lafayette Square, the official said.Trump had been midsentence during the first attempt at a briefing when security came into the room and asked him to leave the area."Excuse me?" Trump asked when the security approached."Step outside," the agent said."""
    t = _Translate(driver, text=long)
    # print(t.split(long))
    # print(len(t.split(long)))
    print(t.translate())
    print('done')
    time.sleep(1000)
    # print(t.translate())
    # for i in range(100):
    #    t = Translate(driver=driver, text='this is a book? that is a tree!')
    #    print(t.translate())
    # print(time.time() - start)
