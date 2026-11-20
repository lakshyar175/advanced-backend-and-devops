# Pydantic is a Python library used for data validation and data parsing.
        # DV --> checks whether the given data follows the rules or requirements    
        # DP --> converts the input data into the required data type or structured format 

#  what is pydantic model?
#  it is a class that inherits from basemodel. It allows to define data shapes with type annotations and automatically handles: 
                                # --> validation, --> conversion, --> Error handling

# why do we need pydantic?
# so for the current problem statement we have a package with 2 details name and weight where if a user gives weight as twenty in text but we defined it should be in int/float so to avoid this problem we use pydantic.
            #   we can think pydantic as a security checker at the entrance of our application, so here it checks the info before allowing the application to use it. 

# from pydantic import BaseModel      #so here we are importing basemodel from the pydantic library
# class Package(BaseModel):   #so here we are creating a class called package
#     name: str
#     weight: float
# p1 = Package(name="Laptop", weight="2.5")
# print(p1)
# #         output: name="Laptop", weight=2.5
# p2 = Package(name="Phone", weight="one")
# print(p2)


#  what is hashing  
# salt 

#  rquest library help us in testing 