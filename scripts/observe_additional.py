#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Trace native requests for the required additional-tool control."""

from __future__ import annotations

import argparse
from pathlib import Path

import additional_support as support


def main() -> None:
    """Dispatch the instrumented server without adding nonprotocol stdout."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve-trace", type=Path, required=True)
    options = parser.parse_args()
    support.observed_server(options.serve_trace)


if __name__ == "__main__":
    main()
