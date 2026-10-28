# timestamp_parser_range_py

Parses a single ISO 8601 timestamp (UTC or with an explicit offset) into its scalar components, raising `ValueError` on ambiguous or non-compliant strings.

```python
from timestamp_parser_range_py import parse_timestamp, ParseResult

r = parse_timestamp("2024-01-02T03:04:05.6789+09:30")
assert r.nanosecond == 678_900_000
assert r.offset_minutes == 570
```

## Why this exists

The standard library offers `datetime.fromisoformat`, but its acceptance rules vary across Python versions and tend to be permissive on one axis and brittle on another. This library narrows the accepted grammar to one explicit profile and raises on anything outside it, so a caller can trust the return value.

## Accepted shape

    YYYY-MM-DDTHH:MM:SS[.frac][Z | ±HH:MM]

* Extended format only (with `-` and `:` separators). Basic format without separators is rejected.
* Fractional seconds are optional: a `.` then 1 to 9 digits, normalised to nanoseconds.
* Offset is optional. `Z` and `±HH:MM` both work; a bare `±HH` does not.
* Leap seconds (`:60`) are rejected — Python's datetime model treats seconds as 0-59.

## Awkward edges

A missing offset is treated as **UTC zero**, not as "unknown". If you need to distinguish "no offset supplied" from "explicit Z", compare the input string, not the result.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

## Limitations

Values are coerced to floats, so very large integers lose precision. If you need
exact integer aggregates over a window, this is the wrong tool.

