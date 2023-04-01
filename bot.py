from json import load, decoder, dump
from random import choice
from typing import Optional, Dict, Tuple, Union, List
from os import path

import discord
from discord import app_commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
client: discord.Client = discord.Client(intents=intents, help_command=None, activity=discord.Game(name="/yerba"))
tree: app_commands.CommandTree = app_commands.CommandTree(client)


if not path.isfile("config.json"):
    with open("config.json", 'w', encoding="utf-8") as new_config_file:
        new_config_data: Dict[str, str] = {"token": "Enter your bot's token from Discord Dev Portal.",
                                           "lang": "Enter desired language ['pl', 'en']"}
        dump(new_config_data,
             new_config_file,
             indent=4)
        print("Please check the newly generated config file.")
        exit()


def load_config() -> Tuple[str, str]:
    with open("config.json") as config_file:
        config_data: Dict[str, str] = load(config_file)
        config_token: str = config_data["token"]
        config_language: str = config_data["lang"]
        return config_token, config_language


token, lang_code = load_config()


def load_language(code: str) -> Dict[str, str]:
    with open("languages.json") as lang_file:
        try:
            lang_data: Dict[str, Dict[str, str]] = load(lang_file)
            lang_dict: Dict[str, str] = lang_data[code]
        except decoder.JSONDecodeError:
            print("languages.json file is missing!")
            exit()
        except KeyError:
            print("Wrong language has been passed into config file!")
            exit()
        return lang_dict


lang = load_language(lang_code)


def load_data() -> Dict[str, Dict[str, Union[str, Dict[str, Dict[str, Dict[str, Union[str, List[int], List[str]]]]]]]]:
    with open("yerba.json") as data_file:
        try:
            yerba_data: Dict[str, Dict[str, Union[str, Dict[str, Dict[str, Dict[str, Union[str, List[int], List[str]]]]]]]] = load(data_file)
        except decoder.JSONDecodeError:
            print("yerba.json file is missing!")
            exit()
        return yerba_data


data = load_data()


async def create_embed(user: discord.Interaction.user, country: str, flavour: str, yerba: str) -> discord.Embed:
    embed: discord.Embed = discord.Embed(title=f"{lang['embed_title']} :mate:",
                                         color=discord.Color.from_rgb(*data["countries"][country]["style"]["color"]),
                                         timestamp=datetime.now(),
                                         description=f"{data['countries'][country]['style']['flag']}┇**{yerba} ({data['descriptors'][flavour]})**")
    embed.set_footer(text=user, icon_url=user.avatar.url)
    return embed


async def get_random_yerba() -> Tuple[str, str, str]:
    country: str = choice(list(data["countries"]))
    flavour: str = choice(list(data["countries"][country]["flavours"]))
    yerba: str = choice(data["countries"][country]["flavours"][flavour])
    return country, flavour, yerba


async def get_random_yerba_by_country(country: str) -> Tuple[str, str]:
    flavour: str = choice(list(data["countries"][country]["flavours"]))
    return flavour, choice(data["countries"][country]["flavours"][flavour])


async def get_random_yerba_by_flavour(flavour: str) -> Tuple[str, str]:
    country: str = choice(list(data["countries"]))
    return country, choice(data["countries"][country]["flavours"][flavour])


async def get_random_yerba_by_country_and_flavour(country: str, flavour: str) -> str:
    return choice(data["countries"][country]["flavours"][flavour])


@client.event
async def on_ready():
    await tree.sync()
    print("Bot is ready")


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.add_reaction("🧉")


@tree.command(name="yerba", description=lang["command_desc"])
@app_commands.describe(origin=lang["argument_desc_origin"],
                       taste=lang["argument_desc_flavour"])
@app_commands.choices(origin=[app_commands.Choice(name=lang[key.lower()],
                                                  value=key) for key in list(data["countries"])],
                      taste=[app_commands.Choice(name=lang[key],
                                                 value=key) for key in list(data["countries"]["Argentina"]["flavours"])])
@app_commands.rename(origin=lang["argument_name_origin"],
                     taste=lang["argument_name_flavour"])
async def send_random_yerba(interaction: discord.Interaction,
                            origin: Optional[app_commands.Choice[str]],
                            taste: Optional[app_commands.Choice[str]]):

    match bool(origin), bool(taste):
        case False, False:
            country, flavour, yerba = await get_random_yerba()
            embed: discord.Embed = await create_embed(interaction.user, country, flavour, yerba)
        case True, False:
            flavour, yerba = await get_random_yerba_by_country(origin.value)
            embed = await create_embed(interaction.user, origin.value, flavour, yerba)
        case False, True:
            country, yerba = await get_random_yerba_by_flavour(taste.value)
            embed = await create_embed(interaction.user, country, taste.value, yerba)
        case True, True:
            yerba = await get_random_yerba_by_country_and_flavour(origin.value, taste.value)
            embed = await create_embed(interaction.user, origin.value, taste.value, yerba)

    await interaction.response.send_message(embed=embed)


client.run(token=token)
