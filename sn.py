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


# from fastapi import FastAPI, HTTPException, Header
# from pydantic import BaseModel
# import functions

# app = FastAPI()

# # Pydantic Model
# class packagedetails(BaseModel):
#     package_name: str
#     destination: str
#     weight: float
#     arrival_date: str

# # E1 - Register Package
# @app.post("/packages")
# def register_package(package: packagedetails, token=Header(None)):
#     username = functions.verify_token(token=token, token_type="access")
#     if not username:
#         raise HTTPException(status_code=401, detail="Invalid or expiry token")
#     if package.weight <= 0:
#         raise HTTPException(status_code=422, detail="Incorrect weight")
#     return functions.add_package( package.package_name,
#         package.destination,
#         package.weight,
#         package.arrival_date)


# from datetime import date
# from sqlalchemy.orm import Session

# # Package Details
# def package_details(package):
#     return {
#         "id": package.id,
#         "package_name": package.package_name,
#         "destination": package.destination,
#         "weight": package.weight,
#         "arrival_date": str(package.arrival_date),
#         "status": package.status,
#         "dispatch_batch_id": package.dispatch_batch_id
#     }

# # E1 - Add Package
# def add_package(package_name, destination, weight, arrival_date):
#     session = Session(engine)
#     package = Packages(
#         package_name=package_name,
#         destination=destination,
#         weight=weight,
#         arrival_date=date.fromisoformat(arrival_date),
#         status="pending")
#     session.add(package)
#     session.commit()
#     session.refresh(package)
#     response = package_details(package)
#     session.close()
#     return response
