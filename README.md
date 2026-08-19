# numconvert

A dependency-free Linux command for common numeric conversions. It uses the
Python 3 standard library and provides one consistent interface for number
bases, physical units, computer sizes, percentages, and safe calculations.

## Installation

From this directory, run one command:

```bash
./install.sh
```

The installer places `numconvert` and its Python implementation in
`/usr/local/bin`. It automatically requests `sudo` when needed.

The command is intentionally named `numconvert` so it cannot conflict with
ImageMagick's `convert` command:

```bash
numconvert base 3D hex dec
```

For a user-only installation:

```bash
PREFIX="$HOME/.local" ./install.sh
```

Make sure `$HOME/.local/bin` is in your `PATH` if the `numconvert` command is
not found afterwards.

## Usage

Show the complete help or the available units:

```bash
numconvert --help
numconvert list
```

### Compact syntax

Conversions can also be written as one option followed by the value:

```bash
numconvert -decTohex 10       # a
numconvert -binTodec 1010     # 10
numconvert -kmTomiles 10      # 6.2137119224 mi
numconvert -CToF 100          # 212 F
numconvert -BToMiB 1536       # 0.0014648438 MiB
```

The source and target names are separated by `To`. The optional precision
argument is supported too:

```bash
numconvert -kmTomiles 10 --precision 3
```

### Number bases

```bash
numconvert base 255 dec hex       # ff
numconvert base 1010 bin dec      # 10
numconvert base ff hex dec        # 255
```

Named bases are `bin`, `oct`, `dec`, and `hex`. Numeric bases from 2 to 36 are
also supported.

### Physical units

```bash
numconvert unit 10 km miles       # 6.2137119224 mi
numconvert unit 32 F C             # 0 C
numconvert unit 1 m ft              # 3.280839895 ft
numconvert unit 1,5 h min           # 90 min
```

Supported unit groups include length, mass, volume, area, time, speed,
pressure, energy, power, angle, and temperature (`C`, `F`, `K`). Use
`--precision` to control the number of decimal places:

```bash
numconvert unit 10 km miles --precision 3
```

### Computer sizes

Both decimal units (`KB`, `MB`, `GB`) and binary units (`KiB`, `MiB`, `GiB`)
are supported:

```bash
numconvert size 1536 B MiB
numconvert size 1 GiB GB
```

French byte aliases such as `Ko`, `Mo`, and `Go` are accepted as well.

### Percentages

```bash
numconvert percent 25 of 80      # 20
```

### Calculations

`calc` evaluates a restricted mathematical expression without exposing a
shell or Python runtime:

```bash
numconvert calc 'sqrt(25) + 3'    # 8
numconvert calc '2^8'              # 256
```

Supported functions include `sqrt`, `sin`, `cos`, `tan`, `log`, `log10`,
`abs`, `round`, `min`, and `max`. Constants include `pi`, `e`, and `tau`.

## Files

- `numconvert.py`: conversion logic and command-line interface.
- `numconvert`: executable launcher and command name.
- `install.sh`: one-command installer.

## Requirements

- Linux or another Unix-like system with Bash.
- Python 3.
- The standard `install` utility.
