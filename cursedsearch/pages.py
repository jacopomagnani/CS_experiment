from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import random

class MyWaitPage1(WaitPage):

    def after_all_players_arrive(self):
        self.subsession.update_market()


class NewPeriod(Page):

    timeout_seconds = 20


class Choice(Page):

    timeout_seconds = 20

    form_model = 'player'
    form_fields = ['choice']

    def is_displayed(self):
        return self.player.wait == 0

    def before_next_page(self):
        if self.timeout_happened:
            self.player.late = 1
            flip = random.randint(0,1)
            if flip ==0:
                self.player.choice = False
            else:
                self.player.choice = True


class MyWaitPage2(WaitPage):

    def after_all_players_arrive(self):
        self.subsession.clear_market()


class ChoiceOutcome(Page):

    timeout_seconds = 10

    def is_displayed(self):
        return self.player.wait == 0 and self.player.choice == 1


class LastPeriod(Page):

    timeout_seconds = 20

    def is_displayed(self):
        return self.round_number in Constants.termination_rounds

    def vars_for_template(self):
        return {'market_payoff': sum([p.payoff for p in self.player.in_current_market()])}


class FinalPage(Page):

    def is_displayed(self):
        return self.round_number == Constants.num_rounds


page_sequence = [
    MyWaitPage1,
    NewPeriod,
    Choice,
    MyWaitPage2,
    ChoiceOutcome,
    LastPeriod,
    FinalPage
]
