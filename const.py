from enum import Enum


class AttendancePunchType(Enum):
    CHECK_IN = 0
    CHECK_OUT = 1
    OVERTIME_IN = 4
    OVERTIME_OUT = 5
