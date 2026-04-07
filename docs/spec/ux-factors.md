# ESBot – UX Factor Identification
## Exercise 3.1 | Software Testing Course – SoSe 2026

### 1. Clarity and Comprehensibility
**Definition**  
Clarity means that ESBot presents information in a way that doesn't require me to read it three times to get the point. This covers the chat layout, but more importantly, the language used by the AI. A response is clear if a user understands it immediately without needing to Google half the terms used in the explanation.

**Why it matters for ESBot users**  
As CS students, we usually turn to the bot when we are stuck on complex topics like mutation testing or formal verification. If the answer is just a massive "wall of text" without structure, it doesn't help—it just adds to the cognitive load. Since chat windows have limited space, the bot needs to get straight to the point instead of rambling.

**Example Interaction**  
A student asks: "Difference between black-box and white-box testing?"  
*Low Clarity*: A long, rambling paragraph mixing both terms together.  
*High Clarity*: A clear split using bullet points. First the definition ("testing against specs"), then a quick example ("checking a login field"), followed by the white-box section. This saves time and makes the info stick.

### 2. Feedback Quality
**Definition**  
Feedback here isn't just saying "Correct" or "Incorrect." It’s about pedagogical value. Good feedback explains the "why" and helps the user find their own mistake rather than just spoon-feeding the solution.

**Why it matters for ESBot users**  
ESBot is a learning tool, not just a search engine. If I take a quiz and get an answer wrong, seeing the right result without context doesn't help me for the exam. I need to understand why my logic was flawed. Quality feedback is the difference between actually learning a concept and just memorizing a sequence of clicks.

**Example Interaction**  
A student selects "Statement Coverage" for a question that describes "Branch Coverage."  
*Low Quality*: "Wrong. Branch Coverage was the correct answer."  
*High Quality*: "Not quite. Statement coverage only checks if every line of code was executed. Branch coverage goes further and checks if you took every path (like the 'else' case). Want to try the question again with that in mind?"

### 3. Trust and Transparency
**Definition**  
Since AI isn't perfect, the bot needs to be honest. Transparency means the system shows where its info comes from or admits when it’s unsure, instead of selling "hallucinations" as hard facts.

**Why it matters for ESBot users**  
Nothing is worse than studying for an exam with wrong information. Because LLMs occasionally make mistakes, we need to know when we can trust an answer 100% and when we should double-check the lecture slides. If the bot cites sources or flags uncertainty, it builds much more trust in the long run.

**Example Interaction**  
A student asks for a specific formula from the lecture.  
*Low Transparency*: "The formula is X." (Even though multiple versions exist).  
*High Transparency*: "Based on standard models, X is typically used. However, some courses use variant Y. You should check page 42 of your specific script to see which one your professor expects."

### 4. Learnability (of the tool)
**Definition**  
How fast can I figure out what the bot can actually do without reading a manual? A learnable system feels intuitive and guides me through the features (like chat, quizzes, or summaries) naturally.

**Why it matters for ESBot users**  
No one wants to spend time learning how to use a learning app. Students usually use the bot under time pressure. If I have to guess which command starts a quiz, I'll get frustrated quickly. The tool should basically explain itself as you go.

**Example Interaction**  
On the first launch, instead of just an empty text box, the bot shows three "quick start" suggestions:  
- "Explain a concept to me..."  
- "Start a quiz about..."  
- "Show my recent mistakes..."  

### 5. Error Tolerance and Recovery
**Definition**  
The system shouldn't crash or give cryptic errors if I make a typo or ask a vague question. It’s about "graceful failure"—guiding the user back to a productive state when things go wrong.

**Why it matters for ESBot users**  
We often type questions quickly, leading to typos or messy phrasing. If the bot just returns "Error 500" or "Input not recognized," the learning flow is broken. Even if the AI backend is down, the system should handle it in a way that doesn't feel like the whole app is broken.

**Example Interaction**  
*Input*: "testin stuff"  
*Low Tolerance*: "Command not recognized."  
*High Tolerance*: "It looks like you want to talk about testing! Did you want to start a quiz, or should I explain the different types of software tests for you?"
