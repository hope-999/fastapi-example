# tests/locustfile.py
from locust import HttpUser, task, between

class FastAPIUser(HttpUser):
    wait_time = between(0.5, 2)
    
    @task(3)
    def get_heroes(self):
        self.client.get("/heroes")
    
    @task(1)
    def create_hero(self):
        self.client.post("/heroes", json={
            "name": "Test Hero",
            "secret_name": "Test Secret",
            "age": 30
        })
    
    @task(2)
    def get_hero_with_team(self):
        self.client.get("/heroes/1/with-team")
