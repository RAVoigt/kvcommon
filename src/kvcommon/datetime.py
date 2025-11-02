import datetime
import typing as t

EPOCH = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
NEVER = datetime.datetime(3000, 1, 1, tzinfo=datetime.timezone.utc)


def utcnow() -> datetime.datetime:
    return datetime.datetime.now(tz=datetime.UTC)
