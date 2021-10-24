"""
 A set of utilities for using israel.csv
 The map is extracted from the OpenStreetMap project
"""

import math
from typing import List, Tuple, Dict, Iterator
from collections import defaultdict
import itertools
import numpy as np
from dataclasses import dataclass
import pandas as pd
import pickle
import re

class PlayersNBA:
    """
    The StreetsMap is basically a dictionary fro junction index to the Junction object.
    """

    def __init__(self, players: str, data: str):
        self.data = pd.read_csv(data, index_col=0)
        with open(players, "rb") as f:
            self.players = pickle.load(f)
        self.pos_list = {"PG", "SG", "SF", "PF", "C"}
        for pos in self.pos_list:
            for i, p in enumerate(self.players[pos]):
                first_name = re.findall("(.+?) ", p)[0]
                self.players[pos][i] = self.players[pos][i].replace(first_name, f'{first_name[0]}.')

        to_keep = self.data.index.isin(set([item for sublist in self.players.values() for item in sublist]))
        self.data = self.data[to_keep]
        #TODO: nba
        #"""
        self.data.drop([], inplace=True)
        #"""
    def __getitem__(self, key):
        return self.data[key]


class ScoresNBA:
    def __init__(self, players: PlayersNBA):
        #scores to rankings
        self.max_to = sum(sorted(players.data["TO"].dropna(),reverse=False)[:12])
        self.max_blk = sum(sorted(players.data["BLK"].dropna(),reverse=True)[:12])
        self.max_st = sum(sorted(players.data["ST"].dropna(),reverse=True)[:12])
        self.max_ast = sum(sorted(players.data["AST"].dropna(),reverse=True)[:12])
        self.max_reb = sum(sorted(players.data["REB"].dropna(),reverse=True)[:12])
        self.max_pts = sum(sorted(players.data["PTS"].dropna(),reverse=True)[:12])
        self.max_3pts = sum(sorted(players.data["3PTM"].dropna(),reverse=True)[:12])
        ##self.max_ft = sum(sorted(players.data["FT%"].dropna(),reverse=True)[:12])/12
        ##self.max_fg = sum(sorted(players.data["FG%"].dropna(),reverse=True)[:12])/12

        self.to_line = np.poly1d(np.polyfit([0, self.max_to], [1, 100], deg=1))
        self.blk_line = np.poly1d(np.polyfit([self.max_blk, 0], [1, 100], deg=1))
        self.st_line = np.poly1d(np.polyfit([self.max_st, 0], [1, 100], deg=1))
        self.ast_line = np.poly1d(np.polyfit([self.max_ast, 0], [1, 100], deg=1))
        self.reb_line = np.poly1d(np.polyfit([self.max_reb, 0], [1, 100], deg=1))
        self.pts_line = np.poly1d(np.polyfit([self.max_pts, 0], [1, 100], deg=1))
        self.pts3_line = np.poly1d(np.polyfit([self.max_3pts, 0], [1, 100], deg=1))
        self.ft_line = np.poly1d(np.polyfit([1, 0], [1, 100], deg=1))
        self.fg_line = np.poly1d(np.polyfit([1, 0], [1, 100], deg=1))
