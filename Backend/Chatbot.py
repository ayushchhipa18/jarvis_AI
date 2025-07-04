from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in the same language in which the question is asked. If it's in Hindi, reply in Hindi. If it's in English, reply in English. ***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

# Load existing chat history (only user/assistant messages)
try:
    with open(r"C:/windows_vscode/jarvis_AI/Data/ChatLog.json", "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(r"C:/windows_vscode/jarvis_AI/Data/ChatLog.json", "w") as f:
        dump(messages, f)


def RealtimeInformation():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed,\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours : {now.strftime('%M')} minutes : {now.strftime('%S')} seconds.\n"
    )


def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty = [line for line in lines if line.strip()]
    return "\n".join(non_empty)


def ChatBot(Query):
    """Send query to LLM and return real-time response."""

    try:
        # Load previous chat
        with open(r"C:/windows_vscode/jarvis_AI/Data/ChatLog.json", "r") as f:
            history = load(f)

        # Add user query to history (used only for response)
        temp_messages = [
            {"role": "system", "content": System},
            {"role": "system", "content": RealtimeInformation()},
            *history,
            {"role": "user", "content": Query},
        ]

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=temp_messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None,
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")

        # Save only user and assistant roles to history
        history.append({"role": "user", "content": Query})
        history.append({"role": "assistant", "content": Answer})

        with open(r"C:/windows_vscode/jarvis_AI/Data/ChatLog.json", "w") as f:
            dump(history, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "⚠️ Something went wrong."


if __name__ == "__main__":
    while True:
        user_input = input("Enter the question: ")
        print(ChatBot(user_input))
