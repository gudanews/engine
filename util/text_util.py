import sys
import os
from datetime import date, datetime, timedelta
from util.common import LoggedTestCase
import unittest
from util.config_util import Configure
from util import generate_random_alphanumeric_string, create_parent_folders, human_format
import logging
from googletrans import Translator
from util.webdriver_util import ChromeDriver
import time
from nltk.tokenize import sent_tokenize
from util.common import MetaClassSingleton


logger = logging.getLogger("Util.Text")

TODAY = date.today()

config = Configure()

WEBSITE_BASE_PATH = config.setting["website_path"]
TEXT_BASE_PATH = config.setting["text_path"]
TEXT_PATH = os.path.join(TEXT_BASE_PATH, str(TODAY.year), "%02d" % TODAY.month, "%02d" % TODAY.day)


MAX_ALLOWED_API_TEXT_LENGTH = 512
MAX_ALLOWED_WEB_TEXT_LENGTH = 4990
DELIMITER = "%%"

class Translation(metaclass=MetaClassSingleton):

    __metaclass__ = MetaClassSingleton

    def __init__(self, text=None, language=None):
        self.driver = None
        self.page = None
        self.last = None
        self.text = text
        self.language = language

    def set_text(self, text):
        self.text = text

    def set_language(self, language):
        self.language = language

    def translate(self, language=None):
        if len(self.text) < MAX_ALLOWED_API_TEXT_LENGTH:
            return self.translate_use_googletrans(language=language)
        return self.translate_use_website(language=language)

    def translate_use_googletrans(self, language=None): # Limitation of length and usage frequency
        language = language or self.language
        translator = Translator(service_urls=[
            "translate.google.com",
            "translate.google.co.uk",
            "translate.google.ca",
            "translate.google.com.au",
            "translate.google.co.in",
            "translate.google.co.jp"
        ])
        if self.last and (datetime.now() - self.last < timedelta(seconds=2)):
            time.sleep(2.0)
        self.last = datetime.now()
        if language:
            return translator.translate(self.text, dest=language).text
        return ""

    def translate_use_website(self, language=None):
        language = language or self.language
        self.driver.get(self.page.build_translation_url(language=language))
        paragraphs = self.split_into_paragraphs(self.text)
        translation = ""
        for p in paragraphs:
            time.sleep(2.0) if translation else None
            self.page.input.send_keys(p)
            translation += self.page.output
        return translation

    def split_into_paragraphs(self, text=None):
        text = text or self.text
        sentences = sent_tokenize(text)
        current_paragraph = ""
        paragraphs = []
        for s in sentences:
            if len(current_paragraph + s) <= MAX_ALLOWED_WEB_TEXT_LENGTH:
                current_paragraph += s
            else:
                paragraphs.append(current_paragraph)
                current_paragraph = s
        if current_paragraph:
            paragraphs.append(current_paragraph)
        return paragraphs


class GoogleTranslation(Translation):

    def __init__(self, text=None, language="zh-CN"):
        super(GoogleTranslation, self).__init__(text=text, language=language)

    def translate_use_website(self, language=None):
        from webpage.google import GoogleTranslationPage
        self.driver = ChromeDriver()
        self.page = GoogleTranslationPage(self.driver)
        return super(GoogleTranslation, self).translate_use_website(language=language)


class TextHelper:

    def __init__(self, text, path=None):
        self._text = text
        self._path = path
        self._translation_path = None

    @property
    def path(self):
        if not self._path:
            self._path = os.path.join(TEXT_PATH, generate_random_alphanumeric_string(24) + ".txt")
        elif not os.path.isabs(self._path):
            self._path = os.path.normpath(os.path.join(WEBSITE_BASE_PATH, self._path))
        return self._path

    @property
    def translation_path(self):
        if not self._translation_path:
            name, extension = os.path.splitext(self.path)
        if not self._path:
            self._path = os.path.join(TEXT_PATH, generate_random_alphanumeric_string(24) + ".txt")
        elif not os.path.isabs(self._path):
            self._path = os.path.normpath(os.path.join(WEBSITE_BASE_PATH, self._path))
        return self._path

    def save(self):
        try:
            create_parent_folders(self.path)
            with open(self.path, "w") as fh:
                fh.write(self._text)
            return True
        except:
            return False

    def translate(self, language="zh-CN"):
        tl = GoogleTranslation(self.text)
        self.text = tl.translate(language=language)


class TestCase(LoggedTestCase):

    def setUp(self):
        self.text = TextHelper(text=None)

    def test_save_text(self):
        self.text.save()
        self.assertTrue(os.path.exists(self.text.path))

    def test_translate_text(self):
        self.text.translate()
        self.assertTrue(os.path.exists(self.text.path))



if __name__ == '__main__':
    logger.info("Starting.")

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
    news = [
        "When you are President of the United States, your words matter. Not just to your own voters, not just to your own citizens, but to people in every corner of the planet. It's the inevitable reality of holding the most powerful office in the most powerful country on earth. Every other world leader, ally or enemy, is beneath you on the food chain and watches your every action.",
        "When you are President of the United States, your words matter. Not just to your own voters, not just to your own citizens, but to people in every corner of the planet. It's the inevitable reality of holding the most powerful office in the most powerful country on earth. Every other world leader, ally or enemy, is beneath you on the food chain and watches your every action.",
        "When you are President of the United States, your words matter. Not just to your own voters, not just to your own citizens, but to people in every corner of the planet. It's the inevitable reality of holding the most powerful office in the most powerful country on earth. Every other world leader, ally or enemy, is beneath you on the food chain and watches your every action.",
        "When you are President of the United States, your words matter. Not just to your own voters, not just to your own citizens, but to people in every corner of the planet. It's the inevitable reality of holding the most powerful office in the most powerful country on earth. Every other world leader, ally or enemy, is beneath you on the food chain and watches your every action."
    ]
    long = """
London (CNN)When you are President of the United States, your words matter. Not just to your own voters, not just to your own citizens, but to people in every corner of the planet.
It's the inevitable reality of holding the most powerful office in the most powerful country on earth. Every other world leader, ally or enemy, is beneath you on the food chain and watches your every action. They take cues from you; they seek your leadership and they attempt to find ways to exploit your weaknesses.
That's why Donald Trump's suggestions that the election should be delayed for the first time ever -- and his evidence-free claims that "2020 will be the most inaccurate and fraudulent" vote in history -- matter for reasons beyond the President's own political fate.
The primary focus is rightly on the democratic damage Trump's claims will wreak domestically. "His false claims that the election is being rigged against him are part of that strategy. They aren't true, but they will prime his base to reject the results," said Brian Klaas, assistant professor of global politics at University College London.
But experts say Trump's comments also send the wrong message at a time of growing concerns that leaders around the world are trying to exploit the coronavirus pandemic to erode the rule of law.
They also undercut the Trump administration's strident criticism of China in the wake of Beijing's move to strip semi-autonomous Hong Kong of some of its freedoms.
On the same day Trump floated the idea of delaying the US election, Secretary of State Mike Pompeo was demanding that Hong Kong hold its own legislative elections on time in September.
"They must be held," Pompeo said Thursday. "The people of Hong Kong deserve to have their voice represented by the elected officials that they choose in those elections." On Friday, Hong Kong's leader announced the elections would be delayed due to the growing coronavirus outbreak, but the opposition has questioned whether there are political motives at play.
"The problem isn't just Trump failing to endorse democratic process, it's that he uses the same strategies as undemocratic leaders to undermine the democratic process," said Nic Cheeseman, professor of democracy at the University of Birmingham.
Cheeseman says there is a "real threat in Trump sending out a message that he won't stand up for democracy" that less democratic global leaders will take this as a green light to lower their own standards.
"Leaders around the world really do look at the international climate to see what they can get away with. If you see that Trump is unwilling to promote democracy in other countries then backs that up by undermining democracy in his own country, the risk at play for you, say, rigging your own election is significantly lowered."
Trump's tweet is the latest in a long line of norm-smashing moves that experts say have damaged America's global reputation. During the course of his presidency, he has picked fights with friends and foes alike, threatened supranational institutions like NATO and the World Health Organization, and withdrawn from multilateral treaties like the Iran nuclear deal and Paris Climate Accord.
These unilateral actions also diminish America's diplomatic heft, according to Dr. Jennifer Cassidy, a diplomatic scholar at Oxford University.
"The truth is, that is where real soft power lies and he has done a lot of damage over his four years in office," Cassidy said. "And while America's allies might welcome a Biden presidency, seeing it as a return to something more normal, America's enemies may arguably be much slower to view the Trump presidency as an outlier. If Trump happened once, then why would Iran or China believe someone like him won't happen again?"
It's also impossible to ignore that this behavior has been on full display during the greatest crisis to face the world in decades.
"During a global pandemic, the world needs a leader — someone to help coordinate responses to a virus that knows no borders. Instead, Trump has spent much of his time hawking disproven medicines, tweeting conspiracy theories," said Klaas. "When the world looks to America to lead, they are finding a man who is singularly incapable of leading his country, let alone the world."
The consequences of this lack of global leadership from the most powerful man on the planet goes beyond his response to the health crisis. The Institute for Democracy published an open letter last month, in which more 500 former world leaders and Nobel Laureates warned that authoritarian regimes are using the pandemic to erode democracy.
Cheeseman believes that their cries would have packed more of a punch had they been arranged by the world's only hyperpower. "If America had marshalled democratic countries around the world to support democracy in the age of coronavirus, I think that could have been really significant. The signal that sends is we are watching you and we are on it."
Instead, the President has spent much of the pandemic as he has spent much of his presidency: picking fights and sowing division both at home and abroad.
But experts said the consequences of his latest attempt to undermine November's election could be more far-reaching than the damage wrought by the pandemic.
"If he loses, he seems to be signaling that he will happily try to burn American democratic institutions to the ground if he believes it will help save himself or help him save face," said Klaas.
Should this happen, it's hard to see how it benefits anyone in America other than the President, nor how it stops the international impression that the US is at serious risk of being on an inexorable slide towards becoming an unstable political basketcase.
And both America's allies and enemies will be acutely aware that the country could do it all again in four years' time, should someone Trumpier than Trump decide to run in 2024.


(CNN)In one of the most jolting moments in modern political history, former President Barack Obama reclaimed his political pulpit with a stark warning that his successor is a grave and imminent threat to American democracy and racial justice.
Then, even more remarkably, President Donald Trump went on television and proved him right, putting a foreboding shadow over an election that he is already seeking to cast as illegitimate in the eyes of millions of Americans.
The campaign between Trump and presumptive Democratic presidential nominee Joe Biden has mostly chugged along out of sight, obscured by a pandemic that has killed more than 150,000 Americans.
But the extraordinary interventions Thursday of two presidents, whose legacies will be forever entwined, suddenly underscored how this election, in the words of the quadrennial cliché, will actually be the most important one of our lifetimes.
Thursday brought a tableau of one president, liberated now that he is out of office, at the funeral of Rep. John Lewis, weaving the life of a national hero into a parable of America's long struggle to reach its promise. The current commander in chief, mired in crisis and desperate to cling to power, reached not for inspiration but for lies and disinformation to obscure the truth.
Obama's eulogy was not just his most public intervention in the 2020 campaign or his most passionate denunciation yet of a successor whose highest priority is eradicating Obama's achievements at home and abroad.
The speech, from the church where Martin Luther King Jr. once preached, also represented Obama's most raw, explicit and unrestrained unburdening about race on a prominent public stage of his entire political career.
In his 2008 campaign, he powerfully spoke about racial prejudice while seeking to heal national wounds -- and save his campaign when pressed about his association with the controversial Rev. Jeremiah Wright. And he shared an intimate part of his own experiences and spiritual self in explaining to the country why Black Americans were upset at the acquittal in the shooting of Trayvon Martin and in breaking into "Amazing Grace" while eulogizing parishioners at a Charleston, South Carolina, church hit by a mass shooting in 2015.
But Obama's speech for Lewis was urgent and in the tones of an activist, not a healer or the optimist who once declared there is "not a Black America" nor a "White America."
It brought into the open a clash between the nation's first Black president and the one who has made his name with a racist "birther" campaign against Obama and who is running for reelection wrapped in the Confederate flag and defending monuments to Civil War generals who fought to preserve slavery.
Obama also offered the most prominent accounting so far of the racial awakening following the death of George Floyd with a policeman's knee on his neck at a time when Trump is trying to incite a White backlash to the protests by painting the US as in the grip of a wave of leftist "fascism" and "terrorists."
While Obama's speech offered liberals the kind of inspiration they have lacked since he left office, his reappearance could also serve to embolden voters who saw in Trump a vehicle for their backlash against Obama's presidency. There are already complaints on conservative Twitter that Obama hijacked the funeral to mount a divisive political speech -- an ironic view considering Lewis' life story.
Meanwhile, Trump did not travel to honor Lewis, a man who he once decried as "talk, talk, talk, -- no action." But two other ex-presidents chose their side of history -- Republican George W. Bush and Democrat Bill Clinton also spoke at the service.
The tweet that echoed 'round the world

The day began with Trump floating the idea of delaying the election and recycling the lie that mail-in voting is prone to massive fraud -- in a tweet that almost everyone who has followed his presidency had expected.
Obama, in eulogizing Lewis, a civil rights hero who was beaten to the edge of death while securing voting rights for African Americans, then placed Trump directly in the lineage of old Deep South bigots, a stunningly explicit move that branded Trump's race-baiting campaign a direct threat to the republic.
"Bull Connor may be gone. But today we witness with our own eyes police officers kneeling on the necks of Black Americans," Obama said, in remarks that belied the caution on race he had mostly observed while in office and identified synergy between the civil rights era and the Black Lives Matter movement.
"George Wallace may be gone. But we can witness our federal government sending agents to use tear gas and batons against peaceful demonstrators," Obama said, in a clear reference to Trump's "law and order" alarmism.
"We may no longer have to guess the number of jellybeans in a jar in order to cast a ballot. But even as we sit here, there are those in power that are doing their darnedest to discourage people from voting -- by closing polling locations, and targeting minorities and students with restrictive ID laws, and attacking our voting rights with surgical precision, even undermining the Postal Service in the run-up to an election that is going to be dependent on mailed-in ballots so people don't get sick."
In what may turn out to be the most politically significant line of his eulogy for Democrats, Obama called for Senate revisions to end partisan gerrymandering and to make sure that everybody's vote finally counts.
"And if all this takes eliminating the filibuster -- another Jim Crow relic -- in order to secure the God-given rights of every American, then that's what we should do."
'The ballots are all missing'

Less than three hours later, Trump walked into the White House briefing room and again decried mail-in ballots. He also reversed himself and told reporters he didn't want to delay the election.
"But I don't want to have to wait three months to find out the ballots are all missing," he said. "Smart people know it," Trump said. "Stupid people may not know it. Some people don't want to talk about it."
The President's earlier tweet was decried by many Republican lawmakers who understand that Congress, not the President, sets election days.
The tweet was a clear attempt to limit attention to appalling new data Thursday that showed a stunning 32.9% annualized contraction in the economy in the second quarter amid coronavirus shutdowns -- the worst slump in history.
But that does not mean that the President's comments on alleged fraud were any less pernicious. There is no credible evidence that mail-in voting is rife with corruption. But his team is already readying a sheaf of legal challenges that critics say are meant to cancel out millions of votes in an election that, according to the polls, the President is currently losing badly.
That he should choose to escalate his claims to yet another on the morning of the funeral of the Georgia Democrat who dedicated his life to expanding the franchise was richly ironic.
The President's intention is not hard to gauge. He has been trying to create a face-saving option for himself should he lose in his effort for a second term. But his tactics risk causing deep and lasting damage to the American political system. Trust in elections is the essential foundation of any democracy. An election that he lost but that is viewed as illegitimate by his followers could also energize the conservative base and ruin a new president's hopes of restoring national unity and a successful administration.
Still, it is also possible that Trump's rhetoric on Thursday -- which again underscored the authoritarian impulses evident throughout his time in power -- could further drive away more moderate unaffiliated voters.
'We do not walk alone'

Thursday's extraordinary political theater played out against a backdrop of death and sickness. More than 151,000 Americans have died in a pandemic that Trump first ignored, then politicized and mismanaged. In his White House appearance, the President gloated about outbreaks of Covid-19 in foreign countries that did a far better job than he did in suppressing the first wave of infection.
It was another day when Trump's approach differed starkly from the decorum and gravitas demonstrated by the ex-presidents.
"The virus was said to be under control, but new cases have risen very significantly once again. So when you think somebody's doing well, sometimes you have to hold your decision on that. You have to hold your statements," Trump said.
"Since the beginning of June, daily new cases have increased by a factor of 14 times in Israel, 35 times -- that's 35 times -- in Japan and nearly 30 times in Australia, just to name a few," he added.
The President's comments were shockingly misleading. The nations he mentioned had far lower incidences of the disease than the US and took far more proactive steps to suppress the curve of infections.
The United States, despite having just 4% of the world's population, accounts for around 25% of global coronavirus infections and has the most deaths.
As the daily death toll once more raced toward 1,000 on Thursday, Trump again made highly misleading claims about a quick rebound and a fast decline in cases in Sun Belt states that are enduring a terrible crisis.
Obama, meanwhile, argued that the lesson of Lewis' life was that politics was the work of overcoming complacency and fear.
"That's where real courage comes from. Not from turning on each other, but by turning towards one another. Not by sowing hatred and division, but by spreading love and truth. Not by avoiding our responsibilities to create a better America and a better world, but by embracing those responsibilities with joy and perseverance and discovering that in our beloved community, we do not walk alone," he said.
    """
    # t = GoogleTranslation(text=long)
    # logger.info(t.translate_use_website())
    t = GoogleTranslation()
    for i in range(20):
        for n in news:
            t.set_text(n)
            logger.info(t.translate_use_googletrans())
    logger.info("Completed.")

