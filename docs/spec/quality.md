# ESBot – Quality Model

## 1. Selected Quality Aspects (ISO 25010)

### 1.1 Usability
Goal: Easy interaction for students  
Metric: Task completion time < 10 seconds  
Measurement: User testing  

---

### 1.2 Performance Efficiency
Goal: Fast response time  
Metric: < 2 seconds  
Measurement: Load testing  

---

### 1.3 Reliability
Goal: Stable system  
Metric: 99% uptime  
Measurement: Monitoring  

---

### 1.4 Maintainability
Goal: Easy to extend and modify  
Metric: Low code complexity  
Measurement: Static code analysis  

---

## 2. Quality Model Example

Factor: Performance  
→ Criteria: Response Time  
→ Metric: < 2 seconds  
→ Measurement: Automated tests  

---

## 3. Testability

To ensure testability, the system must include:

- Modular architecture (frontend, backend, database)
- Separation of concerns
- Dependency injection
- Mocking of AI services
- Automated testing:
  - Unit tests
  - Integration tests
  - End-to-end tests
- Continuous Integration (CI)
