from locust import HttpUser, task, between

class ESBotPerformanceTest(HttpUser):
    # Simulate user think time between requests (1 to 3 seconds)
    wait_time = between(1, 3)
    
    def on_start(self):
        """Setup: Create a dedicated test session to be used by the GET tasks."""
        self.session_id = None
        with self.client.post("/sessions", catch_response=True, name="POST /sessions (setup)") as response:
            if response.status_code == 201:
                # Extract session ID from the response (default to 1 if parsing fails for any reason)
                self.session_id = response.json().get("id", 1) 
            else:
                response.failure(f"Failed to create session: {response.status_code}")

    @task(1)
    def health_check(self):
        """Goal: Verify API handles health checks."""
        self.client.get("/health", name="GET /health")

    @task(2)
    def create_and_list_sessions(self):
        """Goal: Simulate creating and listing sessions."""
        self.client.post("/sessions", name="POST /sessions")
        self.client.get("/sessions", name="GET /sessions")

    @task(4)
    def session_details_and_messages(self):
        """Goal: Simulate a user fetching their session context and message history."""
        if self.session_id:
            self.client.get(f"/sessions/{self.session_id}/messages", name="GET /sessions/{id}/messages")

    def on_stop(self):
        """Teardown: Delete the session created on start to avoid state cascade."""
        if self.session_id:
            # Use catch_response to prevent teardown failures from crashing the user
            with self.client.delete(f"/sessions/{self.session_id}", catch_response=True, name="DELETE /sessions/{id} (teardown)") as response:
                if not response.ok:
                    print(f"Warning: Teardown failed for session {self.session_id}: {response.status_code}")