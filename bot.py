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
    with open("config.json", 'w', encoding="utf-8") as new_config_file:
        new_config_data: Dict[str, str] = {"token": "Enter your bots token from Discord Dev Portal.",
                                           "lang": "Enter desired language ['pl', 'en']"}
        dump(new_config_data,
             new_config_file,
             indent=4)
        print("Please check the newly generated config file.")
        exit()


def load_config():
    with open("config.json") as config_file:
        config_data = load(config_file)
        config_token = config_data["token"]
        config_language = config_data["lang"]
        return config_token, config_language


token, lang_code = load_config()


def load_language(code):
    with open("languages.json") as lang_file:
        try:
            lang_data = load(lang_file)
            lang_dict = lang_data[code]
        except decoder.JSONDecodeError:
            print("languages.json file is missing!")
            exit()
        except KeyError:
            print("Wrong language has been passed into config file!")
            exit()
        return lang_dict


lang = load_language(lang_code)


def load_data():
    with open("yerba.json") as data_file:
        try:
            yerba_data = load(data_file)
        except decoder.JSONDecodeError:
            print("yerba.json file is missing!")
            exit()
        return yerba_data


data = load_data()


async def create_embed(user, country, yerba):
    embed = discord.Embed(title=f"{lang['embed_title']} :mate:",
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
    return choice(data[country]["items"])


@client.event
async def on_ready():
    await tree.sync()
    print("Bot is ready")


@tree.command(name="yerba", description=lang["command_desc"])
@app_commands.describe(origin=lang["argument_desc"])
@app_commands.choices(origin=[app_commands.Choice(name=lang[key.lower()],
                                                  value=key) for key in list(data)])
@app_commands.rename(origin=lang["argument_name"])
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
