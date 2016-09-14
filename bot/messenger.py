import datetime
import logging
import random
from bs4 import BeautifulSoup
import re
import urllib2

def getMenu():

    response = urllib2.urlopen('http://www.metsense.be/nl/onze-uitbatingen#bedrijfsrestaurants')
    html = response.read()
    soup = BeautifulSoup(html,"html.parser")
    digipolis = soup.find("h3",string="Digipolis").find_next(class_="restaurant-menu")
    return digipolis
def getSearchParameter():
    dayOfWeek = datetime.datetime.today().weekday()
    if dayOfWeek == 0:
        search = "Maandag"
    elif dayOfWeek == 1:
        search = "Dinsdag"
    elif dayOfWeek == 2:
        search = "Woensdag"
    elif dayOfWeek == 3:
        search = "Donderdag"
    elif dayOfWeek == 4:
        search = "Vrijdag"
    else:
        search = False
    return search

logger = logging.getLogger(__name__)


class Messenger(object):
    def __init__(self, slack_clients):
        self.clients = slack_clients

    def send_message(self, channel_id, msg):
        # in the case of Group and Private channels, RTM channel payload is a complex dictionary
        if isinstance(channel_id, dict):
            channel_id = channel_id['id']
        logger.debug('Sending msg: {} to channel: {}'.format(msg, channel_id))
        channel = self.clients.rtm.server.channels.find(channel_id)
        channel.send_message("{}".format(msg.encode('ascii', 'ignore')))

    def write_help_message(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = '{}\n{}\n{}\n{}'.format(
            "Hallo. Ik ben de LPA-slack-robot.  Ik *_antwoord_* op volgende vragen:",
            "> `<@" + bot_uid + "> menu` - Ik zoek op welke soep er vandaag in Digipolis wordt geserveerd",
            "> `<@" + bot_uid + "> suggestie` - Ik zoek op wat het broodje van de week is",
            "> `hi <@" + bot_uid + ">` - I'll respond with a randomized greeting mentioning your user. :wave:",
            "> `<@" + bot_uid + "> joke` - I'll tell you one of my finest jokes, with a typing pause for effect. :laughing:",
            "> `<@" + bot_uid + "> attachment` - I'll demo a post with an attachment using the Web API. :paperclip:")
        self.send_message(channel_id, txt)

    def write_greeting(self, channel_id, user_id):
        greetings = ['Hi', 'Hello', 'Nice to meet you', 'Howdy', 'Salutations']
        txt = '{}, <@{}>!'.format(random.choice(greetings), user_id)
        self.send_message(channel_id, txt)

    def write_prompt(self, channel_id):
        bot_uid = self.clients.bot_user_id()
        txt = "I'm sorry, I didn't quite understand... Can I help you? (e.g. `<@" + bot_uid + "> help`)"
        self.send_message(channel_id, txt)

    def write_joke(self, channel_id):
        question = "Why did the python cross the road?"
        self.send_message(channel_id, question)
        self.clients.send_user_typing_pause(channel_id)
        answer = "To eat the chicken on the other side! :laughing:"
        self.send_message(channel_id, answer)


    def write_error(self, channel_id, err_msg):
        txt = ":face_with_head_bandage: my maker didn't handle this error very well:\n>```{}```".format(err_msg)
        self.send_message(channel_id, txt)

    def demo_attachment(self, channel_id):
        txt = "Beep Beep Boop is a ridiculously simple hosting platform for your Slackbots."
        attachment = {
            "pretext": "We bring bots to life. :sunglasses: :thumbsup:",
            "title": "Host, deploy and share your bot in seconds.",
            "title_link": "https://beepboophq.com/",
            "text": txt,
            "fallback": txt,
            "image_url": "https://storage.googleapis.com/beepboophq/_assets/bot-1.22f6fb.png",
            "color": "#7CD197",
        }
        self.clients.web.chat.post_message(channel_id, txt, attachments=[attachment], as_user='true')

    def send_menu(self, channel_id):
        search = getSearchParameter
        if search != False:

            question = "Het menu bij Digipolis is vandaag:"
            self.send_message(channel_id, question)
            self.clients.send_user_typing_pause(channel_id)
            digipolis = getMenu()
            for string in  digipolis.find(string=re.compile(search)).find_next("td").stripped_strings:
                answer = string
            self.send_message(channel_id, answer)
        else:
            answer = "Sorry, Niets in de refter vandaag"
            self.send_message(channel_id, answer)
    def send_suggestie(self, channel_id):
        question = "Ik kijk even na wat de suggestie deze week is."
        self.send_message(channel_id, question)
        self.clients.send_user_typing_pause(channel_id)
        digipolis = getMenu()

        for string in  digipolis.find(string=re.compile("Suggestie")).find_next("td").stripped_strings:
            answer = string
        self.send_message(channel_id, answer)
