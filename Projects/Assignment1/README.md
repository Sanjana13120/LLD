# Payment Processing System

## Overview

This project implements a Payment Processing System using Object-Oriented Programming (OOP) and SOLID principles. 
The system is designed to support multiple payment methods while remaining extensible and maintainable.

## Requirements

The system supports:
- Payment Processing
- Refund Handling
- Receipt Generation
- Cashback Support
- Scheduled Payments

## Supported Payment Methods

- Card Payment
- UPI Payment
- Wallet Payment
- Crypto Payment (Future Extension)

## Design

### Core Classes

- User
- Account
- Transaction
- PaymentProcessor

### Interfaces

- PaymentMethod
- Refundable
- ReceiptGeneratable
- CashbackApplicable
- Schedulable

## Sample Output

```
Card Payment
Card Receipt generated
Cashback amount applied: 10.0
Success

UPI Payment
UPI Receipt generated
Success

Wallet Payment
Payment of 100 scheduled for 2026-08-01
Scheduled
```

## Future Enhancements

- Payment validation
- Notification service
- Database integration
- Unit testing
- Logging