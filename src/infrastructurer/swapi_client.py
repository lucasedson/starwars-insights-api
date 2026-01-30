import httpx

class SwapiClient:
    def __init__(self):
        self.client = httpx.Client(base_url="https://swapi.dev/api")

    def get(self, path):
        return self.client.get(path)
    

if __name__ == "__main__":
    client = SwapiClient()
    response = client.get("/people/1")
    print(response.json())