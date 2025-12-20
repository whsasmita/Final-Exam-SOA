from locust import HttpUser, task


class Http1User(HttpUser):
    @task
    def health(self) -> None:
        self.client.get("/health")
