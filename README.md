<img width="1230" alt="image" src="https://github.com/sezaras85/Sentient-ai/blob/main/sentient%20resim.png" />


# Sentient AI Dobby Discord Bot

This is a simple Discord chatbot using Fireworks AI's **Dobby-70B** model.

## Features

- Uses Sentient's Dobby model (`dobby-unhinged-llama-3-3-70b-new`)
- Friendly, filtered replies
- Basic profanity filter
- Async Discord client

 


1. Get an API Key from Firework AI
   
 ```bash
1. Go to the [Firework AI](https://firework.ai) website.
2. Log in to your account or create a new account.
3. Go to the **API Keys** section and create a new API key.
4. Save the generated API key in a safe place.

   ```

2. Creating a Discord Bot (Developer Portal)

```bash
Go to Discord Developer Portal.
https://discord.com/developers

“New Application” → name your bot.

From the left menu “Bot” → “Add Bot” → Yes, do it!

You will see the Bot Token here → copy it (keep it private).
*Don't forget to save your Discor_Bot_Token

```

3. Install dependencies:
  
```bash
  pip install discord.py requests

```

4. Generate Python Code
   
```bash
   nano bot.py
```
5. enter your own keys FIREWORKS_API_KEY = "YOUR_FIREWORKS_API_KEY" and DISCORD_BOT_TOKEN = "YOUR_DISCORD_BOT_TOKEN"

write code save it with ctrl+O.

```bash
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

```
6. Run the bot

```bash
 python3 bot.py

```


8. Discord enable required permissions
   
```bash
Go to discord developer page
 https://discord.com/developers/applications

Activate the following 3 settings in the “Privileged Gateway Intents” section on the bottom left:

-Message Content Intent (can read user messages)

-Presence Intent (optional, for online status)

-Server Members Intent (optional, if member information is required)
```

8.Invite Bot to Your Server (OAuth2)

```bash
Go to the “OAuth2 → URL Generator” tab on the left menu.

Select the following boxes:

Scopes: ✅ bot

Bot Permissions:

✅ Send Messages

✅ Read Message History

✅ View Channels

✅ Read Messages/View Channels

✅ Mention Everyone (if you want)

Copy the generated URL at the bottom of the page and paste it into your browser.

Invite the bot to your server.

```
