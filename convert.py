#!/usr/bin/env python3
"""A small, dependency-free command for common numeric conversions."""

from __future__ import annotations

import argparse
import ast
import math
import operator
import re
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext


class ConversionError(ValueError):
    """An error caused by an invalid conversion request."""


def decimal(value: str) -> Decimal:
    """Parse a human-friendly decimal number."""
    cleaned = value.strip().replace("_", "")
    if "," in cleaned and "." not in cleaned and cleaned.count(",") == 1:
        cleaned = cleaned.replace(",", ".")
    try:
        number = Decimal(cleaned)
    except InvalidOperation as exc:
        raise ConversionError(f"nombre invalide : {value!r}") from exc
    if not number.is_finite():
        raise ConversionError("le nombre doit être fini")
    return number


def format_decimal(value: Decimal, places: int) -> str:
    """Round a Decimal and remove insignificant zeroes."""
    with localcontext() as context:
        context.prec = max(50, places + max(0, value.adjusted()) + 10)
        rounded = value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)
    text = format(rounded, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


BASE_ALIASES = {
    "bin": 2,
    "binary": 2,
    "binaire": 2,
    "oct": 8,
    "octal": 8,
    "dec": 10,
    "decimal": 10,
    "hex": 16,
    "hexa": 16,
    "hexadecimal": 16,
}


def resolve_base(value: str) -> int:
    key = value.strip().casefold()
    if key in BASE_ALIASES:
        return BASE_ALIASES[key]
    try:
        base = int(key)
    except ValueError as exc:
        raise ConversionError(f"base inconnue : {value!r}") from exc
    if not 2 <= base <= 36:
        raise ConversionError("une base doit être comprise entre 2 et 36")
    return base


def convert_base(value: str, source: str, target: str) -> str:
    source_base = resolve_base(source)
    target_base = resolve_base(target)
    cleaned = value.strip().replace("_", "")
    try:
        number = int(cleaned, source_base)
    except ValueError as exc:
        raise ConversionError(
            f"{value!r} n'est pas un entier valide en base {source_base}"
        ) from exc

    if target_base == 10:
        return str(number)
    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    sign = "-" if number < 0 else ""
    number = abs(number)
    if number == 0:
        return "0"
    result = []
    while number:
        number, remainder = divmod(number, target_base)
        result.append(digits[remainder])
    return sign + "".join(reversed(result))


def unit_data(factor: str, *aliases: str) -> tuple[Decimal, tuple[str, ...]]:
    return Decimal(factor), aliases


# Factors are relative to the SI unit of each group.
UNIT_GROUPS = {
    "length": {
        "m": unit_data("1", "m", "meter", "metre", "meters", "metres"),
        "km": unit_data("1000", "km", "kilometer", "kilometre", "kilometers", "kilometres"),
        "cm": unit_data("0.01", "cm", "centimeter", "centimetre", "centimeters", "centimetres"),
        "mm": unit_data("0.001", "mm", "millimeter", "millimetre", "millimeters", "millimetres"),
        "um": unit_data("0.000001", "um", "micrometer", "micrometre", "micrometers", "micrometres"),
        "nm": unit_data("0.000000001", "nm", "nanometer", "nanometre", "nanometers", "nanometres"),
        "in": unit_data("0.0254", "in", "inch", "inches", '"'),
        "ft": unit_data("0.3048", "ft", "foot", "feet"),
        "yd": unit_data("0.9144", "yd", "yard", "yards"),
        "mi": unit_data("1609.344", "mi", "mile", "miles"),
        "nmi": unit_data("1852", "nmi", "nauticalmile", "nauticalmiles"),
    },
    "mass": {
        "g": unit_data("1", "g", "gram", "gramme", "grams", "grammes"),
        "kg": unit_data("1000", "kg", "kilogram", "kilogramme", "kilograms", "kilogrammes"),
        "mg": unit_data("0.001", "mg", "milligram", "milligramme", "milligrams", "milligrammes"),
        "t": unit_data("1000000", "t", "tonne", "tonnes", "metricton", "metrictons"),
        "lb": unit_data("453.59237", "lb", "pound", "pounds"),
        "oz": unit_data("28.349523125", "oz", "ounce", "ounces"),
    },
    "volume": {
        "l": unit_data("1", "l", "liter", "litre", "liters", "litres"),
        "ml": unit_data("0.001", "ml", "milliliter", "millilitre", "milliliters", "millilitres"),
        "m3": unit_data("1000", "m3", "m^3", "cubicmeter", "cubicmetre"),
        "cm3": unit_data("0.000001", "cm3", "cm^3", "cubiccentimeter", "cubiccentimetre"),
        "gal": unit_data("3.785411784", "gal", "gallon", "gallons"),
        "qt": unit_data("0.946352946", "qt", "quart", "quarts"),
        "pt": unit_data("0.473176473", "pt", "pint", "pints"),
        "cup": unit_data("0.2365882365", "cup", "cups"),
    },
    "area": {
        "m2": unit_data("1", "m2", "m^2", "sqm"),
        "km2": unit_data("1000000", "km2", "km^2", "sqkm"),
        "cm2": unit_data("0.0001", "cm2", "cm^2", "sqcm"),
        "ft2": unit_data("0.09290304", "ft2", "ft^2", "sqft"),
        "in2": unit_data("0.00064516", "in2", "in^2", "sqin"),
        "ha": unit_data("10000", "ha", "hectare", "hectares"),
        "acre": unit_data("4046.8564224", "acre", "acres"),
    },
    "time": {
        "ns": unit_data("0.000000001", "ns", "nanosecond", "nanoseconds"),
        "us": unit_data("0.000001", "us", "microsecond", "microseconds"),
        "ms": unit_data("0.001", "ms", "millisecond", "milliseconds"),
        "s": unit_data("1", "s", "sec", "second", "seconds"),
        "min": unit_data("60", "min", "minute", "minutes"),
        "h": unit_data("3600", "h", "hr", "hour", "hours"),
        "day": unit_data("86400", "d", "day", "days"),
        "week": unit_data("604800", "week", "weeks"),
    },
    "speed": {
        "m/s": unit_data("1", "m/s", "mps"),
        "km/h": unit_data("0.2777777777777777777777777778", "km/h", "kmh", "kph"),
        "mph": unit_data("0.44704", "mph", "mi/h"),
        "knot": unit_data("0.5144444444444444444444444444", "knot", "knots", "kt"),
    },
    "pressure": {
        "pa": unit_data("1", "pa", "pascal", "pascals"),
        "kpa": unit_data("1000", "kpa"),
        "bar": unit_data("100000", "bar", "bars"),
        "atm": unit_data("101325", "atm", "atmosphere", "atmospheres"),
        "psi": unit_data("6894.757293168", "psi"),
    },
    "energy": {
        "j": unit_data("1", "j", "joule", "joules"),
        "kj": unit_data("1000", "kj"),
        "wh": unit_data("3600", "wh", "watt-hour", "watthour"),
        "kwh": unit_data("3600000", "kwh", "kilowatt-hour", "kilowatthour"),
        "cal": unit_data("4.184", "cal", "calorie", "calories"),
        "kcal": unit_data("4184", "kcal", "kilocalorie", "kilocalories"),
    },
    "power": {
        "w": unit_data("1", "w", "watt", "watts"),
        "kw": unit_data("1000", "kw", "kilowatt", "kilowatts"),
        "mw": unit_data("1000000", "mw", "megawatt", "megawatts"),
        "hp": unit_data("745.6998715822702", "hp", "horsepower"),
    },
    "angle": {
        "rad": unit_data("1", "rad", "radian", "radians"),
        "deg": unit_data("0.0174532925199432957692369077", "deg", "degree", "degrees"),
        "turn": unit_data("6.2831853071795864769252867666", "turn", "turns"),
    },
}

TEMPERATURE_UNITS = {
    "C": ("c", "celsius", "degc"),
    "F": ("f", "fahrenheit", "degf"),
    "K": ("k", "kelvin", "kelvins"),
}

SIZE_UNITS = {
    "B": (Decimal("1"), ("b", "byte", "bytes", "o", "octet", "octets")),
    "KB": (Decimal("1000"), ("kb", "ko", "kilobyte", "kilobytes")),
    "MB": (Decimal("1000000"), ("mb", "mo", "megabyte", "megabytes")),
    "GB": (Decimal("1000000000"), ("gb", "go", "gigabyte", "gigabytes")),
    "TB": (Decimal("1000000000000"), ("tb", "to", "terabyte", "terabytes")),
    "PB": (Decimal("1000000000000000"), ("pb", "po", "petabyte", "petabytes")),
    "KiB": (Decimal(2**10), ("kib", "kio", "kibibyte", "kibibytes")),
    "MiB": (Decimal(2**20), ("mib", "mio", "mebibyte", "mebibytes")),
    "GiB": (Decimal(2**30), ("gib", "gio", "gibibyte", "gibibytes")),
    "TiB": (Decimal(2**40), ("tib", "tio", "tebibyte", "tebibytes")),
    "PiB": (Decimal(2**50), ("pib", "pio", "pebibyte", "pebibytes")),
}


def normalize_unit(value: str) -> str:
    return (
        value.strip()
        .casefold()
        .replace(" ", "")
        .replace("°", "")
        .replace("²", "2")
        .replace("³", "3")
    )


def find_unit(value: str) -> tuple[str, str, Decimal]:
    key = normalize_unit(value)
    for group, units in UNIT_GROUPS.items():
        for canonical, (factor, aliases) in units.items():
            if key in {normalize_unit(alias) for alias in aliases}:
                return group, canonical, factor
    raise ConversionError(f"unité inconnue : {value!r} (utilisez `convert list`)")


def find_temperature(value: str) -> str:
    key = normalize_unit(value)
    for canonical, aliases in TEMPERATURE_UNITS.items():
        if key in {normalize_unit(alias) for alias in aliases}:
            return canonical
    raise ConversionError(f"température inconnue : {value!r} (C, F ou K)")


def convert_temperature(value: Decimal, source: str, target: str) -> Decimal:
    source = find_temperature(source)
    target = find_temperature(target)
    if source == "C":
        celsius = value
    elif source == "F":
        celsius = (value - Decimal("32")) * Decimal(5) / Decimal(9)
    else:
        celsius = value - Decimal("273.15")

    if target == "C":
        return celsius
    if target == "F":
        return celsius * Decimal(9) / Decimal(5) + Decimal("32")
    return celsius + Decimal("273.15")


def convert_unit(value: str, source: str, target: str, places: int) -> str:
    number = decimal(value)
    if normalize_unit(source) in {normalize_unit(alias) for aliases in TEMPERATURE_UNITS.values() for alias in aliases} or normalize_unit(target) in {
        normalize_unit(alias) for aliases in TEMPERATURE_UNITS.values() for alias in aliases
    }:
        result = convert_temperature(number, source, target)
        target_name = find_temperature(target)
        return f"{format_decimal(result, places)} {target_name}"

    source_group, _, source_factor = find_unit(source)
    target_group, target_name, target_factor = find_unit(target)
    if source_group != target_group:
        raise ConversionError(
            f"conversion impossible entre {source!r} et {target!r}"
        )
    result = number * source_factor / target_factor
    return f"{format_decimal(result, places)} {target_name}"


def find_size(value: str) -> tuple[str, Decimal]:
    key = normalize_unit(value)
    for canonical, (factor, aliases) in SIZE_UNITS.items():
        if key in {normalize_unit(alias) for alias in aliases}:
            return canonical, factor
    raise ConversionError(f"taille inconnue : {value!r} (utilisez `convert list`)")


def convert_size(value: str, source: str, target: str, places: int) -> str:
    number = decimal(value)
    _, source_factor = find_size(source)
    target_name, target_factor = find_size(target)
    result = number * source_factor / target_factor
    return f"{format_decimal(result, places)} {target_name}"


def shortcut_conversion(value: str, source: str, target: str, places: int) -> str:
    """Convert using the compact -sourceTotarget syntax."""
    try:
        resolve_base(source)
        resolve_base(target)
    except ConversionError:
        pass
    else:
        return convert_base(value, source, target)

    try:
        find_size(source)
        find_size(target)
    except ConversionError:
        pass
    else:
        return convert_size(value, source, target, places)

    return convert_unit(value, source, target, places)


def percent_of(value: str, total: str, places: int) -> str:
    result = decimal(value) * decimal(total) / Decimal(100)
    return format_decimal(result, places)


CALC_CONSTANTS = {"pi": math.pi, "e": math.e, "tau": math.tau}
CALC_FUNCTIONS = {
    "abs": abs,
    "ceil": math.ceil,
    "cos": math.cos,
    "floor": math.floor,
    "log": math.log,
    "log10": math.log10,
    "max": max,
    "min": min,
    "round": round,
    "sin": math.sin,
    "sqrt": math.sqrt,
    "tan": math.tan,
}
CALC_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
CALC_UNARYOPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def evaluate_calculation(node: ast.AST) -> int | float:
    if isinstance(node, ast.Expression):
        return evaluate_calculation(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        if isinstance(node.value, bool):
            raise ConversionError("valeur booléenne interdite")
        return node.value
    if isinstance(node, ast.Name) and node.id in CALC_CONSTANTS:
        return CALC_CONSTANTS[node.id]
    if isinstance(node, ast.BinOp) and type(node.op) in CALC_BINOPS:
        left = evaluate_calculation(node.left)
        right = evaluate_calculation(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ConversionError("exposant trop grand")
        try:
            return CALC_BINOPS[type(node.op)](left, right)
        except (ArithmeticError, OverflowError) as exc:
            raise ConversionError("calcul impossible") from exc
    if isinstance(node, ast.UnaryOp) and type(node.op) in CALC_UNARYOPS:
        return CALC_UNARYOPS[type(node.op)](evaluate_calculation(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        function = CALC_FUNCTIONS.get(node.func.id)
        if function is None or node.keywords:
            raise ConversionError(f"fonction non autorisée : {node.func.id}")
        try:
            return function(*(evaluate_calculation(argument) for argument in node.args))
        except (ArithmeticError, TypeError, ValueError, OverflowError) as exc:
            raise ConversionError("calcul impossible") from exc
    raise ConversionError("expression non autorisée")


def calculate(expression: str, places: int) -> str:
    try:
        tree = ast.parse(expression.replace("^", "**"), mode="eval")
    except SyntaxError as exc:
        raise ConversionError("expression invalide") from exc
    result = evaluate_calculation(tree)
    if isinstance(result, float) and not math.isfinite(result):
        raise ConversionError("le résultat n'est pas fini")
    if isinstance(result, float):
        text = f"{result:.{places}g}"
        return str(int(result)) if result.is_integer() and abs(result) < 10**15 else text
    return str(result)


def print_units() -> None:
    print("Bases : bin, oct, dec, hex, ou un nombre de 2 à 36")
    print("Unités physiques :")
    for group, units in UNIT_GROUPS.items():
        print(f"  {group:9} : {', '.join(units)}")
    print("Températures : C, F, K")
    print(f"Tailles     : {', '.join(SIZE_UNITS)}")


def positive_places(value: str) -> int:
    places = int(value)
    if not 0 <= places <= 50:
        raise argparse.ArgumentTypeError("la précision doit être comprise entre 0 et 50")
    return places


SHORTCUT_PATTERN = re.compile(r"^-([^\s-]+?)[tT][oO]([^\s-]+)$")


def compact_command(argv: list[str]) -> tuple[str, int] | None:
    """Parse -sourceTotarget value and return its result and precision."""
    if not argv:
        return None
    match = SHORTCUT_PATTERN.fullmatch(argv[0])
    if match is None:
        return None
    if len(argv) not in {2, 4}:
        raise ConversionError(
            "syntaxe compacte : convert -sourceTotarget valeur [--precision nombre]"
        )

    places = 10
    if len(argv) == 4:
        if argv[2] != "--precision":
            raise ConversionError(
                "la syntaxe compacte accepte uniquement --precision après la valeur"
            )
        try:
            places = positive_places(argv[3])
        except (TypeError, ValueError, argparse.ArgumentTypeError) as exc:
            raise ConversionError(str(exc)) from exc

    source, target = match.groups()
    return shortcut_conversion(argv[1], source, target, places), places


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="convert",
        description="Convertisseur numérique polyvalent sans dépendance externe.",
        epilog="Exemples : convert -decTohex 255 | convert -kmTomiles 10 | convert base 255 dec hex",
    )
    parser.add_argument("--version", action="version", version="convert 1.0")
    commands = parser.add_subparsers(dest="command", metavar="COMMANDE")

    base = commands.add_parser("base", help="convertir un entier entre deux bases")
    base.add_argument("value", help="valeur à convertir")
    base.add_argument("source", help="base de départ : bin, oct, dec, hex ou 2-36")
    base.add_argument("target", help="base d'arrivée : bin, oct, dec, hex ou 2-36")

    unit = commands.add_parser("unit", help="convertir une unité physique")
    unit.add_argument("value")
    unit.add_argument("source", help="unité de départ")
    unit.add_argument("target", help="unité d'arrivée")
    unit.add_argument("--precision", type=positive_places, default=10, help="nombre de décimales (défaut : 10)")

    size = commands.add_parser("size", help="convertir des tailles informatiques")
    size.add_argument("value")
    size.add_argument("source", help="B, KB, MB, GB, KiB, MiB, ...")
    size.add_argument("target", help="B, KB, MB, GB, KiB, MiB, ...")
    size.add_argument("--precision", type=positive_places, default=10, help="nombre de décimales (défaut : 10)")

    percent = commands.add_parser("percent", help="calculer un pourcentage d'une valeur")
    percent.add_argument("value", help="pourcentage")
    percent.add_argument("of", choices=["of"], help="mot-clé obligatoire")
    percent.add_argument("total", help="valeur totale")
    percent.add_argument("--precision", type=positive_places, default=10, help="nombre de décimales (défaut : 10)")

    calc = commands.add_parser("calc", help="évaluer un calcul mathématique sûr")
    calc.add_argument("expression", help="exemple : 'sqrt(25) + 3'")
    calc.add_argument("--precision", type=positive_places, default=12, help="chiffres significatifs (défaut : 12)")

    commands.add_parser("list", help="afficher les unités disponibles")
    return parser


def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else argv
    parser = build_parser()
    try:
        compact = compact_command(raw_argv)
        if compact is not None:
            print(compact[0])
            return 0
    except ConversionError as exc:
        print(f"convert: erreur : {exc}", file=sys.stderr)
        return 2

    args = parser.parse_args(raw_argv)
    try:
        if args.command == "base":
            print(convert_base(args.value, args.source, args.target))
        elif args.command == "unit":
            print(convert_unit(args.value, args.source, args.target, args.precision))
        elif args.command == "size":
            print(convert_size(args.value, args.source, args.target, args.precision))
        elif args.command == "percent":
            print(percent_of(args.value, args.total, args.precision))
        elif args.command == "calc":
            print(calculate(args.expression, args.precision))
        elif args.command == "list":
            print_units()
        else:
            parser.print_help()
            return 1
    except ConversionError as exc:
        print(f"convert: erreur : {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
