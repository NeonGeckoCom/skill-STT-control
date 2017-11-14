from adapt.intent import IntentBuilder
import datetime
from mycroft.skills.core import MycroftSkill
from mycroft.util.log import getLogger
from mycroft.configuration import ConfigurationManager
from mycroft.util import (
    create_signal,
    check_for_signal
)
from mycroft.messagebus.message import Message

__author__ = 'neongecko.com inc'
globdate = str(datetime.date.today())
config = ConfigurationManager.get()

LOGGER = getLogger(__name__)


class CPIControlSTTSkill(MycroftSkill):
    """
            Class name: CPIControlSTTSkill

            Purpose: Creates the "CPIControlSTTSkill" skill, to control STT
            processing. This enables switching the STT processing between local
            pocketsphinx or internet. Utterance: 'Start local speech' or
            'Begin internet processing'.


            Note: This skill would not proceed without the clear confirmation
             of the command from the user by asking

                "Should I switch to local speech processing?"

                and expecting a positive answer.


            Supporting Files:
                 skill-STT-control/vocab/en-us/ConfirmNo.voc
                 skill-STT-control/vocab/en-us/ConfirmYes.voc
                 skill-STT-control/vocab/en-us/STT1.voc
                 skill-STT-control/vocab/en-us/InternetSTT2.voc
                 skill-STT-control/vocab/en-us/STT3.voc
                 skill-STT-control/vocab/en-us/LocalSTT2.voc

                 skill-STT-control/test/intent/CPIConfirmIntentNo.intent.json
                 skill-STT-control/test/intent/CPIConfirmIntentYes.intent.json
                 skill-STT-control/test/intent/CPIDoInternetSTT.intent.json
                 skill-STT-control/test/intent/CPIDoLocalSTT.intent.json
        """

    def __init__(self):
        # name the new class:
        super(CPIControlSTTSkill, self)\
            .__init__(name="CPIControlSTTSkill")

    def initialize(self):
        # name intent and build it:
        internet_stt = IntentBuilder("UseMycroftSTT") \
            .require("STT1") \
            .require("InternetSTT2") \
            .require("STT3") \
            .build()
        # register:
        self.register_intent(internet_stt, self.handle_internet_stt)

        local_stt = IntentBuilder("UseLocalSTT") \
            .require("STT1") \
            .require("LocalSTT2") \
            .require("STT3") \
            .build()
        # register:
        self.register_intent(local_stt, self.handle_local_stt)

        self.confirm_yes = IntentBuilder("ConfirmYes") \
            .require("ConfirmYes") \
            .build()
        # register:
        self.register_intent(self.confirm_yes, self.handle_confirm_yes)

        self.confirm_no = IntentBuilder("ConfirmNo") \
            .require("ConfirmNo") \
            .build()
        # register:
        self.register_intent(self.confirm_no, self.handle_confirm_no)

        self.disable_intent('ConfirmYes')
        self.disable_intent('ConfirmNo')

    def handle_internet_stt(self, message):

        self.speak("Should I switch to internet speech processing?", True)

        self.enable_intent('ConfirmYes')
        self.enable_intent('ConfirmNo')

        create_signal('InternetSTT')
        create_signal('WaitingToConfirm')

    def handle_local_stt(self, message):

        self.speak("Should I switch to local speech processing?", True)

        self.enable_intent('ConfirmYes')
        self.enable_intent('ConfirmNo')

        create_signal('LocalSTT')
        create_signal('WaitingToConfirm')

    def handle_confirm_yes(self, message):

        if check_for_signal("InternetSTT", 0):
            check_for_signal('UseLocalSTT', 0)
            create_signal('UseMycroftSTT')
            self.speak("Switching to internet speech to text processing.",
                       False)
            self.emitter.emit(Message('recognizer_loop:restart'))

        elif check_for_signal("LocalSTT", 0):
            check_for_signal('UseMycroftSTT', 0)
            create_signal('UseLocalSTT')
            self.speak("Switching to local speech to text processing.", False)
            self.emitter.emit(Message('recognizer_loop:restart'))

        self.disable_intent('ConfirmYes')
        self.disable_intent('ConfirmNo')

    def handle_confirm_no(self, message):
        self.speak("O K. Not doing anything.", False)

        self.disable_intent('ConfirmYes')
        self.disable_intent('ConfirmNo')

    def stop(self):
        pass


def create_skill():
    return CPIControlSTTSkill()
