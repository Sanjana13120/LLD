# ================================================================================================================================
# Facade Design Pattern is a structural design pattern that provides a simplified interface to a complex subsystem of classes.
#
# Instead of the client interacting with multiple classes directly, it interacts with a single facade class that coordinates all subsystem operations.
#
# When to use:
# - When a system has many complex subsystems.
# - When clients should not know the internal implementation details.
# - When we want to provide a simple API over a complicated workflow.
# - When we want to reduce dependencies between client code and subsystems.
#
# Example: Online shopping order placement.
#
# Without Facade: Client has to understand the complete ordering process.
# Client needs to call:
# 1. UserService.validate_user()
# 2. InventoryService.check_inventory()
# 3. PaymentService.pay()
# 4. NotificationService.send()
#
# With Facade: Client only calls: OrderFacade.place_order()  --> The facade internally manages all required services.

# Components:
# 1. Facade: Provides a simple interface to the client and coordinates subsystem calls.
#    Example: OrderFacade
#
# 2. Subsystems: Existing classes that perform individual tasks.
#    Example: UserService/ InventoryService/ PaymentService/ NotificationService
#
# 3. Client: Uses the facade instead of directly interacting with subsystems.
#    Example: order.place_order()
#
# ================================================================================================================================


class UserService:
    def validate_user(self):
        print("User validated")

class InventoryService:
    def check_inventory(self):
        print("Inventory checked")

class PaymentService:
    def pay(self):
        print("Payment completed")

class NotificationService:
    def send(self):
        print("Notification sent")

class InvoiceService:
    def generate_invoice(self):
        print("Invoice generated")

class OrderFacade:
    def __init__(self):
        self.user_service=UserService()
        self.inventory_service =InventoryService()
        self.payment_service=PaymentService()
        self.invoice_service=InvoiceService()
        self.notification_service=NotificationService()

    def place_order(self):
        print("Processing order....")

        self.user_service.validate_user()
        self.inventory_service.check_inventory()
        self.payment_service.pay()
        self.invoice_service.generate_invoice()
        self.notification_service.send()

        print("Order created successfully!")
        
if __name__=="__main__":
    order=OrderFacade()
    order.place_order()