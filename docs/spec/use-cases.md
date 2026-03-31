# Use Cases
## Use Case Diagram
![Use Case Diagram](../../assets/UseCases.png)

## Use Case UC-001
Use Case ID: UC-001  
Title: Chat with ESBot  
Primary Actor: User  
Stakeholders and Interests:
  - User: Wants to ask questions and receive accurate, contextualized answers to learn and practice course content
  - System Owner: Wants the system to process requests efficiently, provide correct answers, and maintain session data securely
  - Admin: Wants the system to log interactions and maintain AI integration properly

Preconditions:
  - User has registered and is logged in
  - Chat interface is available
  - External AI (LLM) is operational

Trigger:
  - User types a question or prompt into the chat interface

Main Success Scenario:
  1. User opens the chat interface
  2. User types a question or prompt related to course material
  3. User submits the input
  4. ESBot validates the input
  5. ESBot sends the prompt to the External AI (LLM)
  6. LLM generates a contextualized answer
  7. ESBot receives the generated answer
  8. ESBot displays the answer to the User
  9. ESBot stores the conversation in the database
 10. User continues the conversation or ends the session

Postconditions:
  - User receives a contextualized answer
  - Conversation is stored persistently for future retrieval

Extensions (Alternate Flows):
  - 5a. LLM Request Fails:
    - 5a1. ESBot notifies the user of a temporary issue
    - 5a2. System retries the request or logs the error for admin review

  - 4a. Invalid Input:
    - 4a1. ESBot displays error messages or guidance
    - 4a2. User corrects and resubmits the input

Special Requirements:
  - Responses should be generated within 2 seconds
  - User data must be stored securely
  - Chat interface must be intuitive and support multiple concurrent users

Frequency of Use:
  - High frequency (daily use by multiple students)

## Use Case UC-002

## Use Case UC-003

## Use Case UC-004

## Use Case UC-005

## Use Case UC-006

## Use Case UC-007
