"""Parse a single ISO 8601 timestamp into its components.

The grammar accepted here is intentionally narrow:

    YYYY-MM-DDTHH:MM:SS[.fraction][Z | ±HH:MM]

Why this shape and not the full ISO 8601 calendar-grammar?
A parser that accepts week dates, ordinal dates, comma decimal
separators, and "basic format" (no separators) also has to *reject*
the ambiguous strings that form the long tail of ISO 8601 — for
example "2024-01" which could be a 4-digit year or year-month. We
choose one profile, validate it strictly, and raise ValueError for
anything outside it. The caller gets a predictable answer.
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass

__all__ = ["ParseResult", "parse_timestamp"]


_DATETIME_RE = re.compile(
    r"^"
    r"(\d{4})-([01]\d)-([0-3]\d)"
    r"T"
    r"([0-2]\d):([0-5]\d):([0-5]\d)"
    r"(?:\.(\d{1,9}))?"
    r"(Z|[+-][01]\d:[0-5]\d)?"
    r"$"
)


class ParseError(ValueError):
    """Raised when a string is not a valid timestamp in the supported profile."""


@dataclass(frozen=True)
class ParseResult:
    """The components of a parsed timestamp.

    Stored as scalar ints (not as a datetime) because the whole point
    is to *inspect* the parts, not to re-validate them.
    """

    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    nanosecond: int
    offset_minutes: int


def _split_digits_and_remainders(s: str) -> tuple[int, int]:
    """Given digits captured from the regex, return (digits_value, remainder_len).

    The separator between whole and fractional part is always '.', and
    a valid remainder is 1-9 digits (enforced by the regex), so no
    extra validation is needed here.
    """
    if s is None:
        return 0, 0
    length = len(s)
    digits = int(s, 10)
    return digits, 9 - length


def parse_timestamp(s: str) -> ParseResult:
    """Parse a single ISO 8601 timestamp.

    Accepted shape::

        YYYY-MM-DDTHH:MM:SS[.frac][Z | ±HH:MM]

    * Date and time parts use extended format (``-`` and ``:``
      separators). Basic format without separators is not accepted.
    * Fractional seconds are optional, ``.`` then 1-9 digits.
    * The offset is optional; ``Z`` means +00:00, ``±HH:MM`` is also
      allowed. A bare ``±HH`` or ``±HHMM`` is *not* accepted.
    * Leap seconds (``second == 60``) are rejected: Python's
      ``datetime`` and the supported profile treat seconds as 0-59.

    Raises ValueError on anything else, including empty strings,
    trailing characters, week dates, comma decimals, and
    space-separated date/time.
    """
    if not isinstance(s, str):
        raise ParseError(f"expected str, got {type(s).__name__}")
    m = _DATETIME_RE.match(s)
    if m is None:
        raise ParseError(f"not an ISO 8601 timestamp: {s!r}")

    year, month, day, hour, minute, second = (int(x) for x in m.group(1, 2, 3, 4, 5, 6))
    frac_digits, missing = _split_digits_and_remainders(m.group(7))
    nanos = frac_digits * (10 ** missing)

    try:
        datetime.date(year, month, day)
        datetime.time(hour, minute, second)
    except ValueError as exc:
        raise ParseError(f"out-of-range component in {s!r}: {exc}") from exc

    off = m.group(8)
    if off is None:
        offset_minutes = 0
    elif off == "Z":
        offset_minutes = 0
    else:
        sign = 1 if off[0] == "+" else -1
        off_hours = int(off[1:3], 10)
        off_mins = int(off[4:6], 10)
        offset_minutes = sign * (off_hours * 60 + off_mins)

    return ParseResult(
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        second=second,
        nanosecond=nanos,
        offset_minutes=offset_minutes,
    )
