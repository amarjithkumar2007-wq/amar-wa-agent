"""Parse reminder times. Pure functions, no I/O."""
import re
from datetime import datetime, timedelta, timezone

REL = re.compile(r"^(\d+)([mhd])$", re.I)
CLOCK = re.compile(r"^(\d{1,2}):(\d{2})$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def parse_when(tokens, now, tz_minutes=330):
    """tokens: list of words after /remind. now: aware datetime.
    Returns (due_datetime_utc, remaining_text) or None.
    Accepts: 30m / 2h / 1d, HH:MM (next occurrence, local tz), YYYY-MM-DD HH:MM.
    """
    if not tokens:
        return None
    tz = timezone(timedelta(minutes=tz_minutes))
    first = tokens[0]
    m = REL.match(first)
    if m:
        n, unit = int(m.group(1)), m.group(2).lower()
        delta = {"m": timedelta(minutes=n), "h": timedelta(hours=n), "d": timedelta(days=n)}[unit]
        return now + delta, " ".join(tokens[1:])
    m = CLOCK.match(first)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if h > 23 or mi > 59:
            return None
        local = now.astimezone(tz).replace(hour=h, minute=mi, second=0, microsecond=0)
        if local <= now:
            local += timedelta(days=1)
        return local.astimezone(timezone.utc), " ".join(tokens[1:])
    if DATE.match(first) and len(tokens) > 1:
        m2 = CLOCK.match(tokens[1])
        if not m2:
            return None
        try:
            y, mo, d = (int(x) for x in first.split("-"))
            local = datetime(y, mo, d, int(m2.group(1)), int(m2.group(2)), tzinfo=tz)
        except ValueError:
            return None
        return local.astimezone(timezone.utc), " ".join(tokens[2:])
    return None
