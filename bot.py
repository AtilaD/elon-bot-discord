import discord
import asyncio
import requests
from bs4 import BeautifulSoup
from discord.ext import tasks
from dotenv import load_dotenv
import os

# Carrega variáveis do arquivo .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))

intents = discord.Intents.default()
client = discord.Client(intents=intents)

def get_latest_tweet():
    url = "https://nitter.net/elonmusk"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    tweet_element = soup.find("div", class_="timeline-item")
    if tweet_element:
        content = tweet_element.find("div", class_="tweet-content")
        if content:
            return content.text.strip()
    return None

def read_last_tweet():
    if not os.path.exists("last_tweet.txt"):
        return None
    with open("last_tweet.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def write_last_tweet(tweet):
    with open("last_tweet.txt", "w", encoding="utf-8") as f:
        f.write(tweet)

@tasks.loop(seconds=60)
async def check_tweet():
    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if not channel:
        print("Canal não encontrado.")
        return

    latest_tweet = get_latest_tweet()
    last_tweet = read_last_tweet()

    if latest_tweet and latest_tweet != last_tweet:
        await channel.send(f"Novo tweet de Elon Musk:\n\n{latest_tweet}")
        write_last_tweet(latest_tweet)

@client.event
async def on_ready():
    print(f'Logado como {client.user}')
    check_tweet.start()

client.run(DISCORD_TOKEN)
