# convert

A dependency-free Linux command for common numeric conversions. It uses the
Python 3 standard library and provides one consistent interface for number
bases, physical units, computer sizes, percentages, and safe calculations.

## Installation

From this directory, run one command:

```bash
./install.sh
```

The installer places `convert` and its Python implementation in
`/usr/local/bin`. It automatically requests `sudo` when needed.

For a user-only installation:

```bash
PREFIX="$HOME/.local" ./install.sh
```

Make sure `$HOME/.local/bin` is in your `PATH` if the `convert` command is
not found afterwards.

## Usage

Show the complete help or the available units:

```bash
convert --help
convert list
```

### Number bases

```bash
convert base 255 dec hex       # ff
convert base 1010 bin dec      # 10
convert base ff hex dec        # 255
```

Named bases are `bin`, `oct`, `dec`, and `hex`. Numeric bases from 2 to 36 are
also supported.

### Physical units

```bash
convert unit 10 km miles       # 6.2137119224 mi
convert unit 32 F C             # 0 C
convert unit 1 m ft              # 3.280839895 ft
convert unit 1,5 h min           # 90 min
```

Supported unit groups include length, mass, volume, area, time, speed,
pressure, energy, power, angle, and temperature (`C`, `F`, `K`). Use
`--precision` to control the number of decimal places:

```bash
convert unit 10 km miles --precision 3
```

### Computer sizes

Both decimal units (`KB`, `MB`, `GB`) and binary units (`KiB`, `MiB`, `GiB`)
are supported:

```bash
convert size 1536 B MiB
convert size 1 GiB GB
```

French byte aliases such as `Ko`, `Mo`, and `Go` are accepted as well.

### Percentages

```bash
convert percent 25 of 80      # 20
```

### Calculations

`calc` evaluates a restricted mathematical expression without exposing a
shell or Python runtime:

```bash
convert calc 'sqrt(25) + 3'    # 8
convert calc '2^8'              # 256
```

Supported functions include `sqrt`, `sin`, `cos`, `tan`, `log`, `log10`,
`abs`, `round`, `min`, and `max`. Constants include `pi`, `e`, and `tau`.

## Files

- `convert.py`: conversion logic and command-line interface.
- `convert`: executable launcher.
- `install.sh`: one-command installer.

## Requirements

- Linux or another Unix-like system with Bash.
- Python 3.
- The standard `install` utility.
