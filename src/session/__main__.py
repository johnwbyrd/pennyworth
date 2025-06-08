from . import get_session
import sys
import argparse
import getpass

def main():
    parser = argparse.ArgumentParser(description="Pennyworth session management")
    parser.add_argument("--username", help="Cognito username")
    parser.add_argument("--password", help="Cognito password")
    parser.add_argument("--new-password", help="New password (if change required)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose debug logging")
    args = parser.parse_args()

    try:
        params = {k: v for k, v in vars(args).items() if k in ("username", "password", "new_password", "verbose") and v is not None}
        session = get_session(params)
        if session:
            print("Current session valid until:", session["aws_credentials"]["Expiration"])
            return 0
        else:
            print("No valid session")
            return 1
    except Exception as e:
        print(f"Error: {e}")
        return 2

if __name__ == "__main__":
    sys.exit(main()) 