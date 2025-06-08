from typing import TypedDict, List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass


class DifficultyStat(TypedDict):
    difficulty: str
    count: int
    submissions: int


class UserStats(TypedDict):
    solvedProblem: int
    easySolved: int
    mediumSolved: int
    hardSolved: int
    totalSubmissionNum: List[DifficultyStat]
    acSubmissionNum: List[DifficultyStat]


class UserData(TypedDict):
    lc_id: str
    goal: List  # [daily_points, end_date]
    easySolved: int
    mediumSolved: int
    hardSolved: int
    points: int
    weekly_points: int


@dataclass
class UserToTag:
    username: str
    daily_goal: int


@dataclass
class LeaderboardEntry:
    username: str
    points: int


PROBLEM_SCALE = {
    "easy": 1,
    "medium": 2,
    "hard": 3,
}
