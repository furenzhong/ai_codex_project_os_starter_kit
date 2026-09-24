#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# Check references; never infer or rewrite project facts automatically.
exec "${PYTHON:-python3}" "$SCRIPT_DIR/../project_os.py" check "$@"
