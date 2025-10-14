from locust import HttpUser, task, between



class QuickstartUser(HttpUser):
    def on_start(self):
        response = self.client.post("/api/v1/login", json={"email":"testemail@email.com","password":"123456789"})

        access_token = response.json()["access_token"]
        self.client.headers = {"Authorization": f"Bearer {access_token}"}

        


    @task
    def user_list(self):
        self.client.get("/users")
