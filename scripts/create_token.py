"""Generate a JWT token for local testing.

Usage:
    uv run python scripts/create_token.py --role editor
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse

from src.core.models import Role
from src.security.rbac import create_token


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a test JWT token")
    parser.add_argument("--role", choices=[r.value for r in Role], default="editor")
    parser.add_argument("--subject", default="dev-user")
    args = parser.parse_args()

    token = create_token(args.subject, Role(args.role))
    print(f"\nToken (role={args.role}, sub={args.subject}):\n")
    print(token)
    print("\nUsage:")
    print(f'  curl -H "Authorization: Bearer {token}" http://localhost:8000/query ...')


if __name__ == "__main__":
    main()
