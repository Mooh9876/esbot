import { useEffect, useState } from 'react'

function App() {
  const [health, setHealth] = useState('Checking backend...')
  const [sessions, setSessions] = useState([])
  const [activeSession, setActiveSession] = useState(null)
  const [messages, setMessages] = useState([])
  const [messageInput, setMessageInput] = useState('')
  const [quizTopic, setQuizTopic] = useState('')
  const [quiz, setQuiz] = useState(null)
  const [quizAnswer, setQuizAnswer] = useState('')
  const [quizFeedback, setQuizFeedback] = useState('')
  const [error, setError] = useState('')
  const [chatLoading, setChatLoading] = useState(false)

  async function apiRequest(path, options = {}) {
    const response = await fetch(`/api${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })

    if (!response.ok) {
      const body = await response.json().catch(() => ({}))

      let message = body.detail || `Request failed with status ${response.status}`

      if (Array.isArray(message)) {
        message = message.map((item) => item.msg).join(', ')
      }

      throw new Error(message)
    }

    if (response.status === 204) {
      return null
    }

    return response.json()
  }

  async function loadSessions() {
    try {
      const sessionData = await apiRequest('/sessions')
      setSessions(sessionData)
    } catch (err) {
      setError(err.message)
    }
  }

  async function checkHealth() {
    try {
      const result = await apiRequest('/health')
      setHealth(result.status === 'ok' ? 'Backend online' : 'Backend unavailable')
    } catch {
      setHealth('Backend unavailable')
    }
  }

  useEffect(() => {
    checkHealth()
    loadSessions()
  }, [])

  async function createSession() {
    setError('')

    try {
      const newSession = await apiRequest('/sessions', {
        method: 'POST',
      })

      setSessions((currentSessions) => [newSession, ...currentSessions])
      setActiveSession(newSession)
      setMessages([])
      setQuiz(null)
      setQuizFeedback('')
    } catch (err) {
      setError(err.message)
    }
  }

  async function selectSession(session) {
    setError('')
    setActiveSession(session)
    setQuiz(null)
    setQuizFeedback('')

    try {
      const messageData = await apiRequest(`/sessions/${session.id}/messages`)
      setMessages(messageData)
    } catch (err) {
      setError(err.message)
    }
  }

  async function sendMessage(event) {
    event.preventDefault()
    setError('')

    if (!activeSession) {
      setError('Please create or select a session first.')
      return
    }

    const content = messageInput.trim()

    if (!content) {
      setError('Message must not be empty.')
      return
    }

    setChatLoading(true)

    try {
      const assistantMessage = await apiRequest(
        `/sessions/${activeSession.id}/messages`,
        {
          method: 'POST',
          body: JSON.stringify({ content }),
        },
      )

      const userMessage = {
        id: `local-user-${Date.now()}`,
        content,
        role: 'user',
      }

      setMessages((currentMessages) => [
        ...currentMessages,
        userMessage,
        assistantMessage,
      ])

      setMessageInput('')
    } catch (err) {
      setError(err.message)
    } finally {
      setChatLoading(false)
    }
  }

  async function generateQuiz() {
    setError('')
    setQuiz(null)
    setQuizFeedback('')

    if (!activeSession) {
      setError('Please create or select a session first.')
      return
    }

    const topic = quizTopic.trim()

    if (!topic) {
      setError('Quiz topic must not be empty.')
      return
    }

    try {
      const quizData = await apiRequest(`/sessions/${activeSession.id}/quiz`, {
        method: 'POST',
        body: JSON.stringify({ topic }),
      })

      setQuiz(quizData.items[0] || null)
    } catch (err) {
      setError(err.message)
    }
  }

  async function submitQuizAnswer() {
    setError('')
    setQuizFeedback('')

    if (!activeSession || !quiz) {
      setError('Please generate a quiz first.')
      return
    }

    const answer = quizAnswer.trim()

    if (!answer) {
      setError('Answer must not be empty.')
      return
    }

    try {
      const result = await apiRequest(
        `/sessions/${activeSession.id}/quiz/${quiz.id}/answer`,
        {
          method: 'POST',
          body: JSON.stringify({ answer }),
        },
      )

      setQuizFeedback(result.feedback)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <main className="app">
      <header className="header">
        <div>
          <h1>ESBot</h1>
          <p>Learning assistant for software testing</p>
        </div>

        <span data-testid="health-status" className="health-status">
          {health}
        </span>
      </header>

      {error && (
        <div data-testid="error-banner" className="error-banner" role="alert">
          {error}
        </div>
      )}

      <section className="layout">
        <aside className="sidebar">
          <button
            data-testid="new-session-btn"
            className="primary-button"
            onClick={createSession}
          >
            New session
          </button>

          <h2>Sessions</h2>

          <div data-testid="session-list" className="session-list">
            {sessions.length === 0 && (
              <p className="muted-text">No sessions available.</p>
            )}

            {sessions.map((session) => (
              <button
                key={session.id}
                data-testid={`session-item-${session.id}`}
                className={
                  activeSession?.id === session.id
                    ? 'session-item active'
                    : 'session-item'
                }
                onClick={() => selectSession(session)}
              >
                Session #{session.id}
              </button>
            ))}
          </div>
        </aside>

        <section className="content">
          <section className="chat-panel">
            <h2>Chat</h2>

            <div data-testid="message-list" className="message-list">
              {!activeSession && (
                <p className="muted-text">
                  Create or select a session to start chatting.
                </p>
              )}

              {messages.map((message) => (
                <div
                  key={message.id}
                  data-testid={
                    message.role === 'user'
                      ? 'user-message'
                      : 'assistant-message'
                  }
                  className={
                    message.role === 'user'
                      ? 'message user-message'
                      : 'message assistant-message'
                  }
                >
                  <strong>
                    {message.role === 'user' ? 'You' : 'ESBot'}:
                  </strong>{' '}
                  {message.content}
                </div>
              ))}

              {chatLoading && (
                <p data-testid="chat-loading" className="muted-text">
                  ESBot is writing a response...
                </p>
              )}
            </div>

            <form className="message-form" onSubmit={sendMessage}>
              <label htmlFor="message-input">Your message</label>

              <textarea
                id="message-input"
                data-testid="message-input"
                value={messageInput}
                onChange={(event) => setMessageInput(event.target.value)}
                placeholder="Ask a question about software testing..."
                rows="4"
              />

              <button
                data-testid="send-message-btn"
                className="primary-button"
                type="submit"
              >
                Send message
              </button>
            </form>
          </section>

          <section className="quiz-panel">
            <h2>Quiz</h2>

            <label htmlFor="quiz-topic-input">Quiz topic</label>

            <input
              id="quiz-topic-input"
              data-testid="quiz-topic-input"
              value={quizTopic}
              onChange={(event) => setQuizTopic(event.target.value)}
              placeholder="For example: software testing"
            />

            <button
              data-testid="generate-quiz-btn"
              className="primary-button"
              onClick={generateQuiz}
            >
              Generate quiz
            </button>

            {quiz && (
              <div className="quiz-card">
                <p data-testid="quiz-question" className="quiz-question">
                  {quiz.question}
                </p>

                <label htmlFor="quiz-answer-input">Your answer</label>

                <input
                  id="quiz-answer-input"
                  data-testid="quiz-answer-input"
                  value={quizAnswer}
                  onChange={(event) => setQuizAnswer(event.target.value)}
                  placeholder="Enter your answer"
                />

                <button
                  data-testid="submit-answer-btn"
                  className="primary-button"
                  onClick={submitQuizAnswer}
                >
                  Submit answer
                </button>
              </div>
            )}

            {quizFeedback && (
              <p data-testid="quiz-feedback" className="quiz-feedback">
                {quizFeedback}
              </p>
            )}
          </section>
        </section>
      </section>
    </main>
  )
}

export default App