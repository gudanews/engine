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
            #print(sentence)
            if length + len(sentence + '. ') < MAX_ALLOWED_TEXT_LENGTH:
                length += len(sentence)
                batch += sentence
                batch += '. '
            else:
                output.append(batch)
                batch = sentence + '. '
                length = len(sentence + '. ')
        output.append(batch)
        #print(output, len(output))
        return output

    def translate(self):
        output = ''
        if len(self.text) < MAX_ALLOWED_TEXT_LENGTH:
            return self._fetch_translation_from_website(self.text)
        else:
            for i in self.split_large_text_into_multiple_chunks(self.text):
                # print(i)
                output += self._fetch_translation_from_website(i)
            return output


class TranslateGoogle(_Translate):
    def __init__(self):
        super(TranslateGoogle, self).__init__()


if __name__ == '__main__':
    start = time.time()
    driver = ChromeDriver()
    long = """(CNN)As US leaders work to control the spread of coronavirus, researchers across the country -- and globe -- are working to answer the mysteries that remain around infections.One of those mysteries: why the experience can be so different from person to person. One expert says the answer may involve looking at previous vaccines individuals have had."When we looked in the setting of Covid disease, we found that people who had prior vaccinations with a variety of vaccines -- for pneumococcus, influenza, hepatitis and others -- appeared to have a lower risk of getting Covid disease," Dr. Andrew Badley, an infectious disease specialist at Mayo Clinic told CNN's Anderson Cooper on Monday night.It's what immunologists call immune training: how your immune system creates an effective response to fight off infections, Badley says."A good analogy is to think of your immune system as being a muscle," he said. "The more you exercise that muscle, the stronger it will be when you need it."There's been no definitive evidence of any other vaccines boosting immunity against Covid-19. But some researchers have suggested it's possible.Do some people have protection against the coronavirus?Do some people have protection against the coronavirus?In June, a team of researchers in the US proposed giving a booster dose of the measles, mumps and rubella (MMR) vaccine to people to see if it helps prevent the most severe effects of coronavirus infections. And last month, researchers found that countries where many people have been given the tuberculosis vaccine Bacillus Calmette-Guerin (BCG) had less mortality from coronavirus, a finding that fits with other research suggesting the vaccine can boost people's immunity in general."""
    t = _Translate(driver=driver,text=long)
    # print(t.split(long))
    # print(len(t.split(long)))
    print(t.translate())
    #t.split_large_text_into_multiple_chunks(long)
    print('done')
    time.sleep(1000)
    # print(t.translate())
    # for i in range(100):
    #    t = Translate(driver=driver, text='this is a book? that is a tree!')
    #    print(t.translate())
    # print(time.time() - start)
