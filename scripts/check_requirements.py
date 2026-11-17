#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare this repository's exact input pins/includes with its generated lock."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_PIN = re.compile(
    r"([A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?)"
    r"\s*==\s*([0-9][A-Za-z0-9.!+_-]*)"
)
_INCLUDE = re.compile(r"-r\s+(\S+)")
_HASH = re.compile(r"--hash=sha256:[0-9a-f]{64}")


def _read_pins(path: Path, *, lock: bool, stack: tuple[Path, ...] = ()) -> dict[str, str]:
    """Read the narrow repository format, rejecting rather than ignoring unknown lines."""
    path = path.resolve()
    if path in stack:
        raise ValueError(f"{path}: requirements include cycle")
    pins: dict[str, str] = {}
    for number, raw in enumerate(path.read_text().splitlines(), 1):
        line = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
        if not line or line.startswith("#"):
            continue
        if lock:
            line = line.removesuffix("\\").rstrip()
        include = _INCLUDE.fullmatch(line)
        pin = _PIN.fullmatch(line)
        if include and not lock:
            added = _read_pins(path.parent / include[1], lock=False, stack=(*stack, path))
        elif pin:
            added = {re.sub(r"[-_.]+", "-", pin[1]).lower(): pin[2]}
        elif lock and pins and _HASH.fullmatch(line):
            continue
        else:
            raise ValueError(f"{path}:{number}: unsupported requirements line")
        for name, version in added.items():
            if name in pins and pins[name] != version:
                raise ValueError(f"{path}:{number}: conflicting pins for {name}")
            pins[name] = version
    return pins


def check_requirements(root: Path) -> None:
    """Require every development/runtime input pin in the lock; allow transitive extras."""
    requirements = root / "requirements"
    inputs = _read_pins(requirements / "development.in", lock=False)
    locked = _read_pins(requirements / "development.lock", lock=True)
    errors = []
    for name, version in sorted(inputs.items()):
        if name not in locked:
            errors.append(f"{name}: input =={version}, missing from development.lock")
        elif locked[name] != version:
            errors.append(f"{name}: input =={version}, lock =={locked[name]}")
    if errors:
        raise ValueError("\n".join(errors))


def main() -> int:
    """Report input/lock drift or unsupported format on stderr with a failing status."""
    try:
        check_requirements(ROOT)
    except (OSError, ValueError) as error:
        print(f"Requirements lock check failed: {error}", file=sys.stderr)
        return 1
    print("Requirement input pins match development.lock.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
