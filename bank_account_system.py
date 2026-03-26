from abc import ABC, abstractmethod
from datetime import datetime
import time

class Client:
    def __init__(self, address):
        self.address = address
        self.accounts = []
        
    def make_transaction(self, account, transaction_type, value):
        #Unified method to perform deposits and withdrawals
        if transaction_type.lower() == "deposit":
            transaction = Deposit(value)
        elif transaction_type.lower() == "withdraw":
            transaction = Withdraw(value)
        else:
            print("Invalid transaction type. Use 'deposit' or 'withdraw'.\n")
            return False
        
        transaction.register(account)
        return True
    
    def add_account(self, account_num):
        self.accounts.append(account_num)
        

class NaturalPerson(Client):
    def __init__(self, name, birth_date, register_num, address):
        super().__init__(address)
        self.name = name
        self.birth_date = birth_date
        self.register_num = register_num
        
class Account:
    def __init__(self, number, client):
        self._balance = 0
        self._number = number
        self._agency = "0001-1"
        self._client = client
        self._historic = Historic()
        
    @classmethod
    def new_account(cls, number, client):
        return cls(number, client)
        
    @property
    def balance(self):
        return self._balance
    
    @property
    def number(self):
        return self._number
    
    @property
    def agency(self):
        return self._agency
        
    @property
    def historic(self):
        return self._historic
        
    def withdraw(self, value):
        if value > 0 and value <= self._balance:
            self._balance -= value
            print(f"The amount of ${value} was withdrawn from your account.\n")
            return True
        print("Insufficient balance or invalid value.\n")
        return False
    
    def deposit(self, value):
        if value > 0:
            self._balance += value
            print(f"The amount of ${value} has been deposited into your account.\n")
            return True
        print("Invalid deposit value.\n")
        return False
    
class CheckingAccount(Account):
    # account with withdraw limit per day and per value
    def __init__(self, number, client, limit=500, limit_per_day=3):
        super().__init__(number, client)
        self.limit = limit
        self.limit_per_day = limit_per_day
        
    def withdraw(self, value):
        # logic to handle withdraw limit and limit per day
        today = datetime.now().strftime("%d-%m-%Y")
        withdraw_times_today = len(
            [
                transaction for transaction in self.historic.transactions 
                if transaction["type"] == "Withdraw" 
                and transaction["date"][:10] == today[:10]
            ]
        )
        
        if value > self.limit:
            print(f"You cannot withdraw more than ${self.limit} at once\n")
            return False
        elif withdraw_times_today >= self.limit_per_day:
            print(f"You have reached your transaction limit for today. Limit per day: {self.limit_per_day}\n")
            return False
        else:
            return super().withdraw(value)
    
    def __str__(self):
        return f"""\
        Agency:\t{self.agency}
        Acc:\t{self.number}
        Holder:\t{self._client.name}
        """

class Historic:
    def __init__(self):
        self._transactions = []
        
    @property
    def transactions(self):
        return self._transactions
        
    def add_transaction(self, transaction):
        self._transactions.append(
            {
                "type": transaction.__class__.__name__,
                "value": transaction.value,
                "date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            }
        )
        
class Transaction(ABC):
    @property
    @abstractmethod
    def value(self):
        pass
    
    @abstractmethod
    def register(self, account):
        pass
    
class Withdraw(Transaction):
    def __init__(self, value):
        self._value = value
    
    @property
    def value(self):
        return self._value
        
    def register(self, account):
        transaction_success = account.withdraw(self.value)
        if transaction_success:
            account.historic.add_transaction(self)
        else:
            print("Transaction could not be completed.\n")
        return transaction_success

class Deposit(Transaction):
    def __init__(self, value):
        self._value = value
    
    @property
    def value(self):
        return self._value
        
    def register(self, account):
        transaction_success = account.deposit(self.value)
        if transaction_success:
            account.historic.add_transaction(self)
        else:
            print("Transaction could not be completed.\n")
        return transaction_success


# Exemplos de uso:
cliente = NaturalPerson("Alexandre", "05/10/1988", "01234567-8", "1st Avenue")
conta_corrente = CheckingAccount.new_account(number=123, client=cliente)
print(f"""
{conta_corrente.__class__.__name__} of: {cliente.name}
Address: {cliente.address}
Birth Date: {cliente.birth_date}
Register Number: {cliente.register_num}
""")
print(conta_corrente)
print("Carrying out Transactions...\n")
print("\tDepositing $1000...")
time.sleep(1.5)
cliente.make_transaction(conta_corrente, "deposit", 1000)
print("\tWithdrawing $500...")
time.sleep(1.5)
cliente.make_transaction(conta_corrente, "withdraw", 500)
print("\tWithdrawing $600...")
time.sleep(2)
cliente.make_transaction(conta_corrente, "withdraw", 600)  # This will be limited by the per-transaction limit
print("\tWithdrawing $300...")
time.sleep(1.5)
cliente.make_transaction(conta_corrente, "withdraw", 300)
print("\tWithdrawing $250...")
time.sleep(2)
cliente.make_transaction(conta_corrente, "withdraw", 250) # This will be limited by the total balance
print("\tWithdrawing $50...")
time.sleep(1.5)
cliente.make_transaction(conta_corrente, "withdraw", 50)
print("\tWithdrawing $50...")
time.sleep(2)
cliente.make_transaction(conta_corrente, "withdraw", 50)  # This will be limited by the per-day limit
print("\tDepositing $1000...")
time.sleep(1.5)
cliente.make_transaction(conta_corrente, "deposit", 1000)

# Exibindo Historico e Balanço final
print("\nTransaction History:")
for transaction in conta_corrente.historic.transactions:
    print(f"{transaction['date']} - {transaction['type']}: ${transaction['value']}")

print(f"\nFinal balance: ${conta_corrente.balance}")
