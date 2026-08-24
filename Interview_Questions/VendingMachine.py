"""
# Objective: Design a Vending Machine

1. Funtional Requirements:

1) User should be able to select products.
2) System supports multiple products and quantites. 
3) system should dispense the product and return change if necessary
4) User can insert coins. The machine verifies that the inserted amount is sufficient for the selected product.
5) System should keep track of inventory.
6) System should display error when product out of stock/insufficien cash
7) System should support other payment options as well  -  — future extension

2. Non - Funtional Requirements:
1) Concurrency - Multiple requests may happen concurrently, but inventory and payment state must remain consistent.
2) Data consistency -- a successful purchase should correctly update inventory and payment/change state.
3) Purchase/payment operation should be atomic.

3. Identigy core entities

VendingMachine  (orchestrates the purchase flow)
    - current_balance, machine_state, selected_product
    - Inventory

    - select_item()
    - insert_coin()
    - dispense_item()
    - refund_balance()

VendingMachineState (ABC)
    - select_item()
    - insert_coin()
    - dispense_item()
    - refund_balance()

IdleState(VendingMachineState)
ItemSelectedState(VendingMachineState)
MoneyInsertedState(VendingMachineState)
DispensingState(VendingMachineState)

Product (product information)
    - product_id
    - price
    - product_name

Inventory
    - items = {product_id: Product}
    - stock = {product_id: quantity}

    - add_item(product_id, product, quantity)
    - remove_item(product_id)
    - get_item(product_id)
    - get_quantity(product_id)
    - is_product_available(product_id)

Coin
    - ONE
    - TWO
    - FIVE
    - TEN


Payment 
    - UPI/Card- future extensions

4. Identify relationship

VendingMachine HAS-A Inventory
VendingMachine HAS-A current transaction state
VendingMachine uses Product
VendingMachine uses Coin

Payment  → future extension for UPI/Card/etc.

5. Coding
"""

# Concurrency:
# - Current implementation assumes a single-threaded vending machine.
# - In a concurrent environment, state-changing operations such as select_item(), insert_coin(), dispense_item(), and refund_balance() should be protected using a reentrant lock (RLock).
# - This ensures balance, inventory, and transaction state remain consistent.
# - The purchase flow should be atomic so inventory deduction and payment state changes happen as one operation.

from abc import ABC, abstractmethod
from enum import Enum

class Coin(Enum):
    ONE = 1
    TWO = 2
    FIVE = 5
    TEN = 10

class Product:
    def __init__(self, product_id, product_name, price):
        self.product_id = product_id
        self.product_name = product_name
        self.price = price

class Inventory:
    def __init__(self):
        self.items = {}
        self.stock = {}

    def is_product_available(self,product_id):
        return product_id in self.items and self.stock[product_id] > 0

    def add_item(self, product_id, product, quantity):
        if product_id in self.items:
            self.stock[product_id] += quantity
        else:
            self.items[product_id] = product
            self.stock[product_id] = quantity

    def remove_item(self, product_id):
        if not self.is_product_available(product_id):
            return False
        
        self.stock[product_id] -=1
        return True

    def get_item(self,product_id):
        return self.items.get(product_id)

    def get_quantity(self, product_id):
        return self.stock.get(product_id,0)

    def print_inventory(self):
        print("\n--- Inventory ---")

        for product_id, product in self.items.items():
            quantity = self.stock[product_id]
            status = "AVAILABLE" if quantity > 0 else "OUT OF STOCK"

            print(f"{product_id}: {product.product_name} | " f"Price: Rs {product.price} | "f"Quantity: {quantity} | {status}")

class VendingMachineState(ABC):
    def __init__(self,machine):
        self.machine = machine

    @abstractmethod
    def insert_coin(self, coin):
        pass
    @abstractmethod
    def select_item(self, product_id):
        pass
    @abstractmethod
    def dispense_item(self):
        pass
    @abstractmethod
    def refund_balance(self):
        pass
    
class IdleState(VendingMachineState):

    def insert_coin(self, coin):
        print("Please select an item before inserting money...")
        return False

    def select_item(self, product_id):
        if product_id not in self.machine.inventory.items:
            print("Invalid product")
            return False
        
        if not self.machine.inventory.is_product_available(product_id):
            print("OUT OF STOCK!!!")
            return False
        
        product = self.machine.inventory.get_item(product_id)

        self.machine.selected_product = product
        self.machine.machine_state = ItemSelectedState(self.machine)
        print(f"Item selected: {product.product_name}")
        return True
    
    def dispense_item(self):
        print("No item selected....")
        return False
    
    def refund_balance(self):
        print("No money to refund...")
        return False

class ItemSelectedState(VendingMachineState):
    def select_item(self, product_id):
        print("Item already selected. Please insert coin.")
        return False
    
    def insert_coin(self, coin):
        self.machine.add_balance(coin.value)
        print(f"Coin inserted: Rs {coin.value}") 

        self.machine.machine_state = MoneyInsertedState(self.machine)

    def dispense_item(self):
        print("Please insert sufficient coins.")
        return False
    
    def refund_balance(self):
        refund = self.machine.refund_balance()  
        self.machine.reset()
        self.machine.machine_state= IdleState(self.machine)
        return refund

class MoneyInsertedState(VendingMachineState):
    def select_item(self, product_id):
        print("Item already selected. Please complete.")
        return False
    
    def insert_coin(self, coin):
        if self.machine.balance >= self.machine.selected_product.price:
            print("Sufficient money inserted. Please dispense the item.")
            return False
        
        self.machine.add_balance(coin.value)
        print(f"Coin inserted: Rs {coin.value}")

        if self.machine.balance >= self.machine.selected_product.price:
            print("Sufficient money inserted. Please dispense the item.")
            self.machine.machine_state = DispensingState(self.machine)

        return True      
    
    def dispense_item(self):
        if self.machine.balance < self.machine.selected_product.price:
            print("Insufficient coins")
            return False

        self.machine.machine_state = DispensingState(self.machine)
        return self.machine.dispense_item()
    
    def refund_balance(self):
        refund = self.machine.refund_balance()  
        self.machine.reset()
        self.machine.machine_state= IdleState(self.machine)
        return refund

class DispensingState(VendingMachineState):
    def select_item(self, product_id):
        print("Currently dispensing. Please wait.")
        return False
    
    def insert_coin(self, coin):
        print("Currently dispensing. Please wait.")
        return False
    
    def dispense_item(self):
        product = self.machine.selected_product
        if not self.machine.inventory.remove_item(product.product_id):
            print("Unable to dispense item")
            self.machine.refund_balance()
            self.machine.reset()
            self.machine.machine_state = IdleState(self.machine)
            return False

        change = self.machine.balance - product.price
        print(f"Dispensing {product.product_name}")
        print(f"Change returned = Rs {change}")

        self.machine.reset()
        self.machine.machine_state = IdleState(self.machine)

        return change
    
    def refund_balance(self):
        print("Dispensing in progress. Refund not allowed.")
        return False

class VendingMachine:
    def __init__(self,inventory: Inventory):
        self.inventory = inventory
        self.balance = 0
        self.selected_product = None
        self.machine_state = IdleState(self)

    def add_item(self,product_id, product_name, price, quantity):
        product = Product(product_id, product_name, price)
        self.inventory.add_item(product_id,product,quantity)
        return product
        
    def select_item(self,product_id):
        return self.machine_state.select_item(product_id)

    def insert_coin(self,coin):
        return self.machine_state.insert_coin(coin)

    def dispense_item(self):
        return self.machine_state.dispense_item()

    def refund_balance(self):
        refund = self.balance
        print(f"Refunding balance: Rs {refund}")
        self.reset()
        self.machine_state = IdleState(self)
        self.balance = 0
        return refund

    def reset(self):
        self.selected_product = None
        self.balance = 0

    def add_balance(self,amount):
        self.balance += amount

    def print_inventory(self):
        self.inventory.print_inventory()


def main():

    vending_machine =  VendingMachine(Inventory())
    vending_machine.add_item("A1","Coke", 25 , 3)
    vending_machine.add_item("A2", "Pepsi", 25, 2)
    vending_machine.add_item("B1", "Water", 30, 1)

    vending_machine.print_inventory()

    print("\n--- Step 1: Select an item ---")
    vending_machine.select_item("A1")

    # Insert coins
    print("\n--- Step 2: Insert coins ---")
    vending_machine.insert_coin(Coin.TEN)
    vending_machine.insert_coin(Coin.TEN)
    vending_machine.insert_coin(Coin.FIVE)

    #Dispense item
    print("\n--- Step 3: Dispense item ---")
    vending_machine.dispense_item()

    vending_machine.print_inventory()

    #Select another item
    print("\n--- Step 4: Select another item ---")
    vending_machine.select_item("B1")

    #insert coins
    vending_machine.insert_coin(Coin.TEN)
    vending_machine.insert_coin(Coin.TEN)

    # Try to dispense the product
    print("\n--- Step 6: Dispense and return change ---")
    vending_machine.dispense_item()

    vending_machine.print_inventory()

    print("\n--- Step 6: choose water again---")
    vending_machine.select_item("B1")

    print("\n--- Step 8: Select another item not in list---")
    vending_machine.refund_balance()
    vending_machine.select_item("Z1")

    

    

if __name__=="__main__":
    main()