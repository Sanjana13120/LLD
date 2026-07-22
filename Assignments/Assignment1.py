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

class User:
    def __init__(self,user_id,name):
        self.user_id=user_id
        self.name=name
        self.accounts=[]

class Account:
    def __init__(self,account_id,balance):
        self.account_id=account_id
        self.balance=balance   

class Transaction:
    def __init__(self, transaction_id,status:"TransactionStatus", amount, sender, receiver,timestamp, payment_method):
        self.transaction_id=transaction_id
        self.amount=amount
        self.sender=sender
        self.receiver=receiver
        self.timestamp=timestamp
        self.status=status
        self.payment_method=payment_method      

class TransactionStatus(Enum):
    PENDING="Pending"
    SUCCESS="Success"
    FAILED="Failed"  
    CANCELLED="Cancelled"
    PROCESSING="Processing"
        

class PaymentProcessor: # WHAT steps happen around payment
    def process_payment(self,transaction):
        pass

class PaymentMethod(ABC): #HOW payment happens
    @abstractmethod
    def pay(self):
        pass

class Refundable(ABC):
    @abstractmethod
    def refund(self):
        pass

class CashbackApplicable(ABC):
    @abstractmethod
    def cashback(self):
        pass

class Schedulable(ABC):
    @abstractmethod
    def schedule(self):
        pass

class ReceiptGeneratable(ABC):
    @abstractmethod
    def generate_receipt(self):
        pass

class CardPayment(PaymentMethod, Refundable, CashbackApplicable, ReceiptGeneratable):
    def pay(self):
        print("Card Payment")

    def refund(self):
        print("Refund Initiated")

    def generate_receipt(self):
        print("Receipt generated")

    def cashback(self):
        print("Cashback applied")

class UPIPayment(PaymentMethod,ReceiptGeneratable):
    def pay(self):
        print("UPI Payment")
    
    def generate_receipt(self):
        print("Receipt generated")

class WalletPayment(PaymentMethod, Schedulable, Refundable):
    def pay(self):
        print("Wallet Payment")
    
    def schedule(self):
        print("Payment scheduled")

    def refund(self):
        print("Refund Initiated")