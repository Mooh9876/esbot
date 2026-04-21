Feature: Generate a quiz for a topic
  As a student using ESBot
  I want to request a quiz on a specific course topic
  So that I can practice and test my understanding

  Background:
    Given the AI provider is a stub that returns deterministic responses
    And the student "bob@example.com" is registered and logged in

  Scenario: Happy path – student requests a quiz on a valid topic
    Given the student is on the chat interface
    When the student sends the message "Generate a quiz about software testing"
    Then the student receives a quiz with at least 1 question
    And the first question reads "What does TDD stand for?"
    And the quiz appears in the conversation history

  Scenario: Error path – student requests a quiz with an unsupported or blank topic
    Given the student is on the chat interface
    When the student sends the message "Generate a quiz about "
    Then the student sees the error "Quiz topic must not be empty"
    And no message appears in the conversation history
