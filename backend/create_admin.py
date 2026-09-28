"""
creates a new admin account directly in the db.

usage: uv run create_admin.py <username> <password>
no running server needed, connects to the sqlite db directly.
"""

import argparse
import os
import sys

# adds backend/ to import search path
sys.path.insert(0, os.path.dirname(__file__))

from app.admin import create_admin


def main():
    parser = argparse.ArgumentParser(description="creates a new admin account")
    parser.add_argument("username")
    parser.add_argument("password")
    args = parser.parse_args()

    try:
        created = create_admin(args.username, args.password)
    except ValueError as e:
        print(e)
        sys.exit(1)

    if not created:
        print("admin_already_exists")
        sys.exit(1)

    print("success")


if __name__ == "__main__":
    main()
