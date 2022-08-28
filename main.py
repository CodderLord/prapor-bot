import discord
import re
from discord.ext import commands
from config import settings
from lists_conf import possible_hello, possible_hello_for_new_user, url, url_gallery, url_gallery_end
from random import randint
import urllib.parse
from req import get_soup
from bs4 import BeautifulSoup
import time
import datetime
import sqlite3
#import youtube_dl
import os

db = sqlite3.connect('time_voice_users.db')

intents = discord.Intents.all()
intents.members = True
intents.voice_states = True
#intents.presences = True
#intents.message_content = True
bot = commands.Bot(command_prefix=settings["prefix"], intents=intents)
client = discord.Client(intents=intents)


#@bot.command
#async def play(ctx, url: str):
#	song_there = os.path.isfile("song.mp3")
#	try:
#		if song_there:
#			os.remove("song.mp3")
#	except PermissionError:
#		return
#	voice_channel = discord.utils.get(ctx.guild.voice_channels, name="music")
#	await voice_channel.connect()
#	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
#	ydl_opts = {
#		'format': 'bestaudio/best',
#		'postprocessors': [{
#			'key': 'FFmpegExtractAudio',
#			'preferredcodec': 'mp3',
#			'preferredquality': '192',
#		}],
#	}
#	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#		ydl.download([url])
#	for file in os.listdir("./"):
#		if file.endswith(".mp3"):
#			os.rename(file, "song.mp3")
#	voice.play(discord.FFmpegPCMAudio('song.mp3'))
#
#
#@bot.command
#async def leave(ctx):
#	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
#	if voice.is_connected():
#		await voice.disconnect()
#	else:
#		pass
#
#
#@bot.command
#async def pause(ctx):
#	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
#	if voice.is_playing():
#		voice.pause()
#	else:
#		pass
#
#
#@bot.command
#async def resume(ctx):
#	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
#	if voice.is_paused():
#		voice.resume()
#	else:
#		pass
#
#
#@bot.command
#async def stop(ctx):
#	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
#	voice.stop()

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
		result_bot_help = re.search(r"прапор помоги с квестом .?", str(message.content), re.I)
		if result_hello is not None:
			await message.channel.send(f'{possible_hello[randint(0, len(possible_hello)-1)]}{message.author}')
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
			try:
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
			except AttributeError:
				await message.channel.send("К сожалению ничего не смог найти.")
				return
"""https://discord.com/channels/1000370246428921909/1000370247553011773 ---- моой
https://discord.com/channels/993850749236813915/993850749677211679 --- нащ"""


@bot.event
async def on_member_join(member):
	global id_massage, mes
	for ch in bot.get_guild(member.guild.id).channels:
		if ch.id == 993850749677211679:
			await bot.get_channel(ch.id).send(f"{possible_hello_for_new_user[randint(0, len(possible_hello_for_new_user)-1)]}{member.name}")
	await member.create_dm()
	await member.dm_channel.send(f'{possible_hello[randint(0, len(possible_hello)-1)]}{member.name}\n'
		f'Я могу порыться в документах, поискать что-то о интересующих тебя квестах\nДля этого просто напиши мне, или в специальный чат "Для новеньких --> Квесты прапор". \nПрапор помоги " и добавь " с квестом [Название квеста, можно и примерное]"')
	massage = await member.dm_channel.send(
		"Ну а теперь, напиши мне количество своего опыта в Таркове\n**Нож - меньше 400 часов**\n**Меч - от 400 до 1400 часов**\n**Два меча - от 1400 часов**\nКликни на нужную рекацию для указания кол. часов.\nЭто нужно для выдачи роли.")
	await massage.add_reaction("🔪")
	await massage.add_reaction("🗡️")
	await massage.add_reaction("⚔️")
	guild = bot.get_guild(993850749236813915)
	base_roles = discord.utils.get(guild.roles, name="Бродяга")
	await member.add_roles(base_roles)
	mes = massage
	id_massage = massage.id
	

@bot.event
async def on_member_remove(member):
	channel = bot.get_channel(1013337671394922546)
	await channel.send(f"{member} ушёл из сервера.")
	
	
@bot.event
async def on_raw_reaction_add(payload):
	try:
		ourMessageID = id_massage
		if ourMessageID == payload.message_id:
			guild = bot.get_guild(993850749236813915)
			base_roles = discord.utils.get(guild.roles, name="Бродяга")
			member = discord.utils.get(guild.members, id=payload.user_id)
			emoji = payload.emoji.name
			if emoji == "🔪":
				await member.remove_roles(base_roles)
				role = discord.utils.get(guild.roles, name="Новобранец")
				await member.add_roles(role)
			if emoji == "🗡️":
				await member.remove_roles(base_roles)
				role = discord.utils.get(guild.roles, name="Солдат")
				await member.add_roles(role)
				await member.dm_channel.send(
					"Если хотите влиться в клан и стать Модератором клана - пишите Администраторам или модерам клана.")
			if emoji == "⚔️":
				await member.remove_roles(base_roles)
				role = discord.utils.get(guild.roles, name="Ветеран")
				await member.add_roles(role)
				await member.dm_channel.send(
					"Прошаренный да?\nНу смотри, соклановцам всегда помощь нужна.Если хочешь им как-то помочь можешь стать шерпом клана.\nДля этого обратись к Админу клана, заму, или модераторам.\nМы всегда будем рады.")
				await member.dm_channel.send(
					"Если хотите влиться в клан и стать Модератором клана - пишите Администраторам или модерам клана.")
			await mes.delete(delay=None)
	except NameError:
		pass
	
	
#@bot.event
#async def on_voice_state_update(member, before, after):
#	print(f"member: \n{member}")
#	print(f"before: \n{before.requested_to_speak_at}")
#	print(f"after: \n{after.requested_to_speak_at}")

bot.run(settings['token'])
