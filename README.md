# Cron Expression Parser

A small Python command-line program that expands a standard five-field cron expression into a readable table. It uses only the Python standard library.

## Requirements

- macOS or Linux
- Python 3.9 or later (`python3`)

## Run

From the project directory:

```sh
python3 cron_parser.py "*/15 0 1,15 * 1-5 /usr/bin/find"
```

Expected output:

```text
minute        0 15 30 45
hour          0
day of month  1 15
month         1 2 3 4 5 6 7 8 9 10 11 12
day of week   1 2 3 4 5
command       /usr/bin/find
```

The cron expression must be passed as **one quoted command-line argument**. The command portion may itself contain spaces.

## Test

```sh
python3 -m unittest discover -v
```

No installation or third-party dependencies are required.

## Design

- `expand_field()` parses a single field into a sorted, deduplicated list of integers.
- `parse_cron()` splits the five schedule fields from the command and applies each field's numeric bounds.
- `format_table()` formats the result with a 14-character left-aligned field-name column.
- `main()` handles the CLI and returns a nonzero exit code on invalid input.

Separating expansion, parsing, and presentation makes it straightforward to add syntax features or alternative output formats later.

## Supported syntax

| Syntax | Example | Meaning |
| --- | --- | --- |
| Wildcard | `*` | All allowed values |
| Number | `5` | A single value |
| List | `1,15` | Both values |
| Range | `1-5` | Inclusive range |
| Step | `*/15` | Every 15 values, starting at field minimum |
| Range with step | `1-10/2` | 1, 3, 5, 7, 9 |
| Start with step | `5/20` | 5, 25, 45 (for minutes) |

Combinations such as `1-5,10,20-30/5` are supported.

## Assumptions and limitations

- Five numeric schedule fields followed by a nonempty command are required.
- Field bounds: minute 0–59, hour 0–23, day of month 1–31, month 1–12, day of week 0–7.
- Day-of-week 7 is accepted as an alias for Sunday (0) and is displayed as 0. Some cron implementations differ in their preferred representation.
- Named weekdays/months (e.g. `MON`, `JAN`), `@yearly`, and extensions such as `L`, `W`, `#`, and `?` are not supported.
- This is an **expression expander**, not a scheduler. It does not compute actual future run dates or account for month lengths, leap years, time zones, or day-of-month/day-of-week matching semantics.
- Invalid syntax and out-of-range values produce an error message on stderr and a nonzero exit code.

## Future extensions

Field definitions can be enhanced with name-to-number mappings, or the expansion function can be extended to support special cron tokens. A separate scheduling layer could calculate actual run dates without changing table formatting.
