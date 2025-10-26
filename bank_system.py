
"""
Bank System by Jo Foundation
Core module for Phase 1: multi-account bank system with username + PIN (4 digits)
Features:
- Create account (username, 4-digit PIN, initial deposit)
- Login / logout
- Deposit
- Withdraw (with balance checks)
- Check balance
- Transaction history per account
- Persistence to JSON (accounts.json)
Security:
- PINs are stored as SHA-256 hashes (not plain text) for minimal security awareness.
Usage:
- Import this module in Google Colab or run it as a script.
- A simple CLI demo is included under `if __name__ == '__main__'`.
"""

import json
import os
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
import hashlib
import datetime

ACCOUNTS_FILE = '/mnt/data/accounts.json'  # In Colab this path will persist for the session only


def hash_pin(pin: str) -> str:
    """Return SHA-256 hash of the PIN string."""
    return hashlib.sha256(pin.encode('utf-8')).hexdigest()


def now_iso():
    return datetime.datetime.utcnow().isoformat() + 'Z'


@dataclass
class Transaction:
    timestamp: str
    type: str  # "deposit" or "withdraw"
    amount: float
    balance_after: float
    note: Optional[str] = None


@dataclass
class BankAccount:
    username: str
    pin_hash: str
    balance: float = 0.0
    transactions: List[Dict] = field(default_factory=list)

    def check_pin(self, pin: str) -> bool:
        return self.pin_hash == hash_pin(pin)

    def deposit(self, amount: float, note: Optional[str] = None) -> Transaction:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        tx = Transaction(timestamp=now_iso(), type="deposit", amount=amount, balance_after=self.balance, note=note)
        self.transactions.append(asdict(tx))
        return tx

    def withdraw(self, amount: float, note: Optional[str] = None) -> Transaction:
        if amount <= 0:
            raise ValueError("Withdraw amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        tx = Transaction(timestamp=now_iso(), type="withdraw", amount=amount, balance_after=self.balance, note=note)
        self.transactions.append(asdict(tx))
        return tx

    def get_balance(self) -> float:
        return self.balance

    def get_statement(self, n: int = 10) -> List[Dict]:
        return list(reversed(self.transactions))[:n]


class AccountManager:
    def __init__(self, storage_file: str = ACCOUNTS_FILE):
        self.storage_file = storage_file
        self.accounts: Dict[str, BankAccount] = {}
        self.logged_in: Optional[BankAccount] = None
        self.load()

    def load(self):
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    data = json.load(f)
                for username, info in data.items():
                    acc = BankAccount(username=username, pin_hash=info['pin_hash'], balance=info.get('balance', 0.0), transactions=info.get('transactions', []))
                    self.accounts[username] = acc
            except Exception as e:
                print(f"[WARN] Failed to load accounts from {self.storage_file}: {e}")

    def save(self):
        data = {}
        for username, acc in self.accounts.items():
            data[username] = {
                'pin_hash': acc.pin_hash,
                'balance': acc.balance,
                'transactions': acc.transactions
            }
        os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2)
        return self.storage_file

    def create_account(self, username: str, pin: str, initial_deposit: float = 0.0) -> BankAccount:
        if username in self.accounts:
            raise ValueError("Username already exists.")
        if not (pin.isdigit() and len(pin) == 4):
            raise ValueError("PIN must be 4 digits.")
        if initial_deposit < 0:
            raise ValueError("Initial deposit cannot be negative.")
        acc = BankAccount(username=username, pin_hash=hash_pin(pin), balance=float(initial_deposit))
        if initial_deposit > 0:
            # record initial deposit transaction
            acc.transactions.append(asdict(Transaction(timestamp=now_iso(), type="deposit", amount=initial_deposit, balance_after=acc.balance, note="initial_deposit")))
        self.accounts[username] = acc
        self.save()
        return acc

    def login(self, username: str, pin: str) -> BankAccount:
        acc = self.accounts.get(username)
        if acc is None:
            raise ValueError("Account not found.")
        if not acc.check_pin(pin):
            raise ValueError("Incorrect PIN.")
        self.logged_in = acc
        return acc

    def logout(self):
        self.logged_in = None

    def deposit_logged(self, amount: float, note: Optional[str] = None) -> Transaction:
        if not self.logged_in:
            raise RuntimeError("No user logged in.")
        tx = self.logged_in.deposit(amount, note=note)
        self.save()
        return tx

    def withdraw_logged(self, amount: float, note: Optional[str] = None) -> Transaction:
        if not self.logged_in:
            raise RuntimeError("No user logged in.")
        tx = self.logged_in.withdraw(amount, note=note)
        self.save()
        return tx

    def get_balance_logged(self) -> float:
        if not self.logged_in:
            raise RuntimeError("No user logged in.")
        return self.logged_in.get_balance()

    def get_statement_logged(self, n: int = 10) -> List[Dict]:
        if not self.logged_in:
            raise RuntimeError("No user logged in.")
        return self.logged_in.get_statement(n=n)


# Simple CLI demo (useful when run as script or in a cell)
def cli_demo():
    mgr = AccountManager()
    print("=== Bank System by Jo Foundation — CLI Demo ===")
    while True:
        print("\\nOptions: [1] Create [2] Login [3] Exit")
        cmd = input("Choose: ").strip()
        if cmd == '1':
            uname = input("Choose username: ").strip()
            pin = input("Choose 4-digit PIN: ").strip()
            dep = float(input("Initial deposit (0 if none): ").strip() or 0)
            try:
                mgr.create_account(uname, pin, dep)
                print("Account created.")
            except Exception as e:
                print("Error:", e)
        elif cmd == '2':
            uname = input("Username: ").strip()
            pin = input("PIN: ").strip()
            try:
                acc = mgr.login(uname, pin)
                print(f\"Logged in as {acc.username}. Balance: {acc.balance}\")
                while True:
                    print(\"\\n[1] Balance  [2] Deposit [3] Withdraw [4] Statement [5] Logout\")
                    c2 = input(\"Choose: \").strip()
                    if c2 == '1':
                        print(\"Balance:\", mgr.get_balance_logged())
                    elif c2 == '2':
                        amt = float(input(\"Amount to deposit: \").strip())
                        mgr.deposit_logged(amt)
                        print(\"Deposited.\", \"Balance:\", mgr.get_balance_logged())
                    elif c2 == '3':
                        amt = float(input(\"Amount to withdraw: \").strip())
                        try:
                            mgr.withdraw_logged(amt)
                            print(\"Withdrawn.\", \"Balance:\", mgr.get_balance_logged())
                        except Exception as e:
                            print(\"Error:\", e)
                    elif c2 == '4':
                        for tx in mgr.get_statement_logged(20):
                            print(tx)
                    elif c2 == '5':
                        mgr.logout()
                        print(\"Logged out.\")
                        break
                    else:
                        print(\"Unknown option.\")
            except Exception as e:
                print(\"Login failed:\", e)
        elif cmd == '3':
            print(\"Goodbye.\")
            break
        else:
            print(\"Unknown option.\")


if __name__ == '__main__':
    cli_demo()
