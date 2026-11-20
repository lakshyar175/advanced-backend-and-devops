import requests 

URL=("http://127.0.0.1:8000")
user_credential={"user_name":"Lucky","password":"12345", "user_type": "admin"}
# response = requests.post(url=URL+"/register",json=user_credential)
# print(response.status_code)
# print(response.json())

response = requests.post(url=URL+"/login",json=user_credential)
print(response.status_code)
print(response.json())
access_token = response.json()["access_token"]
refresh_token = response.json()["refresh_token"]

header = {"token": access_token}
# response = requests.get(url=URL+"/packages", headers=header )
# print(response.status_code)
# print(response.json())

# package_id = 1
# response = requests.get(url=URL + f"/packages/{package_id}", headers=header)
# print(response.status_code)
# print(response.json())


# package_id = 1
# update_data = {"destination": "Chennai"}
# response = requests.patch(url=URL + f"/packages/{package_id}", json=update_data, headers=header)
# print(response.status_code)
# print(response.json())

# package_id = 1
# update_data = {"destination": "Chennai"}
# response = requests.delete(url=URL + f"/packages/{package_id}", headers=header)
# print(response.status_code)
# print(response.json())

# package_id = 2
# response = requests.get(URL + "/dispatch-batches", headers=header)
# print(response.status_code)
# print(response.json())


response = requests.post(URL + "/dispatch-batches", headers=header)
print(response.status_code)
print(response.json())


# response = requests.get(URL + "/warehouse/statistics", headers=header)
# print(response.status_code)
# print(response.json())