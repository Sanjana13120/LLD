# ================================================================================================================================
# Builder design pattern is a creational design pattern that allows to construct complex objects step by step. It separates the object construction process from
# the final representation of the object

# When to use:
# - When object has many optional parameters.
# - When constructor becomes too complex.
# - When we want readable object creation using method chaining.

# The Builder pattern mainly consists of:
# 1. Builder: Responsible for storing the object configuration and constructing the product step by step. It hides the complexity of object creation and provides a controlled way to build the final object.
#
# 2. Setter methods: Setter methods configure different properties of the object. Returning "self" enables method chaining (fluent interface), making object creation more readable:
#       HouseBuilder()
#           .set_bedrooms(4)
#           .set_garage(True)
#
# 3. Build method: The build() method completes the construction process and returns the final product object. It can also perform validation before creating the object if required.

# Example:

# HouseBuilder()
#     .set_bedrooms(4)
#     .set_garage(True)
#     .build()

# This creates a House object without needing a large constructor.

# =================================================================================================================================

class House:
    def __init__(self, builder):
        self.bedrooms=builder.bedrooms
        self.bathrooms=builder.bathrooms
        self.garage=builder.garage
        self.garden=builder.garden
        self.swimmingpool=builder.swimmingpool

    def __str__(self):
        return (f"House(bedrooms={self.bedrooms},"
                f"bathrooms={self.bathrooms},"
                f"garage={self.garage},"
                f"garden={self.garden},"
                f"swimmingpool={self.swimmingpool})")

    
class HouseBuilder:
    def __init__(self):
        self.bedrooms=0
        self.bathrooms=0
        self.garage=False
        self.garden=False
        self.swimmingpool=False

    def set_bedrooms(self, bedrooms: int) -> "HouseBuilder":
        self.bedrooms = bedrooms
        return self

    def set_bathrooms(self, bathrooms:int) -> "HouseBuilder":
        self.bathrooms=bathrooms
        return self

    def set_garage(self, garage:bool) -> "HouseBuilder":
        self.garage=garage
        return self

    def set_garden(self,garden:bool) -> "HouseBuilder":
        self.garden=garden
        return self

    def set_swimmingpool(self,swimmingpool:bool) -> "HouseBuilder":
        self.swimmingpool=swimmingpool
        return self

    def build(self):
          return House(self)

if __name__=="__main__":
      house= (HouseBuilder()
              .set_bedrooms(4)
              .set_bathrooms(1)
              .set_garage(True)
              .set_swimmingpool(True)
              .build()
      )
      print(house)