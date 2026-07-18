'''Encapsulation is bundling data and methods together and restricting direct access to internal data.
Use methods to modify data instead of direct access.'''

class BankAccount:
    def __init__(self,balance):
        self.__balance=balance

    def deposit(self,amount):
        self.__balance+=amount

    def withdraw(self,amount):
        if amount<=self.__balance:
            self.__balance-=amount
        else:
            print("Insuffient balance")

    def getbalance(self):
        return self.__balance

acc=BankAccount(1000)
acc.deposit(500)
acc.withdraw(200)
print(f"Balance= {acc.getbalance()}")


#Output - 1300