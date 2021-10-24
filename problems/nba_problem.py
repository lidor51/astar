from framework import *

from typing import Iterator
from dataclasses import dataclass
import numpy as np
import itertools
from random import shuffle

__all__ = ['NBAState', 'NBAProblem']


@dataclass(frozen=True)
class NBAState(GraphProblemState):
    """
    StreetsNBA state is represents the current geographic location on the map.
    This location is defined by the junction index.
    """
    players: frozenset

    def __eq__(self, other):
        assert isinstance(other, NBAState)
        return other.players == self.players

    def __hash__(self):
        return hash(self.players)

    def __str__(self):
        return str(self.players).rjust(5, ' ')


class NBAProblem(GraphProblem):
    """
    Represents a problem on the streets map.
    The problem is defined by a source location on the map and a destination.
    """

    name = 'PlayersNBA'

    def __init__(self, players_map: PlayersNBA, scores: ScoresNBA, players: frozenset):
        initial_state = NBAState(players)
        super(NBAProblem, self).__init__(initial_state)
        self.players_map = players_map
        self.scores = scores
        self.name += f'(src: {players})'
        self.best_cost = np.inf
        self.best_group = []

    def get_positions(self, player):
        positions = []
        for pos in self.players_map.pos_list:
            if player in self.players_map.players[pos]:
                positions.append(pos)
        return positions

    def count(self, pos_list, pos):
        return len([x for x in pos_list if x == pos])


    def is_legal(self, players):
        roster_players = 10
        util_limits = 2
        bench_players = 2 #TODO: nba
        if len(players) > roster_players + bench_players:
            return False
        positions = []
        for player in players:
            positions.append(self.get_positions(player))
        options = frozenset([tuple(sorted(x)) for x in itertools.product(*positions)])

        if not options:
            return True
        limits = {
            "pg_limit": 1,
            "sg_limit": 1,
            #"g_limit": 1,
            "sf_limit": 1,
            "pf_limit": 1,
            #"f_limit": 1,
            "c_limit": 2,
            #"util_limit": 2
        }
        g_limit = 1
        f_limit = 1

        for option in options:
            pg_count = self.count(option, "PG")
            sg_count = self.count(option, "SG")
            sf_count = self.count(option, "SF")
            pf_count = self.count(option, "PF")
            c_count = self.count(option, "C")

            utils = frozenset(itertools.combinations_with_replacement(list(self.players_map.pos_list), util_limits + bench_players))
            for util_lim in utils:
                pg = limits["pg_limit"] + util_lim.count("PG") - pg_count
                sg = limits["sg_limit"] + util_lim.count("SG") - sg_count
                sf = limits["sf_limit"] + util_lim.count("SF") - sf_count
                pf = limits["pf_limit"] + util_lim.count("PF") - pf_count
                c = limits["c_limit"] + util_lim.count("C") - c_count
                if ((pg + sg) >= (0 - g_limit)) and ((sf + pf) >= (0 - f_limit)) and (c >= 0):
                    return True

    def expand_state_with_costs(self, state_to_expand: GraphProblemState) -> Iterator[OperatorResult]:
        """
        For a given state, iterates over its successor states.
        The successor states represents the junctions to which there
         exists a road originates from the given state.
        """

        # All of the states in this problem are instances of the class `NBAState`.
        assert isinstance(state_to_expand, NBAState)

        # Get the junction (in the map) that is represented by the state to expand.
        curr_state = state_to_expand

        # union of labs and apartments
        for player, _ in self.players_map.data.sample(frac=1).iterrows():
            if player not in curr_state.players:
                players = curr_state.players | frozenset([player])
                if self.is_legal(players):
                    succ_state = NBAState(players=players)
                    cost = self.get_operator_cost(curr_state, succ_state)
                    if cost < self.best_cost:
                        self.best_cost = cost
                        self.best_group = players
                        print(players, cost)
                    yield OperatorResult(successor_state=succ_state, operator_cost=cost, operator_name="add " + player)
        # [Ex.10]:
        #  Read the documentation of this method in the base class `GraphProblem.expand_state_with_costs()`.
        #  Finish the implementation of this method.
        #  Iterate over the outgoing links of the current junction (find the implementation of `Junction`
        #  type to see the exact field name to access the outgoing links). For each link:
        #    (1) Create the successor state (it should be an instance of class `NBAState`). This state represents the
        #        target junction of the current link;
        #    (2) Yield an object of type `OperatorResult` with the successor state and the operator cost (which is
        #        `link.distance`). You don't have to specify the operator name here.
        #  Note: Generally, in order to check whether a variable is set to None you should use the expression:
        #        `my_variable_to_check is None`, and particularly do NOT use comparison (==).

    def is_goal(self, state: GraphProblemState) -> bool:
        """
        :return: Whether a given map state represents the destination.
        """
        assert (isinstance(state, NBAState))

        #  [Ex.10]: modify the returned value to indicate whether `state` is a final state.
        # You may use the problem's input parameters (stored as fields of this object by the constructor).
        return False

    def get_operator_cost(self, curr_state, succ_state) -> float:
        top = 6 #TODO: nba
        to = self.players_map.data.loc[succ_state.players]["TO"].sum()
        blk = self.players_map.data.loc[succ_state.players]["BLK"].sum()
        st = self.players_map.data.loc[succ_state.players]["ST"].sum()
        ast = self.players_map.data.loc[succ_state.players]["AST"].sum()
        reb = self.players_map.data.loc[succ_state.players]["REB"].sum()
        pts = self.players_map.data.loc[succ_state.players]["PTS"].sum()
        pts3 = self.players_map.data.loc[succ_state.players]["3PTM"].sum()
        fta = self.players_map.data.loc[succ_state.players]["FTA"].sum()
        ft = 0 if fta == 0 else self.players_map.data.loc[succ_state.players]["FTM"].sum() / fta
        fga = self.players_map.data.loc[succ_state.players]["FGA"].sum()
        fg = 0 if fga == 0 else self.players_map.data.loc[succ_state.players]["FGM"].sum() / fga
        scores = [self.scores.to_line(to), self.scores.blk_line(blk), self.scores.st_line(st), self.scores.ast_line(ast), self.scores.reb_line(reb), self.scores.pts_line(pts), self.scores.pts3_line(pts3), self.scores.ft_line(ft), self.scores.fg_line(fg)]
        score = np.prod(sorted(scores)[:top])
        if score < 0:
            print(scores)
        return score
