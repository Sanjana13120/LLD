# There should be exactly one  instance of class and everyone should use the same instance.


class Logger:
    """ 
    Singleton Logger - Ensures only one shared Logger instance is created.
    """
    instance = None

    @classmethod    
    def get_instance(cls):
        
        if cls.instance is None:
            cls.instance = cls()
            print("Object Created")
        return cls.instance


if __name__=="__main__":
    logger1= Logger.get_instance()
    logger2= Logger.get_instance()
    logger3= Logger.get_instance()

#   Uncommenting the line below breaks the Singleton. Python cannot enforce a private constructor like Java.
#   Therefore, Logger() can still create a new object.
#   logger = Logger()

    print(logger1 is logger2)
    print(logger2 is logger3)
    print(logger3 is logger1)


    print(id(logger1))
    print(id(logger2))
    print(id(logger3))
    