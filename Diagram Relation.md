# Diagram UML
## Code
```PlantUML
@startuml
title UML Diagram - Python Bank Account System

class Transaction {
    - timestamp: str
    - type: str
    - amount: float
    - balance_after: float
    - note: Optional[str]
}

class BankAccount {
    - username: str
    - pin_hash: str
    - balance: float
    - transactions: List[Dict]
    + check_pin(pin: str): bool
    + deposit(amount: float, note: Optional[str] = None): Transaction
    + withdraw(amount: float, note: Optional[str] = None): Transaction
    + get_balance(): float
    + get_statement(n: int = 10): List[Dict]
}

class AccountManager {
    - storage_file: str
    - accounts: Dict[str, BankAccount]
    - logged_in: Optional[BankAccount]
    + load(): void
    + save(): str
    + create_account(username: str, pin: str, initial_deposit: float = 0.0): BankAccount
    + login(username: str, pin: str): BankAccount
    + logout(): void
    + deposit_logged(amount: float, note: Optional[str] = None): Transaction
    + withdraw_logged(amount: float, note: Optional[str] = None): Transaction
    + get_balance_logged(): float
    + get_statement_logged(n: int = 10): List[Dict]
}

' Relationships
AccountManager "1" --> "*" BankAccount : manages
BankAccount "1" --> "*" Transaction : records
@enduml
```

## Images
![Bank Diagram]()
