Feature: Graceful handling of AI service failures
  As a student using ESBot
  I want the system to handle AI service outages gracefully
  So that I receive a clear fallback message instead of a crash

  Background:
    Given the student "carol@example.com" is registered and logged in

  Scenario: Happy path – AI service recovers after a transient failure
    Given the AI provider fails on the first call but succeeds on retry
    And the student is on the chat interface
    When the student sends the message "Explain polymorphism"
    Then the student receives an explanation containing "Polymorphism allows objects of different types to be treated uniformly"
    And the message appears in the conversation history

  Scenario: Error path – AI service is completely unavailable
    Given the AI provider is unavailable
    And the student is on the chat interface
    When the student sends the message "Explain polymorphism"
    Then the student sees the error "AI service is currently unavailable. Please try again later."
    And no message appears in the conversation history
