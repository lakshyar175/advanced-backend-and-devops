from fastapi import FastAPI, HTTPException
import functions

app = FastAPI()
# @app.get("/")
# def hello():
#     return {"message": "Welcome to Warehouse Dispatch Management System"}

# E1 - Register Package
@app.post("/packages")
def register_package(package_name: str, destination: str, weight: float, arrival_date: str):
    if weight <= 0:
        raise HTTPException(status_code=422, detail="Incorrect weight")
    return functions.add_package(package_name, destination, weight, arrival_date)

# E2 - Get Package
@app.get("/packages/{package_id}")
def get_package(package_id: int):
    response = functions.get_package(package_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Package not found")
    return response

# E3 - Update Package
@app.patch("/packages/{package_id}")
def update_package(package_id: int, package_name=None, destination=None, weight=None, arrival_date=None):
    if weight is not None and weight <= 0:
        raise HTTPException(status_code=422, detail="Incorrect weight")
    data = {}
    if package_name is not None:
        data["package_name"] = package_name
    if destination is not None:
        data["destination"] = destination
    if weight is not None:
        data["weight"] = weight
    if arrival_date is not None:
        data["arrival_date"] = arrival_date
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

# E4 - Delete Package
@app.delete("/packages/{package_id}")
def delete_package(package_id: int):
    response = functions.delete_package(package_id)
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Package not found")
    if response == "already_dispatched":
        raise HTTPException(status_code=400, detail="Dispatched package cannot be deleted")
    return {"message": "Package deleted successfully"}

# E5 - Get All Packages
@app.get("/packages")
def get_packages(destination=None, status=None, arrival_date=None):
    if status and status not in ["pending", "assigned", "dispatched"]:
        raise HTTPException(status_code=422, detail="Invalid package status")
    return functions.get_all_packages(destination, status, arrival_date)

# E6 - Get Dispatch Batches
@app.get("/dispatch-batches")
def get_dispatch_batches(destination=None, vehicle=None, dispatch_status=None):
    if dispatch_status and dispatch_status not in ["pending", "dispatched"]:
        raise HTTPException(status_code=422, detail="Invalid dispatch status")
    return functions.get_all_dispatch_batches(destination, vehicle, dispatch_status)

# E7 - Warehouse Statistics
@app.get("/warehouse/statistics")
def warehouse_statistics():
    return functions.get_warehouse_statistics()

# E8 - Create Dispatch Batch
@app.post("/dispatch-batches")
def create_dispatch_batch(destination: str, vehicle: str, package_ids: str, dispatch_status: str = "pending"):
    ids = []
    for package_id in package_ids.split(","):
        ids.append(int(package_id))
    response = functions.create_dispatch_batch(
        destination, vehicle, ids, dispatch_status)
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

# Update Dispatch Status
@app.patch("/dispatch-batches/{batch_id}")
def update_dispatch_status(batch_id: int, dispatch_status: str):
    if dispatch_status not in ["pending", "dispatched"]:
        raise HTTPException(status_code=422, detail="Invalid dispatch status")
    response = functions.update_dispatch_status(batch_id, dispatch_status)
    if response == "not_found":
        raise HTTPException(status_code=404, detail="Dispatch batch not found")
    return response


@app.post("/login")
def login(username:str, password:str):
    token = functions.verify_login(username=username, password=password)
    if token is None:
        raise HTTPException(status_code=401, detail="Invalid")
    return{"token": token}

