from json import load, decoder, dump
from random import choice
from typing import Optional, Dict
from os import path

import discord
from discord import app_commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents, help_command=None, activity=discord.Game(name="/yerba"))
tree = app_commands.CommandTree(client)


if not path.isfile("config.json"):
    with open("config.json", 'w', encoding="utf-8") as config_file:
        config_data: Dict[str, str] = {"token": "Enter your bots token from Discord Dev Portal."}
        dump(config_data,
             config_file,
             indent=4)
        print("Please check the newly generated config file.")
        input()
        exit()


with open("config.json") as config_file:
    config_data = load(config_file)
    token = config_data["token"]


def load_data():
    with open("yerba.json") as data_file:
        try:
            yerba_data = load(data_file)
        except decoder.JSONDecodeError:
            yerba_data = {}
        return yerba_data


data = load_data()


async def create_embed(user, country, yerba):
    embed = discord.Embed(title="Losowa Yerba Mate :mate:",
                          color=discord.Color.from_rgb(*data[country]["style"]["color"]),
                          timestamp=datetime.now(),
                          description=f"{data[country]['style']['flag']}┇**{yerba}**")
    embed.set_footer(text=user, icon_url=user.avatar.url)
    return embed


async def get_random_yerba():
    country = choice(list(data))
    yerba = choice(data[country]["items"])
    return country, yerba


async def get_random_yerba_by_country(country):
    yerba = choice(data[country]["items"])
    return yerba


@client.event
async def on_ready():
    await tree.sync()
    print("Bot jest gotowy")


@tree.command(name="yerba", description="Wysyła losową Yerba Mate")
@app_commands.describe(origin="Opcjonalnie: Kraj z którego chcesz wylosować yerbę.")
@app_commands.choices(origin=[app_commands.Choice(name=key,
                                                  value=key) for key in list(data)])
@app_commands.rename(origin="kraj")
async def send_random_yerba(interaction, origin: Optional[app_commands.Choice[str]]):
    if not origin:
        country, yerba = await get_random_yerba()
        embed = await create_embed(interaction.user, country, yerba)
        await interaction.response.send_message(embed=embed)
        return
    yerba = await get_random_yerba_by_country(origin.value)
    embed = await create_embed(interaction.user, origin.value, yerba)
    await interaction.response.send_message(embed=embed)


client.run(token=token)
