from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants


class MyWaitPage1(WaitPage):

    def after_all_players_arrive(self):
        self.subsession.update_market()


class NewPeriod(Page):
    pass


class Choice(Page):

    form_model = 'player'
    form_fields = ['choice']

    def is_displayed(self):
        return self.player.wait == 0


class MyWaitPage2(WaitPage):

    def after_all_players_arrive(self):
        self.subsession.clear_market()


class ChoiceOutcome(Page):

    def is_displayed(self):
        return self.player.wait == 0


class FinalPage(Page):
    def is_displayed(self):
        return self.round_number == Constants.num_rounds


page_sequence = [
    MyWaitPage1,
    NewPeriod,
    Choice,
    MyWaitPage2,
    ChoiceOutcome,
    FinalPage
]
