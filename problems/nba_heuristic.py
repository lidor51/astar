import numpy as np
import networkx as nx
from typing import *

from framework import *
from .nba_problem import *
#from .cached_nba_calculator import CachedNBACalculator

__all__ = ['NBATotalScoreHeuristic']


class NBATotalScoreHeuristic(HeuristicFunction):
    heuristic_name = 'NBATotalScoreHeuristic'

    def __init__(self, problem: GraphProblem):
        super(NBATotalScoreHeuristic, self).__init__(problem)
        assert isinstance(self.problem, NBAProblem)
        self.players_map = problem.players_map
        self.scores = ScoresNBA(self.players_map)
        #self.nba_cached_calculator = CachedNBACalculator()

    def estimate(self, state: GraphProblemState) -> float:
        """
        This heuristic returns a lower bound to the remained tests-travel-distance of the remained ambulance path.
        The main observation is that driving from a laboratory to a reported-apartment does not increase the
         tests-travel-distance cost. So the best case (lowest cost) is when we go to the closest laboratory right
         after visiting any reported-apartment.
        If the ambulance currently stores tests, this total remained cost includes the #tests_on_ambulance times
         the distance from the current ambulance location to the closest lab.
        The rest part of the total remained cost includes the distance between each non-visited reported-apartment
         and the closest lab (to this apartment) times the roommates in this apartment (as we take tests for all
         roommates).
        [Ex.33]:
            Complete the implementation of this method.
            Use `self.problem.get_reported_apartments_waiting_to_visit(state)`.
        """
        assert isinstance(self.problem, NBAProblem)
        assert isinstance(state, NBAState)
        #return 0
        top = 9 #TODO: nba
        to = self.players_map.data.loc[state.players]["TO"].sum()
        blk = self.players_map.data.loc[state.players]["BLK"].sum()
        st = self.players_map.data.loc[state.players]["ST"].sum()
        ast = self.players_map.data.loc[state.players]["AST"].sum()
        reb = self.players_map.data.loc[state.players]["REB"].sum()
        pts = self.players_map.data.loc[state.players]["PTS"].sum()
        pts3 = self.players_map.data.loc[state.players]["3PTM"].sum()
        fta = self.players_map.data.loc[state.players]["FTA"].sum()
        ft = 0 if fta == 0 else self.players_map.data.loc[state.players]["FTM"].sum() / fta
        fga = self.players_map.data.loc[state.players]["FGA"].sum()
        fg = 0 if fga == 0 else self.players_map.data.loc[state.players]["FGM"].sum() / fga
        scores = [self.scores.to_line(to), self.scores.blk_line(blk), self.scores.st_line(st), self.scores.ast_line(ast), self.scores.reb_line(reb), self.scores.pts_line(pts), self.scores.pts3_line(pts3), self.scores.ft_line(ft), self.scores.fg_line(fg)]
        score = np.prod(sorted(scores)[:top])
        return score