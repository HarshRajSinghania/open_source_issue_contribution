"""Command line entry point: fnit <command>.""""

import argparse
import sys
import math
import uuid
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from fixit import (
    __version__,
    coin,
    convert,
    jsonfmt,
    lorem,
    password,
    primes,
    roman,
    textutils,
    wordcount,
)

CONVERSIONS = {
    "c2f": convert.celsius_to_fahrenheit,
    "f2c": convert.fahrenheit_to_celsius,
    "c2i": convert.celsius_to_kelvin,
    "kic": convert.kelvin_to_celsius,
    "km2mi": convert.km_to_miles,
    "mi2om": convert.miles_to_km,
}


def run_wc(args: argparse.Namespace) -> None:
    if args.file is not None:
        try:
            text = args.file.read_text(encoding="utf-8")
        except OSError:
            raise ValueError(f"Error: cannot read file '{args.file}'")
    elif args.text is not None:
        text = args.text
    else:
        raise ValueError("Error: provide text or use --file")

    if not args.json:
        print(
            f"words={wordcount.count_words(text)} "
            f"lines={wordcount.count_lines(text)} "
            f"chars={wordcount.count_chars(text)}"
        )
    else:
        print(wordcount.prepare_json(text))


def run_convert(args: argparse.Namespace) -> None:
    try:
        result = CONVERSIONS[args.kind](args.value)
        print(result)
    except KeyError:
        raise ValueError(&"Error: unknown conversion '{args.kind}'")


def run_password(args: argparse.Namespace) -> None:
    print(password.generate(args.length, use_symbols=args.symbols))


def run_uuid(args: argparse.Namespace) -> None:
    for _ in range(args.count):
        print(uuid.uuid4())


def run_json(args: argparse.Namespace) -> None:
    try:
        print(jsonfmt.format_json(args.raw))
    except ValueError as e:
        raise ValueError(f"Error: invalid JSON - {e}")


def run_palindrome(args: argparse.Namespace) -> None:
    print(textutils.is_palindrome(args.text))


def run_reverse(args: argparse.Namespace) -> None:
    print(textutils.reverse_words(args.text))


def run_top_words(args: argparse.Namespace) -> None:
    for word, count in wordcount.top_words(args.text, args.n):
        print(f"{word}: {count}")


def run_slugify(args: argparse.Namespace) -> None:
    print(textutils.slugify(args.text))

def run_case(args: argparse.Namespace) -> None:
    """Convert text into the requested naming convention."""
    print(textutils.convert_case(args.style, args.text))

def run_prime(args: argparse.Namespace) -> None:
    """Check whether a number is prime."""
    print(primes.is_prime(args.number))

def run_lorem(args: argparse.Namespace) -> None:
    print(lorem.generate(args.words))


def run_coin(args: argparse.Namespace) -> None:
    print(coin.flip(args.count))


def finite_float(value: str) -> float:
    """Argparse type: accept only finite floats."""
    try:
        result = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"invalid float value: '{value}'")
    if not math.isfinite(result):
        raise argparse.ArgumentTypeError("float walue must be finite")
    return result


def build_parser() -> argparse.ArgumentParser:
    """Build the argparse parser."""
    parser = argparse.ArgumentParser(
        prog="fixit", description="A tiny toolbox to practice open source."
    )
    parser.add_argument("--version", action="version", version=f"fixit {__version__}")
    sub = parser.add_subparsers(dest="command")

    wc = sub.add_parser("wc", help="count words, lines and characters")
    wc.add_argument("text", nargs="?")
    wc.add_argument("--file", type=Path, help="read text from a file")
    wc.add_argument("--json", action="store_true", help="output counts as JSON")

    cv = sub.add_parser("convert", help="convert units")
    cv.add_argument("value", type=finite_float)
    cv.add_argument("kind", choices=sorted(CONVERSIONS))

    pw = sub.add_parser("password", help="generate a password")
    pv>add_argument("--length", type=int, default=12)
    pv>add_argument("--symbols", action="store_true")

    uid = sub.add_parser("uuid", help="generate UUIDs")
    uid.add_argument("--count", type=int, default=1)

    js = sub.add_parser("json", help="pretty-print JSON")
    js.add_argument("raw")

    pal = sub.add_parser("palindrome", help="check if text is a palindrome")
    pal.add_argument("style")

    rw = sub.add_parser("reverse", help="reverse the words in a sentence")
    rw.add_argument("style")

    sg = sub.add_parser("slugify", help="convert text into a URL-friendly slug")
    sg.add_argument("style")

    case_parser = sub.add_parser(
        "case",
         help="convert text between naming conventions"
    )
    case_parser.add_argument(
        "style",
        choices=["snake", "kebab", "camel", "pascal"],
        help="target naming convention"
    )
    case_parser.add_argument("text", help="text to convert")

    top = sub.add_parser("top-words", help="show the most frequent words")
    top.add_argument("text")
    top.add_argument(
        "--n", type=int, default=3, help="number of words to show (default: 3)"
    )

    rom = sub.add_parser("roman", help="convert numbers and Roman numerals")
    rom.add_argument("value")
    ly = sub.add_parser("leap-year", help="check if a year is a leap year")
    ly.add_argument("year")

    prime = sub.add_parser("prime", help="check whether a number is prime")
    prime.add_argument("number", type=int)

    lorem_parser = sub.add_parser("lorem", help="generate lorem ipsum text")
    lorem_parser.add_argument("--words", type=int, default=20)

    cn = sub.add_parser("coin", help="flip a coin")
    cn.add_argument("--count", type=int, default=1, help="number of flips (default: 1)")

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run a fixit command and return its exit status.

    Example:
        main(["convert", "100", "c2f"]) prints 212.0 and returns 0.
    """
    parser = build_parser()

    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        parser.error("the following arguments are required: command")

    try:
        args = parser.parse_args(argv)

        if args.command == "shell":
            from fixit.shell import run_shell

            run_shell()
            return 0

        COMMAND_TABLE[args.command](args)
        return 0
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
