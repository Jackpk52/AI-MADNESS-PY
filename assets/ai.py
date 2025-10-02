import os
from openai import AsyncOpenAI
import random
import asyncio
import aiohttp

# Initialize the OpenAI client with HuggingFace router
client = AsyncOpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv('HF_TOKEN'),
)

async def generate_ai_response(prompt):
    clean_prompt = prompt.replace('<@!?\\d+>', '').strip()
    
    if not clean_prompt:
        return "Hello! How can I help you today?"

    try:
        # Use the HuggingFace router with DeepSeek model - WITH TIMEOUT
        chat_completion = await asyncio.wait_for(
            client.chat.completions.create(
                model="deepseek-ai/DeepSeek-V3.1-Terminus:novita",
                messages=[
                    {
                        "role": "user",
                        "content": clean_prompt,
                    },
                ],
                max_tokens=100,  # Reduced from 150 to be faster
                temperature=0.7,
                stream=False  # Ensure no streaming
            ),
            timeout=15.0  # 15 second timeout
        )

        ai_response = chat_completion.choices[0].message.content
        
        if ai_response:
            return ai_response
        else:
            return generate_fallback_response(clean_prompt)

    except asyncio.TimeoutError:
        print("🤖 AI API Timeout - using fallback")
        return generate_fallback_response(clean_prompt)
    except Exception as error:
        print(f"🤖 AI API Error: {error}")
        
        # Handle specific errors
        error_str = str(error).lower()
        if any(word in error_str for word in ['quota', 'limit', 'overload']):
            return "⚠️ AI is busy right now! Try again in a moment."
        elif any(word in error_str for word in ['token', 'auth', 'key']):
            return "🔑 AI access issue. Using fallback mode."
        elif any(word in error_str for word in ['timeout', 'connect']):
            return "⏰ AI timeout! Using fallback response."
        else:
            return generate_fallback_response(clean_prompt)

# Smart fallback responses - ENHANCED
def generate_fallback_response(prompt):
    lower_prompt = prompt.lower()
    
    if any(word in lower_prompt for word in ['hello', 'hi', 'hey']):
        return random.choice([
            "👋 Hey there! What's up?",
            "Hello! How can I help you today?",
            "Hi! Ready to chat! 😊"
        ])
    elif 'how are you' in lower_prompt:
        return "I'm doing great! Ready to chat with you! How about you?"
    elif 'thank' in lower_prompt:
        return "You're welcome! 😊 Happy to help!"
    elif '?' in lower_prompt:
        return random.choice([
            "That's a great question! What do you think?",
            "Interesting question! I'd love to hear your thoughts.",
            "Hmm, that makes me curious. What's your take on it?"
        ])
    elif any(word in lower_prompt for word in ['bot', 'madness', 'ai']):
        return "🤖 That's me! AI Madness Bot - your friendly assistant!"
    
    responses = [
        "Interesting! Tell me more.",
        "I see what you mean! What else?",
        "Cool! What's on your mind?",
        "That's fascinating! Go on...",
        "I'm listening! Continue please.",
        "That's awesome! What next?",
        "Nice! What else should we talk about?",
        "Got it! What's your perspective?"
    ]
    
    return random.choice(responses)