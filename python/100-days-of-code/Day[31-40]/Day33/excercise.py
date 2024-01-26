import requests

# response = requests.get(url="http://api.open-notify.org/iss-now.json")

# data = response.json()
# print(data)

parameters = {
    "lat": 50.023870,
    "lng": 19.931260,
    "formatted": 0,
}
response = requests.get(url="https://api.sunrise-sunset.org/json", params=parameters)
response.raise_for_status()

print(response.json())