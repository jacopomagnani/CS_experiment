from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

import random
import numpy



author = 'Jacopo Magnani'

doc = """
Search and Matching Market with noisy signals
"""


class Constants(BaseConstants):
    name_in_url = 'cursedsearch'
    players_per_group = None
    num_rounds = 52
    num_markets = 9
    restart_rounds = [1, 9, 13, 21, 23, 35, 42, 44, 50]
    termination_rounds = [8, 12, 20, 22, 34, 41, 43, 49, 52]
    types = [5 , 10, 100]
    signals = ["blue", "yellow", "red"]
    pL = [2/3, 1/3, 0]
    pM = [1/8, 3/4, 1/8]
    pH = [0, 1/3, 2/3]


class Subsession(BaseSubsession):

    market_number = models.IntegerField()
    period = models.IntegerField()

    def update_market(self):

# set market number, side, type and wait status
        #first, for round 1
        if self.round_number == 1:
            # set market number, and session vars
            self.market_number = 1
            self.period = 1
            self.session.vars['nplayers'] = len(self.get_players())
            self.session.vars['waitlistlength'] = int(len(self.get_players())/6-1)
            # assign side
            side_list = numpy.random.permutation([1, 2] * int(self.session.vars['nplayers']/2))
            k = 0
            for p in self.get_players():
                p.side = side_list[k]
                k = k+1
            side1_players = []
            side2_players = []
            for p in self.get_players():
                pid = p.id_in_group
                if p.side == 1:
                    side1_players.append(pid)
                else:
                    side2_players.append(pid)
            # assign type
            for s in [1,2]:
                k = 0
                type_list = numpy.random.permutation(Constants.types*int(self.session.vars['nplayers']/6))
                for p in self.get_players():
                    if p.side == s:
                        p.type = type_list[k]
                        k = k+1
            # assign wait status
            if self.session.vars['nplayers'] == 6:
                for p in self.get_players():
                    p.wait = 0
            elif self.session.vars['nplayers'] == 12:
                for s in [1, 2]:
                    for t in Constants.types:
                        k = 0
                        wait_list = numpy.random.permutation([0, 1])
                        for p in self.get_players():
                            if p.side == s and p.type == t:
                                p.wait = wait_list[k]
                                k = k + 1
            elif self.session.vars['nplayers'] == 24:
                for s in [1,2]:
                    for t in Constants.types:
                        k = 0
                        wait_list = numpy.random.permutation([0, 1, 2, 3])
                        for p in self.get_players():
                            if p.side == s and p.type == t:
                                p.wait = wait_list[k]
                                k = k + 1
        # then for any restart round >1
        if self.round_number in Constants.restart_rounds and self.round_number > 1:
            # update market number
            self.market_number = self.in_round(self.round_number-1).market_number + 1
            self.period = 1
            # keep side
            for p in self.get_players():
                p.side = p.in_round(self.round_number - 1).side
            # reassign type
            for s in [1,2]:
                k = 0
                type_list = numpy.random.permutation(Constants.types*int(self.session.vars['nplayers']/6))
                for p in self.get_players():
                    if p.side == s:
                        p.type = type_list[k]
                        k = k+1
            # reassign wait status
            if self.session.vars['nplayers'] == 6:
                for p in self.get_players():
                    p.wait = 0
            elif self.session.vars['nplayers'] == 12:
                for s in [1, 2]:
                    for t in Constants.types:
                        k = 0
                        wait_list = numpy.random.permutation([0, 1])
                        for p in self.get_players():
                            if p.side == s and p.type == t:
                                p.wait = wait_list[k]
                                k = k + 1
            elif self.session.vars['nplayers'] == 24:
                for s in [1, 2]:
                    for t in Constants.types:
                        k = 0
                        wait_list = numpy.random.permutation([0, 1, 2, 3])
                        for p in self.get_players():
                            if p.side == s and p.type == t:
                                p.wait = wait_list[k]
                                k = k + 1
        # then for any round that is not a restart round
        if self.round_number not in Constants.restart_rounds:
            # keep market number and update period
            self.market_number = self.in_round(self.round_number-1).market_number
            self.period = self.in_round(self.round_number-1).period + 1
            # keep side and type
            for p in self.get_players():
                p.side = p.in_round(self.round_number - 1).side
                p.type = p.in_round(self.round_number - 1).type
                p.wait = p.in_round(self.round_number - 1).wait
            #update wait status
            for p in self.get_players():
                if p.in_round(self.round_number - 1).match == 1:
                    p.wait = self.session.vars['waitlistlength']
                    for q in self.get_players():
                        if q.side == p.side and q.type == p.type and q.in_round(self.round_number - 1).wait > 0:
                            q.wait = q.in_round(self.round_number - 1).wait - 1


#  form random pairs
        side1_activeplayers = []
        side2_activeplayers = []
        for p in self.get_players():
            pid = p.id_in_group
            if p.wait == 0 and p.side == 1:
                side1_activeplayers.append(pid)
            elif p.wait == 0 and p.side == 2:
                side2_activeplayers.append(pid)
        random_side2_activeplayers = list(numpy.random.permutation(side2_activeplayers))
        k = 0
        for p in self.get_players():
            if p.id_in_group in set(side1_activeplayers):
                k = side1_activeplayers.index(p.id_in_group)
                p.partner = random_side2_activeplayers[k]
            elif p.id_in_group in set(side2_activeplayers):
                k = random_side2_activeplayers.index(p.id_in_group)
                p.partner = side1_activeplayers[k]
#  generate signals
        for p in self.get_players():
            for q in self.get_players():
                if p.wait == 0 and p.partner == q.id_in_group:
                    if q.type == 5:
                        p.signal = numpy.random.choice(Constants.signals, p=Constants.pL)
                    elif q.type == 10:
                        p.signal = numpy.random.choice(Constants.signals, p=Constants.pM)
                    elif q.type == 100:
                        p.signal = numpy.random.choice(Constants.signals, p=Constants.pH)

# matching
    def clear_market(self):
        for p in self.get_players():
            for q in self.get_players():
                if p.wait == 0 and p.partner == q.id_in_group:
                    p.match = p.choice * q.choice
                    p.payoff = q.type * p.choice * q.choice


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    wait = models.IntegerField()  # 0=in market, 1, 2, 3
    side = models.IntegerField()
    type = models.IntegerField()
    partner = models.IntegerField()
    signal = models.StringField()
    choice = models.BooleanField(
        choices=[
            [True, 'Propose'],
            [False, 'Do not propose'],
        ],
        widget=widgets.RadioSelectHorizontal
    )
    match = models.IntegerField()
    late = models.IntegerField()

    def in_current_market(self):
        mn = self.subsession.market_number
        first = Constants.restart_rounds[mn-1]
        last = self.round_number
        return self.in_rounds(first,last)
