from locust import HttpUser, task


class Http2User(HttpUser):
    @task
    def health(self) -> None:
        self.client.get("/health")
