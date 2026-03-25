# backend/app/services/chat_service.py
from groq import Groq
import os
from dotenv import load_dotenv
from app.services.rag_service import search

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_chat_response(messages, system_prompt=None):
    # Extract the last user message for RAG search
    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            content = m.get("content", "")
            last_user_msg = content if isinstance(content, str) else str(content)
            break

    relevant_data = search(last_user_msg)
    context = "\n".join(relevant_data)

    print("USER:", last_user_msg)
    print("CONTEXT:", context[:200])

    default_system = (
        "You are a helpful AI assistant for NareshIT, a software training institute. "
        "Answer the user's question using the context provided from the NareshIT website. "
        "Be concise, friendly, and professional. "
        "If the context doesn't fully answer the question, say so and suggest calling +91 8179191999."
    )

    if context and "Not available" not in context and "No data" not in context:
        # Inject RAG context into the first user message
        augmented_messages = []
        injected = False
        for m in messages:
            if m.get("role") == "user" and not injected:
                augmented_messages.append({
                    "role": "user",
                    "content": f"Context from NareshIT website:\n{context}\n\nUser Question:\n{m['content']}"
                })
                injected = True
            else:
                augmented_messages.append(m)
        messages_to_send = augmented_messages
    else:
        messages_to_send = messages

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt or default_system},
            *messages_to_send
        ]
    )

    return response.choices[0].message.content