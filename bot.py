import discord
import requests
import re
import os
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Fireworks AI API credentials
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY")
FIREWORKS_API_URL = "https://api.fireworks.ai/inference/v1/completions"

# Discord bot token
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set Discord bot permissions
intents = discord.Intents.default()
intents.message_content = True  # Required to read user messages

# Initialize the bot client
client = discord.Client(intents=intents)

# Dictionary to store user timestamps for rate limiting
user_timestamps = {}

# List of profane and toxic words (can be expanded)
BAD_WORDS = [
    "fuck", "shit", "bitch", "asshole", "damn", "dick", "piss", "fucking", "motherfucker",
    "cunt", "fag", "retard", "nigger", "dyke", "slut", "whore", "bollocks", "arsehole"
]

def clean_toxic_language(text):
    """Censors toxic language, reduces character spam, and softens aggressive tone."""
    
    # Censor bad words
    for word in BAD_WORDS:
        pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
        text = pattern.sub("[censored]", text)

    # Reduce excessive character repetitions (e.g. aaaa -> aaa)
    text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)

    # Softening all-uppercase shouting
    def fix_caps(m):
        word = m.group()
        return word.capitalize() if len(word) > 2 else word
    text = re.sub(r'\b[A-Z]{3,}\b', fix_caps, text)

    # Replace aggressive phrases
    replacements = {
        r"fuck off": "[censored]",
        r"shut up": "[please be kind]",
        r"bitch": "[censored]",
        r"dogshit": "bad",
        r"idiot": "a bit careless",
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text.strip()

def generate_reply(message_text):
    """Sends a prompt to Fireworks AI and returns a cleaned reply."""
    headers = {
        "Authorization": f"Bearer {FIREWORKS_API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f'Reply to this Discord message in a helpful, friendly tone: "{message_text}"'

    payload = {
        "model": "accounts/sentientfoundation/models/dobby-unhinged-llama-3-3-70b-new",
        "prompt": prompt,
        "max_tokens": 240,
        "temperature": 0.7,
        "top_p": 0.9
    }

    try:
        response = requests.post(FIREWORKS_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        reply = response.json().get("choices", [{}])[0].get("text", "").strip()
        cleaned_reply = clean_toxic_language(reply)
        return cleaned_reply if cleaned_reply else "Sorry, I didn't understand that."
    except Exception as e:
        print(f"❌ Fireworks API Error: {e}")
        return "Something went wrong 😞"

@client.event
async def on_ready():
    print(f"✅ Logged in as: {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # Ignore bot's own messages

    if message.content.startswith("!"):
        return  # Skip command messages

    user_id = str(message.author.id)
    now = time.time()

    # Rate limiting: allow one response per user per 60 seconds
    if user_id in user_timestamps:
        elapsed = now - user_timestamps[user_id]
        if elapsed < 60:
            await message.channel.send(f"⏳ Please wait {int(60 - elapsed)}s before asking again.")
            return

    user_timestamps[user_id] = now  # Update last message time

    reply = generate_reply(message.content)
    await message.channel.send(reply)

# Run the bot
client.run(DISCORD_BOT_TOKEN)
