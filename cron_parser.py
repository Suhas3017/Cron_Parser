"""Expand standard five-field cron expressions into a readable table."""

import argparse
import sys

FIELDS = (
    ("minute", 0, 59),
    ("hour", 0, 23),
    ("day of month", 1, 31),
    ("month", 1, 12),
    ("day of week", 0, 7),
)


def expand_field(expression: str, minimum: int, maximum: int) -> list[int]:
    """Expand comma-separated cron terms, including ranges and steps."""
    values = set()
    for term in expression.split(","):
        if not term:
            raise ValueError("Empty cron list item")
        if "/" in term:
            base, separator, step_text = term.partition("/")
            if not step_text.isdecimal() or int(step_text) < 1:
                raise ValueError(f"Invalid step: {term}")
            step = int(step_text)
        else:
            base, step = term, 1
        if base == "*":
            start, end = minimum, maximum
        elif "-" in base:
            parts = base.split("-")
            if len(parts) != 2 or not all(part.isdecimal() for part in parts):
                raise ValueError(f"Invalid range: {term}")
            start, end = map(int, parts)
        elif base.isdecimal():
            if "/" in term:
                start, end = int(base), maximum
            else:
                start = end = int(base)
        else:
            raise ValueError(f"Invalid cron term: {term}")
        if not (minimum <= start <= end <= maximum):
            raise ValueError(f"Cron value out of range: {term} (allowed {minimum}-{maximum})")
        values.update(range(start, end + 1, step))
    return sorted(values)


def parse_cron(expression: str) -> list[tuple[str, str]]:
    """Parse five time fields and preserve the remaining command verbatim."""
    parts = expression.split(maxsplit=5)
    if len(parts) != 6 or not parts[5].strip():
        raise ValueError("Expected five cron fields followed by a command")
    result = []
    for token, (name, minimum, maximum) in zip(parts[:5], FIELDS):
        expanded = expand_field(token, minimum, maximum)
        # Both 0 and 7 represent Sunday in common cron implementations.
        if name == "day of week":
            expanded = sorted({0 if value == 7 else value for value in expanded})
        result.append((name, " ".join(map(str, expanded))))
    result.append(("command", parts[5]))
    return result


def format_table(rows: list[tuple[str, str]]) -> str:
    return "\n".join(f"{name:<14}{values}" for name, values in rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expression", help="Quoted cron expression with a command")
    args = parser.parse_args()
    try:
        print(format_table(parse_cron(args.expression)))
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
