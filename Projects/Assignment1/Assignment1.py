# Payment Processing System

# Objective

# Design and implement a Payment Processing System that supports multiple payment methods, safe extensibility, and clean
# separation of responsibilities using OOP and SOLID principles.

# Step1: Functional Requirements

# 1. Payment Processing
#    PaymentMethod (Interface)
#       -> CardPayment
#       -> UPIPayment
#       -> WalletPayment
#       -> CryptoPayment (future)

# 2. Refund Handling
#    Refundable (Interface)

# 3. Receipt Generation
#    ReceiptGeneratable (Interface)

# 4. Cashback / Offers
#    CashbackApplicable (Interface)

# 5. Scheduled Payment
#    Schedulable (Interface)

# Step 2: Non Functional Requirements

# 1. No if-else or switch on payment type
# 2. No UnsupportedOperationException
# 3. Follow OOP and SOLID principles
# 4. High level modules should depend on abstractions
# 5. Easily extensible for new payment methods
# 6. Easy to unit test

# Step 3: identify the entities
# User 
# Account

# PaymentMethod (interface)
# |--- CardPayment
# |--- UPIPayment
# |--- WalletPayment
# |--- CryptoPayment (future)

# Refundable
# ReceiptGeneratable
# CashbackApplicable
# Schedulable

# PaymentProcessor

# Transaction
# Transaction Status

# Step 4: Identify Relationship 

# CardPayment implements:
#     PaymentMethod
#     Refundable
#     ReceiptGeneratable
#     CashbackApplicable

# UPIPayment implements:
    # PaymentMethod
    # ReceiptGeneratable

# WalletPayment implements:
#     PaymentMethod
#     Schedulable
#     Refundable

# Future improvement:
# Separate validator classes can be introduced  to follow SRP.

#Step 4.1 Identify fieds
# User
#   - user_id
#   - Name
#   - accounts

# Accounts
#   - account_id
#   - balance

# Transaction
#   - Transaction_id
#   - status
#   - amount
#   - sender
#   - receiver
#   - timestamp
#   - payment_method


# Step 5: Coding
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime

class User:
    def __init__(self,user_id,name):
        self.user_id=user_id
        self.name=name
        self.accounts=[]

    def get_primary_account(self):
        return self.accounts[0]

class Account:
    def __init__(self,account_id,balance):
        self.account_id=account_id
        self.balance=balance 

    def debit(self,amount):

        if self.balance<amount:
            return False
            
        self.balance-=amount
        return True

    def credit(self,amount):
        self.balance+=amount


class Transaction:
    def __init__(self, transaction_id,status:"TransactionStatus", amount, sender, receiver,timestamp, payment_method,schedule_date=None):
        self.transaction_id=transaction_id
        self.amount=amount
        self.sender=sender
        self.receiver=receiver
        self.timestamp=timestamp
        self.status=status
        self.payment_method=payment_method     
        self.schedule_date=schedule_date 

class TransactionStatus(Enum):
    PENDING="Pending"
    SUCCESS="Success"
    FAILED="Failed"  
    CANCELLED="Cancelled"
    PROCESSING="Processing"
    REFUNDED="Refund"
    SCHEDULED="Scheduled"
        

class PaymentProcessor: # WHAT steps happen around payment
    def process_payment(self,transaction):

        transaction.status = TransactionStatus.PROCESSING
        result=transaction.payment_method.pay(transaction)

        if result:
            transaction.status=TransactionStatus.SUCCESS
            if isinstance(transaction.payment_method,ReceiptGeneratable):
                transaction.payment_method.generate_receipt()

            if isinstance(transaction.payment_method,CashbackApplicable):
                transaction.payment_method.cashback(transaction)

        else:
            transaction.status=TransactionStatus.FAILED

    def schedule_payment(self,transaction):
        if isinstance(transaction.payment_method,Schedulable):
            transaction.payment_method.schedule(transaction)
            transaction.status= TransactionStatus.SCHEDULED

        
class PaymentMethod(ABC): #HOW payment happens
    @abstractmethod
    def pay(self,transaction):
        pass

class Refundable(ABC):
    @abstractmethod
    def refund(self,transaction):
        pass

class CashbackApplicable(ABC):
    @abstractmethod
    def cashback(self,transaction):
        pass

class Schedulable(ABC):
    @abstractmethod
    def schedule(self,transaction):
        pass

class ReceiptGeneratable(ABC):
    @abstractmethod
    def generate_receipt(self):
        pass

class CardPayment(PaymentMethod, Refundable, CashbackApplicable, ReceiptGeneratable):
    def pay(self,transaction):
        sender_account = transaction.sender.get_primary_account()
        receiver_account = transaction.receiver.get_primary_account()

        if not sender_account.debit(transaction.amount):
            print("Insufficient Balance")
            return False

        receiver_account.credit(transaction.amount)

        return True

    def refund(self,transaction):
        sender_account = transaction.sender.get_primary_account()
        receiver_account = transaction.receiver.get_primary_account()

        if not receiver_account.debit(transaction.amount):
            print("Refund Failed")
            return False
        
        sender_account.credit(transaction.amount)
    
        return True

    def generate_receipt(self):
        print("Card Receipt generated")

    def cashback(self,transaction):
        cashback_amount=transaction.amount*0.05
        print("Cashback amount applied: ",cashback_amount)

class UPIPayment(PaymentMethod,ReceiptGeneratable):
    def pay(self,transaction):
        sender_account= transaction.sender.get_primary_account()
        receiver_account = transaction.receiver.get_primary_account()

        if not sender_account.debit(transaction.amount):
            print("Insufficient balance")
            return False

        receiver_account.credit(transaction.amount)
        
        return True
        
    def generate_receipt(self):
        print("UPI Receipt generated")

class WalletPayment(PaymentMethod, Schedulable, Refundable):
    def pay(self,transaction):
        sender_account=transaction.sender.get_primary_account()
        receiver_account=transaction.receiver.get_primary_account()

        if not sender_account.debit(transaction.amount):
            print("Insufficient Balance")
            return False
        
        receiver_account.credit(transaction.amount)

        return True

    def refund(self,transaction):
        sender_account=transaction.sender.get_primary_account()
        receiver_account= transaction.receiver.get_primary_account()

        if not receiver_account.debit(transaction.amount):
            print("Refund Failed")
            return False
        
        sender_account.credit(transaction.amount)
        print("Refund Successful")
        return True
    
    def schedule(self,transaction):
        print(f"Payment of {transaction.amount} scheduled for {transaction.schedule_date}")


class CryptoPayment(PaymentMethod,ReceiptGeneratable):
    def pay(self, transaction):
        print("Crypto Transferred")
        return True

    def generate_receipt(self):
        print("Crypto receipt generated")
    


if __name__=="__main__":
    user1= User("1","Sanjana")
    user2= User("2", "Rahul")

    account1= Account("A101", 1000)
    account2= Account("A102", 500)

    user1.accounts.append(account1)
    user2.accounts.append(account2)

    payment_processor= PaymentProcessor()

################################# Card Payment  #########################################

    print("Card Payment")
    card_payment= CardPayment()

    transaction = Transaction("T1",TransactionStatus.PENDING, 200, user1,user2,datetime.now(), card_payment)

    payment_processor.process_payment(transaction)

    print(transaction.status.value)
    print(f"Sender balance: {user1.get_primary_account().balance}")
    print(f"Receiver balance : {user2.get_primary_account().balance}")

    print("After card Refund")
    if transaction.status == TransactionStatus.SUCCESS:
        refund_result= transaction.payment_method.refund(transaction)
        if refund_result:
            transaction.status=TransactionStatus.REFUNDED
            print(transaction.status.value)
    print(f"Sender balance: {user1.get_primary_account().balance}")
    print(f"Receiver balance: {user2.get_primary_account().balance}")

    print("\n")    

    ################################# UPI Payment  #########################################

    print("UPI Payment")
    upi_payment = UPIPayment()
    transaction=Transaction("U1", TransactionStatus.PENDING, 400, user1, user2, datetime.now(), upi_payment)

    payment_processor.process_payment(transaction)

    
    print(transaction.status.value)
    print(f"Sender balance: {user1.get_primary_account().balance}")
    print(f"Receiver balance : {user2.get_primary_account().balance}")

    print("\n")

################################# Wallet  Payment  #########################################

    print("Wallet Payment")
    wallet_payment = WalletPayment()
    transaction = Transaction("W1", TransactionStatus.PENDING, 100, user1, user2, datetime.now(), wallet_payment,"2026-08-01")

    payment_processor.schedule_payment(transaction)

    print(transaction.status.value)
    print(f"Sender balance: {user1.get_primary_account().balance}")
    print(f"Receiver balance : {user2.get_primary_account().balance}")

# ===============================================================================
# Output: 
# ================================================================================
# Card Payment
# Card Receipt generated
# Cashback amount applied:  10.0
# Success
# Sender balance: 800
# Receiver balance : 700
# After card Refund
# Refund
# Sender balance: 1000
# Receiver balance: 500


# UPI Payment
# UPI Receipt generated
# Success
# Sender balance: 600
# Receiver balance : 900


# Wallet Payment
# Payment of 100 scheduled for 2026-08-01
# Scheduled
# Sender balance: 600
# Receiver balance : 900