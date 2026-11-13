from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException, Header, Body
from pydantic import BaseModel, Field
import functions

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Pydantic
class packagedetails(BaseModel):
    package_name: str
    destination: str
    weight: float = Field(gt=0)
    arrival_date: str

class packageupdate(BaseModel):
    package_name: str | None = None
    destination: str | None = None
    weight: float | None = None
    arrival_date: str | None = None    

class DispatchBatchDetails(BaseModel):
    destination: str
    vehicle: str
    package_ids: list[int]
    dispatch_status: str = "pending"   

class DispatchStatusDetails(BaseModel):
    dispatch_status: str     

@app.post("/login")
def login(username = Body(), password = Body()):
    token = functions.verify_login(username=username, password=password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid")
    return token

@app.post("/refresh")
def refresh(refresh_token = Header(None)):
    username = functions.verify_token(token=refresh_token, token_type = "refresh")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or refresh token")
    access_token = functions.create_token(username=username, token_type = "access")
    return {"access_token": access_token}

@app.post("/register_user")
def register_user(user_name = Body(), password = Body()):
    if functions.register_user(user_name=user_name, password=password):
        return{"message": "user registerd sucessfully"}
    raise HTTPException(status_code=400, detail="user already exists")

# E1 
@app.post("/packages")
def register_package(package: packagedetails, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expiry token")
    return functions.add_package( package.package_name,
        package.destination,
        package.weight,
        package.arrival_date)

# E2 
@app.get("/packages/{package_id}")
def get_package(package_id: int, token = Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expiry token")
    response = functions.get_package(package_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return response

# E3 
@app.patch("/packages/{package_id}")
def update_package(package: packageupdate, package_id: int, token = Header(None)):
    username = functions.verify_token(token=token, token_type = "access")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expiry token")
    if package.weight is not None and package.weight <= 0:
        raise HTTPException(status_code=422, detail="Incorrect weight")
    data = {}
    if package.package_name is not None:
        data["package_name"] = package.package_name
    if package.destination is not None:
        data["destination"] = package.destination
    if package.weight is not None:
        data["weight"] = package.weight
    if package.arrival_date is not None:
        data["arrival_date"] = package.arrival_date
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="No update details provided")
    response = functions.update_package(package_id, data)
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")
    if response == "already_dispatched":
        raise HTTPException(status_code=400, detail="Dispatched package cannot be updated")
    if response == "already_assigned":
        raise HTTPException(status_code=400, detail="Assigned package cannot be updated")
    return response

# E4 
@app.delete("/packages/{package_id}")
def delete_package(package_id: int, token = Header(None)):
    username = functions.verify_token(token=token, token_type = "access")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expiry token")
    response = functions.delete_package(package_id)
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")
    if response == "already_dispatched":
        raise HTTPException(status_code=400, detail="Dispatched package cannot be deleted")
    return {"message": "Package deleted successfully"}

# E5 
@app.get("/packages")
def get_packages(destination=None, status=None, arrival_date=None, token = Header(None)):
    username = functions.verify_token(token=token, token_type = "access")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expiry token")
    if status and status not in ["pending", "assigned", "dispatched"]:
        raise HTTPException(status_code=422, detail="Invalid package status")
    return functions.get_all_packages(destination, status, arrival_date)

# E6 
@app.get("/dispatch-batches")
def get_dispatch_batches(destination=None, vehicle=None, dispatch_status=None, token = Header(None)):
    username = functions.verify_token(token=token, token_type = "access")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expiry token")
    if dispatch_status and dispatch_status not in ["pending", "dispatched"]:
        raise HTTPException(status_code=422, detail="Invalid dispatch status")
    return functions.get_all_dispatch_batches(destination, vehicle, dispatch_status)

# E7 
@app.get("/warehouse/statistics")
def warehouse_statistics(token = Header(None)):
    username = functions.verify_token(token=token, token_type = "access")
    if not username:
        raise HTTPException(status_code = 401, detail = "Invalid or expiry token")
    return functions.get_warehouse_statistics()

# E8
@app.post("/dispatch-batches")
def create_dispatch_batch(package: DispatchBatchDetails, token=Header(None)):
    username = functions.verify_token(token=token, token_type="access")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid or expiry token")
    
    response = functions.create_dispatch_batch( package.destination,
        package.vehicle,
        package.package_ids,
        package.dispatch_status)
    if response == "package_not_found":
        raise HTTPException(status_code=404, detail="Package not found")
    if response == "already_dispatched":
        raise HTTPException(status_code=400, detail="Package already dispatched")
    if response == "already_assigned":
        raise HTTPException(status_code=400, detail="Package already assigned")
    if response == "destination_mismatch":
        raise HTTPException(status_code=400, detail="Destination does not match")
    if response == "no_packages":
        raise HTTPException(status_code=400, detail="No packages provided")
    return response

