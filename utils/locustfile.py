from locust import HttpUser , task



class FirstLocust(HttpUser):
    @task
    def hello_world(self):
        self.client.get('user/movieslist/')