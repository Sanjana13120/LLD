"""
================================================================================
LLD: Payment Service
================================================================================

Functional Requirement:
1. User should be able to make the payment.
2. System should support multiple payment methods - Card/UPI/Wallet/Netbanking
3. Prevent duplicate payments and should be idempotent.
4. Support refunds 
5. System should support multiple payment gateways - RazorPay, Stripe etc..
6. Maintain payment lifecycle/status.

Non- Functional Requirement:
1. Service should avoid duplicate payments.
2. Thread safe / handle concurrent payment requests.
3. Extensibilty - easy to add new payment methods/gateways.
4. Security  - protect payment-sensitive information.
5. Reliability  - safely handle gateway failures and ambiguous outcomes.

Identify core entities:
PaymentStatus
    - INITIATED/ PROCESSING/ SUCCESS/ FAILED/ PENDING

RefundStatus: INITIATED/ PROCESSING/ SUCCESS/ FAILED

PaymentRequest
    - user_id, payment_type, idempotency_key, amount, payment_details

PaymentResponse
    - payment_id, payment_status, message

PaymentMethod
    + validate(self, request:PaymentRequest)  --> CardPaymentMethod/ UPIPaymentMethod/ WalletPaymentMethod - strategy design pattern

PaymentGateway
    + process(self, request:PaymentRequest)  --> RazorPayGateway/ StripeGateway - strategy design pattern

RetryPolicy
    - PaymentGateway
    - max_attempts
    + retry(self, request:PaymentRequest) - decorator design pattern

IdempotencyManager

Refund

PaymentService
    - PaymentGateway
    - Map<PaymentType, PaymentMethod>
    - IdempotencyManager 

    + create_payment

Identify relationship:

PaymentMethod → validates payment-method-specific details
PaymentGateway → actually processes the payment

PaymentService --uses--> PaymentMethod
PaymentService --uses--> PaymentGateway
PaymentService --uses--> IdempotencyManager

RetryPolicy --wraps -->PaymentGateway

Design Patterns:
    1. Strategy Pattern - Allows payment methods and gateways to be changed independently.
       - PaymentMethod
       - PaymentGateway

    2. Decorator Pattern - Wraps PaymentGateway and adds retry behavior without modifying the gateway implementation.
       - RetryPolicy
       
Concurrency:
    - IdempotencyManager maintains a lock per idempotency key.
    - Concurrent requests with the same key are processed sequentially.
    - Prevents duplicate payment processing.

Retry:
    - RetryPolicy retries FAILED gateway responses up to max_attempts.
    - The underlying gateway is responsible for maintaining attempt state.

Idempotency:
    - Same idempotency key returns the previously stored PaymentResponse.
    - Payment is processed only once for a given idempotency key.

Refund:
    - Only successful payments can be refunded.
    - A payment can be refunded only once.


Coding:

"""

from abc import ABC, abstractmethod
from enum import Enum, auto 
from typing import Optional
import threading

class PaymentStatus(Enum):
    INITIATED = auto()
    PROCESSING = auto()
    SUCCESS = auto()
    FAILED = auto()
    PENDING = auto()

class RefundStatus(Enum):
    INITIATED = auto()
    PROCESSING = auto()
    SUCCESS = auto()
    FAILED = auto()

class PaymentType(Enum):
    CARD = auto()
    UPI = auto()
    WALLET = auto()
    NET_BANKING = auto()

class PaymentRequest:
    def __init__(self,  user_id: str, payment_type: PaymentType, idempotency_key:str, amount: float, payment_details):
        self.user_id = user_id
        self.payment_type = payment_type
        self.idempotency_key = idempotency_key
        self.amount = amount
        self.payment_details = payment_details

class PaymentResponse:
    def __init__(self, payment_id: Optional[str], payment_status: PaymentStatus, message: str):
        self.payment_id = payment_id
        self.payment_status = payment_status
        self.message = message

    def __str__(self):
        return f"PaymentResponse(payment_id={self.payment_id}, status={self.payment_status}, message={self.message})"

class Refund:
    def __init__(self, payment_id, refund_amount, refund_status: RefundStatus):
        self.payment_id = payment_id
        self.refund_amount = refund_amount
        self.refund_status = refund_status

    def __str__(self):
        return f"Refund(payment_id={self.payment_id}, amount refunded={self.refund_amount}, status={self.refund_status})"


class PaymentMethod(ABC):
    @abstractmethod
    def validate(self, request: PaymentRequest) -> bool:
        pass

class CardPaymentMethod(PaymentMethod):
    def validate(self, request) -> bool:
        card_number = request.payment_details.get("Card Number")
        return card_number is not None and len(card_number)==16

class UPIPaymentMethod(PaymentMethod):
    def validate(self, request) -> bool:
        upi_id = request.payment_details.get("UPI Id")
        return upi_id is not None and "@" in upi_id

class NetbankingPaymentMethod(PaymentMethod):
    def validate(self, request) -> bool:
        bank_code = request.payment_details.get("Bank code")
        return bank_code is not None

class PaymentGateway(ABC):
    @abstractmethod
    def process(self, request: PaymentRequest):
        pass

    @abstractmethod
    def refund(self, payment_id, refund_amount):
        pass

class RazorPayGateway(PaymentGateway):
    def __init__(self):
        self.attempts = {}
        self.lock = threading.Lock()

    def process(self, request: PaymentRequest):
        # Simulate a transient gateway failure on the first attempt.
        # Subsequent attempts succeed.
        with self.lock:
            attempt = self.attempts.get(request.idempotency_key,0) + 1
            self.attempts[request.idempotency_key] = attempt

        if attempt == 1:
            return PaymentResponse(f"Razorpay: {request.idempotency_key}", PaymentStatus.FAILED, "RazorPay: transient gateway error (attempt 1)")
        
        return PaymentResponse(f"Razorpay: {request.idempotency_key}", PaymentStatus.SUCCESS, "Razorpay: payment successful")

    def refund(self, payment_id, refund_amount):
        return Refund(payment_id, refund_amount, RefundStatus.SUCCESS)

class StripePaymentGateway(PaymentGateway):
    def process(self, request: PaymentRequest):
        return PaymentResponse(f"Stripe: {request.idempotency_key}", PaymentStatus.SUCCESS, "Stripe: payment successful")

    def refund(self, payment_id, refund_amount):
        return Refund(payment_id, refund_amount, RefundStatus.SUCCESS)

class PaymentGatewayDecorator(PaymentGateway):
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
        
class RetryPolicy(PaymentGatewayDecorator):
    # Decorator that adds retry behavior to any PaymentGateway.

    def __init__(self, gateway: PaymentGateway, max_attempts: int):
        super().__init__(gateway)
        self.max_attempts = max_attempts

    def process(self, request: PaymentRequest):
        last_response = None

        # Retry failed gateway responses up to max_attempts.
        for attempt in range(1, self.max_attempts+1):
            last_response = self.gateway.process(request)
            if last_response.payment_status == PaymentStatus.SUCCESS:
                return last_response

            print(f"Payment failed. Retrying... attempt {attempt}/{self.max_attempts}")

        return last_response
    
    def refund(self, payment_id, refund_amount):
        return self.gateway.refund(payment_id, refund_amount)

class IdempotencyManager:
    def __init__(self):
        self.cache = {}
        self.key_lock_map = {}
        self.lock = threading.Lock()

    def get_lock(self, idempotency_key):
        with self.lock:
            if idempotency_key not in self.key_lock_map:
                self.key_lock_map[idempotency_key]= threading.Lock()
            
            return self.key_lock_map[idempotency_key]

    def get_cached(self, idempotency_key):
        with self.lock:
            if idempotency_key not in self.cache:
                return None

            return self.cache[idempotency_key]

    def record(self,idempotency_key, response: PaymentResponse):
        with self.lock:
            self.cache[idempotency_key] = response       

class PaymentService:
    def __init__(self, gateway: PaymentGateway):
        self.gateway = gateway
        self.idempotency_manager = IdempotencyManager()
        self.payment_methods = {PaymentType.CARD: CardPaymentMethod(), PaymentType.UPI: UPIPaymentMethod(), PaymentType.NET_BANKING: NetbankingPaymentMethod()}

        self.payments = {}
        self.refunded_payments = set()

    def create_payment(self, request: PaymentRequest):

        # Acquire a lock specific to this idempotency key.
        # This prevents concurrent requests with the same key from charging the customer multiple times.

        lock = self.idempotency_manager.get_lock(request.idempotency_key)
        with lock:
            cached = self.idempotency_manager.get_cached(request.idempotency_key)
            if cached is not None:
                print(f"Duplicate response for idempotency key{request.idempotency_key}")
                return cached

            # Payment method validation is separated from gateway processing.
            payment_method= self.payment_methods.get(request.payment_type)

            if payment_method is None or not payment_method.validate(request):
                return PaymentResponse(None, PaymentStatus.FAILED, f"Validation failed for {request.payment_type.name}")

            response = self.gateway.process(request)

            self.idempotency_manager.record(request.idempotency_key,response)

            self.payments[response.payment_id] = (request,response)

            return response

    def refund_payment(self,payment_id):
        payment = self.payments.get(payment_id)

        if not payment:
            print("Invalid Payment")
            return None

        request, response = payment

        if response.payment_status != PaymentStatus.SUCCESS:
            return None

        lock = self.idempotency_manager.get_lock(payment_id)

        with lock:
            if payment_id not in self.refunded_payments:      
                refund = self.gateway.refund(payment_id, request.amount)

                if refund.refund_status == RefundStatus.SUCCESS:
                    self.refunded_payments.add(payment_id)

                return refund

            else:
                print("Payment already refunded")
                return None

if __name__=="__main__":
    service = PaymentService(RetryPolicy(RazorPayGateway(),3))
    print("Valid card payment but gateway failure")
    request1 = service.create_payment(PaymentRequest("User-1", PaymentType.CARD, "key-1", 250.0, {"Card Number": "1234567891234567"}))
    print(f"{request1}")

    print("\nSame idempotency key resubmitted (must not charge again):")
    request2 = service.create_payment(PaymentRequest("User-1", PaymentType.CARD, "key-1", 250.0, {"Card Number": "1234567891234567"}))

    print(f"{request2}")

    print("\nFirst refund call")
    refund1 = service.refund_payment(request1.payment_id)
    print(refund1)
    print("\nSecond refund call")
    refund2 = service.refund_payment(request1.payment_id)
    print(refund2)

    print("\nInvalid UPI id (missing '@'):")
    request3= service.create_payment(PaymentRequest("User-2",PaymentType.UPI,"key-2",300, {"UPI Id" : "user2UPI"}))
    print(f"{request3}")

    print("\nSwapping in Stripe for a net-banking payment (gateway is pluggable):")
    stripe_service = PaymentService(RetryPolicy(StripePaymentGateway(),2))
    request4 = stripe_service.create_payment(PaymentRequest("user-3",PaymentType.NET_BANKING, "key-4", 400, {"Bank code": "ICIC001"}))
    print(f"{request4}")