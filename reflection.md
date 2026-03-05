# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
It looked normal in the sense that it took correctly my guessed number and try to verified against the secret number. However, there were things that were odd, as I explain in the next answer.

- List at least two concrete bugs you noticed at the start  
  (for example: "the secret number kept changing" or "the hints were backwards").
  (1) Hints were working backwards
  (2) The Attempt counter was +1
  (3) The game didn't restart properly
  (4) The Enter button to submit my input wasn't working.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
Claude AI Assistant
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
One of the suggestions that was very obvious and easy to catch was the fix of the "HINT" function. It highlighted the error, show the fix, and explained properly before implementation
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).
When fixing the update_score function it made a change that wasn't correct and it lead to the score to be negative. I have to explain to him the problem and how to fix it

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
I double checked my work by implementing a two check process. The first check was me trying out the app, and the second test was using the test folder
- Describe at least one test you ran (manual or using pytest)
  and what it showed you about your code.
I tried the app 10 times with different parameters until it seemed okay to me  
- Did AI help you design or understand any tests? How?
Not really, the test file was pretty straightforward and I didn't need explanation. However, I did use AI to create the test data to be sure that I was covering edge cases and exploring new limitations

---

## 4. What did you learn about Streamlit and state?

- In your own words, explain why the secret number kept changing in the original app.
- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
Streamlit is what allow us to test our application as it were completely deployed but the locally form. Meaning that we can see it in our computer as we were the final user without the need to deploy it to the whole world.
- What change did you make that finally gave the game a stable secret number?
The glitch got fixed in my second iteration with Claude. However, I have to highlight that by nature the secret number should change with every time we reload the website
---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
Understand the code, its structure, and its functionality/limitations before going heavy on AI Tools. I feel like in this way I am ensuring that I understand what I am doing and can instruct with confidence the AI Tool
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
Maybe learn more about classes, functions, and Git/GitHub in general
- In one or two sentences, describe how this project changed the way you think about AI generated code.
Now I see AI tools like a code assistant that does not make the work for you but double check what you are doing and points out with precision when you are wrong and how you can fix it.
