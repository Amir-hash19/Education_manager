from locust import HttpUser, between, task
import random

class WebUser(HttpUser):
    wait_time = between(1,3)

    @task
    def list_bootcamp(self):
        self.client.get("/api/v1/bootcamps/all/list")


    @task
    def list_blogs(self):
        self.client.get("/api/v1/blogs")
            