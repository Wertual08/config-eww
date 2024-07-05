import sys


def info(message: str):
    print(f"INFO: {message}", file=sys.stderr)


def warn(message: str):
    print(f"WARN: {message}", file=sys.stderr)


def fail(message: str):
    print(f"FAIL: {message}", file=sys.stderr)


def crit(message: str):
    print(f"CRIT: {message}", file=sys.stderr)
