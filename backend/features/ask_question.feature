Feature: Ask a course question
  As a student using ESBot
  I want to ask questions about course material
  So that I receive a structured, contextualized explanation

  Background:
    Given the AI provider is a stub that returns deterministic responses
    And the student "alice@example.com" is registered and logged in

  Scenario: Happy path – student asks a valid course question
    Given the student is on the chat interface
    When the student sends the message "What is the difference between unit tests and integration tests?"
    Then the student receives an explanation containing "Unit tests verify individual components in isolation"
    And the message appears in the conversation history

  Scenario: Error path – student submits an empty message
    Given the student is on the chat interface
    When the student sends an empty message
    Then the student sees the error "Message must not be empty"
    And no message appears in the conversation history
