import discord
import re
from discord.ext import commands
from config import settings
from lists_conf import possible_hello, people_helpers, url, url_gallery, url_gallery_end
from random import randint
import urllib.parse
from req import get_soup
from bs4 import BeautifulSoup
import time
import sys


intents = discord.Intents.all()
bot = commands.Bot(command_prefix=settings["prefix"], intents=intents)
client = discord.Client(intents=intents)


@bot.command()
async def die_on_bot(ctx):
	print("Прапор вылетел с дискорда")
	sys.exit()
	

@bot.event
async def on_ready():
	print(f'{settings["bot"]} залетел в Дискорд.')


@bot.event
async def on_message(message):
	if message.author == client.user:
		return
	else:
		message.content = message.content.lower()
		result_hello = re.search(r"всем привет", str(message.content), re.I)
		result_help = re.search(r".?\sпомо[чьщ]\s?.?", str(message.content), re.I)
		result_live = re.search(r"есть кто живой.?", str(message.content), re.I)
		result_bot_help = re.search(r"прапор помоги с квестом .?", str(message.content), re.I)
		if result_hello is not None:
			await message.channel.send(f'{possible_hello[randint(0, len(possible_hello)-1)]}{message.author}')
			return
		if result_live is not None:
			await message.channel.send(f"")
			return
		if result_help is not None:
			await message.channel.send(f"Помочь могут постоянные шерпы клана - {people_helpers}")
			return
		if result_bot_help is not None:
			await message.channel.send("Сейчас поищу в бумагах, может найду что нибудь.")
			result_message = str(message.content).replace(f"прапор помоги с квестом ", '')
			request = get_soup((url + urllib.parse.quote(result_message)))
			request_gallery = get_soup((url_gallery + urllib.parse.quote(result_message) + url_gallery_end))
			try:
				result_url_gallery = BeautifulSoup(request_gallery.text, "html.parser")
				result_url_gallery = result_url_gallery.find(class_="unified-search__result__header").find("a").get("href")
			except AttributeError:
				await message.channel.send("К сожалению ничего не смог найти.")
				return
			result_search_url_gallery = get_soup(result_url_gallery)
			result_search_gallery = BeautifulSoup(result_search_url_gallery.text, "html.parser")
			result_search_gallery = result_search_gallery.find(class_="gallery mw-gallery-packed")
			result_search_table = BeautifulSoup(request.text, "html.parser")
			result_table_href = result_search_table.find(class_="block block-system clearfix").find("a").get("href")
			request_end_link = get_soup(result_table_href)
			result_end_link = BeautifulSoup(request_end_link.text, "html.parser")
			result = result_end_link.find(class_="inside panels-flexible-region-inside panels-flexible-region-tankpanel-center-inside panels-flexible-region-inside-last").text
			table_info = result.replace('\n\n\n\n', '\n').strip()
			target = result_end_link.find(class_="panel-pane pane-entity-field pane-node-field-target").text
			await message.channel.send(f"Вот что сумел найти по твоему запросу, {message.author}:")
			await message.channel.send(table_info)
			await message.channel.send(target)
			try:
				block_end_target = result_end_link.find(class_="block block-entity-field tank-type-data2 clearfix").text
				await message.channel.send(block_end_target)
			except AttributeError:
				pass
			try:
				result_search_gallery = result_search_gallery.find_all("a")
				for result_href in result_search_gallery:
					await message.channel.send(result_href.get("href"))
					time.sleep(0.5)
			except AttributeError:
				pass
			return


@bot.event
async def on_member_join(member):
	await member.create_dm()
	await member.dm_channel.send(f'{possible_hello[randint(0, len(possible_hello)-1)]}{member.name}\n'
		f'Я могу помочь тебе с выполнением всех квестов, новоприбывший\nДля этого просто напиши мне, или в общий чат '
		f'"Прапор помоги " и добавь " с квестом [Название квеста, можно и примерное]" если помощь нужна именно с квестом'
		f'\nЕсли ничего не нашлось, попробуй перефразировать, '
		f'или обратиться к моей поддержке, может у меня уже с глазами что или кто с моих доки посеял"')
bot.run(settings['token'])
