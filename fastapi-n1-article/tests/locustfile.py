# tests/locustfile.py
from locust import HttpUser, task, between

class N1DemoUser(HttpUser):
    wait_time = between(0.5, 2)
    
    @task(1)
    def test_naive(self):
        self.client.get("/heroes/naive")
    
    @task(3)
    def test_selectinload(self):
        self.client.get("/heroes/selectinload")
    
    @task(2)
    def test_joinedload(self):
        self.client.get("/heroes/joinedload")
    
    @task(1)
    def test_with_team(self):
        self.client.get("/heroes/1/with-team")
