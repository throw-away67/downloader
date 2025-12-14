import discord
import asyncio
import requests
from bs4 import BeautifulSoup
import os

URL = "https://auto.bazos.cz" #for example
TOKEN = "token"
CHANNEL_ID = 12345
KEYWORDS = ["keywords"]
CHECK_INTERVAL = 1800
SEEN_FILE = os.path.join(os.path.dirname(__file__), "seen_posts.txt")

intents = discord.Intents.default()


class Crawler(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if os.path.exists(SEEN_FILE):
            with open(SEEN_FILE, "r") as f:
                self.seen_posts = set(line.strip() for line in f if line.strip())
        else:
            self.seen_posts = set()

    def save_seen_post(self, url: str):
        self.seen_posts.add(url)
        with open(SEEN_FILE, "a") as f:
            f.write(url + "\n")

    async def setup_hook(self):
        self.bg_task = asyncio.create_task(self.check())

    async def check(self):
        await self.wait_until_ready()
        channel = self.get_channel(CHANNEL_ID)

        while not self.is_closed():
            try:
                for keyword in KEYWORDS:
                    search_url = (
                        f"{URL}/inzeraty/{keyword}/"
                    )
                    response = requests.get(
                        search_url,
                        headers={"User-Agent": "Mozilla/5.0"},
                        timeout=10
                    )
                    soup = BeautifulSoup(response.text, "html.parser")

                    posts = soup.select("div.inzeraty > div")

                    for post in posts:
                        try:
                            link_tag = post.select_one("h2.nadpis a")
                            if not link_tag:
                                continue

                            url = URL + link_tag["href"]
                            title = link_tag.get_text(strip=True)

                            if url not in self.seen_posts:
                                self.save_seen_post(url)
                                if channel:
                                    await channel.send(f"new post with keyword: **{keyword}**: **{title}**\n{url}")
                        except Exception as e:
                            print(f"error processing a post: {e}")

            except Exception as e:
                print("error while checking:", e)

            await asyncio.sleep(CHECK_INTERVAL)


client = Crawler(intents=intents)
client.run(TOKEN)
