import sys
import json
import bcrypt
from pathlib import Path

USER_FILE = Path("users.json")

def load_users():
    if USER_FILE.exists():
        with open(USER_FILE, "r") as f:
            data = json.load(f)
            return data.get("users", {})
    return {}

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump({"users": users}, f, indent=4)

def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2].encode()

    # Hash password
    hashed = bcrypt.hashpw(password, bcrypt.gensalt()).decode()

    # Load existing users
    users = load_users()

    # Append / Update user
    users[username] = hashed

    # Save back
    save_users(users)
    print(f"User '{username}' added/updated successfully.")

if __name__ == "__main__":
    main()

