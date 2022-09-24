import re
import nextcord
from nextcord.ext import commands
from nextcord import slash_command
from config import settings
from lists_conf import possible_hello, possible_hello_for_new_user, user_groups
from random import randint
# import urllib.parse
# from req import get_soup
# from bs4 import BeautifulSoup
import time
import sqlite3
from copy import deepcopy
# import datetime
# import youtube_dl
# import os

try:
	db_voice = sqlite3.connect('/home/inviking/prapor-bot/time_voice_users.db')
	db_quests = sqlite3.connect('/home/inviking/prapor-bot/prapor_info.db')
except sqlite3.OperationalError:
	db_voice = sqlite3.connect('time_voice_users.db')
	db_quests = sqlite3.connect('prapor_info.db')
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=settings["prefix"], intents=intents)
client = nextcord.Client(intents=intents)
serverID = 993850749236813915

all_quests = []


"""@bot.command
async def play(ctx, url: str):
	song_there = os.path.isfile("song.mp3")
	try:
		if song_there:
			os.remove("song.mp3")
	except PermissionError:
		return
	voice_channel = discord.utils.get(ctx.guild.voice_channels, name="music")
	await voice_channel.connect()
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	ydl_opts = {
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}
	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		ydl.download([url])
	for file in os.listdir("./"):
		if file.endswith(".mp3"):
			os.rename(file, "song.mp3")
	voice.play(discord.FFmpegPCMAudio('song.mp3'))


@bot.command
async def leave(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_connected():
		await voice.disconnect()
	else:
		pass


@bot.command
async def pause(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_playing():
		voice.pause()
	else:
		pass


@bot.command
async def resume(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	if voice.is_paused():
		voice.resume()
	else:
		pass


@bot.command
async def stop(ctx):
	voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
	voice.stop()"""


def create_table_quests_in_db():
	db_quests.execute("""CREATE TABLE IF NOT EXISTS quests(
						id INTEGER PRIMARY KEY AUTOINCREMENT ,
						name_quest VARCHAR(40) ,
						how_take VARCHAR(20) ,
						target TEXT ,
						win TEXT ,
						help_img TEXT
						)
						""")
	
	
def create_table_voice_in_db():
	db_voice.execute("""CREATE TABLE IF NOT EXISTS voice_active(
						id INTEGER PRIMARY KEY AUTOINCREMENT ,
						id_user INTEGER ,
						name_user VARCHAR(100) ,
						active_in_sec INTEGER
						)
						""")
	
	
@bot.command()
async def show_online(ctx):
	list_online = {}
	args = db_voice.execute(f"SELECT name_user, active_in_sec FROM voice_active ORDER BY active_in_sec")
	for name, active in args:
		list_online[name] = int((active/60)/60)
	await ctx.send(list_online)
	
	
@bot.command()
async def invite(ctx, member: nextcord.Member = None):
	guild = bot.get_guild(993850749236813915)
	try:
		await member.add_roles(nextcord.utils.get(guild.roles, name=user_groups[f'{ctx.author}']))
	except KeyError:
		pass


@bot.command()
async def re_invite(ctx, member: nextcord.Member = None):
	guild = bot.get_guild(993850749236813915)
	try:
		await member.remove_roles(nextcord.utils.get(guild.roles, name=user_groups[f'{ctx.author}']))
	except KeyError:
		pass


@bot.event
async def on_ready():
	print(f'{settings["bot"]} залетел в Дискорд.')
	create_table_quests_in_db()
	create_table_voice_in_db()
	extract_db()


@bot.event
async def on_message(message):
	if message.author == client.user:
		return
	await bot.process_commands(message)
	channel = message.channel
	if channel.id == 994848589627006986 or channel.id == 995325196644921395 or channel.id == 994234317054152774 or channel.id == 993926689769922570 or channel.id == 994942461610831944:
		await message.add_reaction("👍")
		await message.add_reaction("🔥")
		await message.add_reaction("😎")
		await message.add_reaction("👎")
		return
	else:
		message.content = message.content.lower()
		result_hello = re.search(r"всем привет", str(message.content), re.I)
		result_bot_help = re.search(r"прапор помоги с квестом .?", str(message.content), re.I)
		if result_hello is not None:
			await message.channel.send(f'{possible_hello[randint(0, len(possible_hello)-1)]}{message.author}')
			return
		if result_bot_help is not None:
			quests = deepcopy(all_quests)
			await message.channel.send("Сейчас поищу в бумагах, может найду что нибудь.")
			result_message = str(message.content).replace(f"прапор помоги с квестом ", '')
			target = None
			win = None
			help_img = None
			param_max = len(result_message.replace(" ", ''))
			name_quest_user = list(
				result_message.lower().replace(" ", '').replace(".", '').replace("-", '').replace("?", '').replace("!", ''))
			for i in quests:
				copy_i = i.copy()
				param = 0
				param_quest_max = len(i)
				for b in name_quest_user:
					if param >= param_max - 2:
						try:
							if b == i[-1]:
								if param_quest_max <= param_max + 4:
									result = ''.join(copy_i)
									quest_result = db_quests.execute(f"SELECT * FROM quests WHERE name_quest = '{result}'")
									for id_result_quest, name_quest, how_take, target, win, help_img in quest_result:
										target = target
										win = win
										help_img = help_img
									try:
										tr = int(i[-1])
										break
									except ValueError:
										break
						except IndexError:
							pass
					if b in i:
						param += 1
						i.remove(b)
			all_win = ''
			try:
				all_win = win.strip().split('\n')
			except AttributeError:
				pass
			try:
				await message.channel.send(f'{str(target.strip())}')
			except AttributeError:
				await message.channel.send('К сожалению в документах по запросу ничего не нашлось.')
				return
			try:
				await message.channel.send(f'{str(win.strip())}')
			except nextcord.errors.HTTPException:
				try:
					for w in all_win:
						await message.channel.send(f'{str(w.strip())}')
						time.sleep(1)
				except nextcord.errors.HTTPException:
					pass
			cl_img = help_img.replace('[', '').replace(']', '').replace("'", '').split(',')
			for im in cl_img:
				time.sleep(3)
				await message.channel.send(f'{str(im)}')
"""https://discord.com/channels/1000370246428921909/1000370247553011773 ---- моой
https://discord.com/channels/993850749236813915/993850749677211679 --- нащ"""


@bot.event
async def on_member_join(member):
	global id_massage, mes
	for ch in bot.get_guild(member.guild.id).channels:
		if ch.id == 993850749677211679:
			await bot.get_channel(ch.id).send(f"{possible_hello_for_new_user[randint(0, len(possible_hello_for_new_user)-1)]}{member.mention}")
	await member.create_dm()
	await member.dm_channel.send(f'{possible_hello[randint(0, len(possible_hello)-1)]}{member.mention}\n'
		f'Я могу порыться в документах, поискать что-то о интересующих тебя квестах\nДля этого просто напиши мне, или в специальный чат "Для новеньких --> Квесты прапор". \nПрапор помоги " и добавь " с квестом [Название квеста, можно и примерное]"')
	massage = await member.dm_channel.send(
		"Ну а теперь, напиши мне количество своего опыта в Таркове\n**Нож - меньше 300 часов**\n**Меч - от 300 до 1000 часов**\n**Два меча - от 1000 часов**\n**Бомба - от 3000 часов**\nКликни на нужную рекацию для указания кол. часов.\nЭто нужно для выдачи роли.")
	await massage.add_reaction("🔪")
	await massage.add_reaction("🗡️")
	await massage.add_reaction("⚔️")
	await massage.add_reaction("💣")
	guild = bot.get_guild(993850749236813915)
	base_roles = nextcord.utils.get(guild.roles, name="Бродяга")
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
			base_roles = nextcord.utils.get(guild.roles, name="Бродяга")
			member = nextcord.utils.get(guild.members, id=payload.user_id)
			emoji = payload.emoji.name
			if emoji == "🔪":
				await member.remove_roles(base_roles)
				role = nextcord.utils.get(guild.roles, name="Новобранец")
				await member.add_roles(role)
			if emoji == "🗡️":
				await member.remove_roles(base_roles)
				role = nextcord.utils.get(guild.roles, name="Солдат")
				await member.add_roles(role)
				await member.dm_channel.send(
					"Если хотите влиться в клан и стать Модератором клана - пишите Администраторам или модерам клана.")
			if emoji == "⚔️":
				await member.remove_roles(base_roles)
				role = nextcord.utils.get(guild.roles, name="Ветеран")
				await member.add_roles(role)
				await member.dm_channel.send(
					"Прошаренный да?\nНу смотри, соклановцам всегда помощь нужна.Если хочешь им как-то помочь можешь стать шерпом клана.\nДля этого обратись к Админу клана, заму, или модераторам.\nМы всегда будем рады.")
				await member.dm_channel.send(
					"Если хотите влиться в клан и стать Модератором клана - пишите Администраторам или модерам клана.")
			if emoji == "💣":
				await member.remove_roles(base_roles)
				role = nextcord.utils.get(guild.roles, name="Воин будущего")
				await member.add_roles(role)
				await member.dm_channel.send(
					"Прошаренный да?\nНу смотри, соклановцам всегда помощь нужна.Если хочешь им как-то помочь можешь стать шерпом клана.\nДля этого обратись к Админу клана, заму, или модераторам.\nМы всегда будем рады.")
				await member.dm_channel.send(
					"Если хотите влиться в клан и стать Модератором клана - пишите Администраторам или модерам клана.")
			await mes.delete(delay=None)
	except NameError:
		pass


def extract_db():
	db_data = db_quests.execute("SELECT id, name_quest FROM quests")
	for data in db_data:
		id_in_db, name_quest = data
		all_quests.append(list(
			name_quest.lower().replace(" ", '').replace(".", '').replace("-", '').replace("?", '').replace("!", '').replace(
				"(квест)", '').replace("(МР133)", '').replace("(АКС74У)", '').replace("(MP5)", '').replace("M4A1)", '').replace(
				"(ДВЛ10)", '').replace("(R11RSASS)", '').replace("(RemingtonM870)", '').replace("(АКМ)", '').replace("(АКС74Н)",'').replace(
				"(АК105)", '').replace("(АСВал)", '').replace("(АК102)", '').replace("(SIGMPX)", '').replace("(АКМН)", '').replace(
				"(M1A)", '').replace("(M4A1)", '')))
				
				
voice_dct = {}


def export_voice_data_for_data_base(data):
	db_voice.execute('INSERT INTO voice_active VALUES(null,?,?,?)', data)
	db_voice.commit()
	

def update_voice_data_for_data_base(old_data, new_data):
	db_voice.execute(f"UPDATE voice_active SET active_in_sec = '{new_data}' WHERE active_in_sec = '{old_data}'")
	db_voice.commit()
	

@bot.event
async def on_voice_state_update(member, before, after):
	if before.channel is None:
		voice_dct[member.id] = time.time()
	if after.channel is None:
		try:
			voice_dct[member.id] -= time.time()
		except KeyError:
			return
		i = db_voice.execute(f'SELECT active_in_sec FROM voice_active WHERE id_user = {member.id}')
		old_data = None
		for k in i:
			old_data = k
		if old_data is None:
			export_voice_data_for_data_base((int(member.id), str(member), int(float(str(voice_dct[member.id]).replace('-', '')))))
		else:
			old_data = int(float(str(old_data).replace(',', '').replace('(', '').replace(')', '')))
			new_data = int(float(old_data)) + int(float(str(voice_dct[member.id]).replace('-', '')))
			update_voice_data_for_data_base(old_data, int(float(new_data)))
			guild = bot.get_guild(993850749236813915)
			channel = bot.get_channel(1022482873032392764)
			users_role = []
			for n in member.roles:
				users_role.append(n.name)
			if 'Модератор' in users_role or 'Cтарший Модератор' in users_role or 'BIG BOSS' in users_role:
				return
			if new_data <= 32000:
				if "Дикий" not in users_role:
					await member.add_roles(nextcord.utils.get(guild.roles, name="Дикий"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Дикий' за первый часы в клане.(До 9ти часов.)")
				return
			if new_data <= 64000:
				if "Рейдер" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Дикий"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Рейдер"))
					await channel.send(
						f"{member.mention} получает повышения до роли 'Рейдер', так держать, тарковчанин!(9-18 часов.)")
				return
			if new_data <= 164000:
				if "Отступник" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Рейдер"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Отступник"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Отступник' за достижения в клане.(18-45 часов.)")
				return
			if new_data <= 264000:
				if "Сектант" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Отступник"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Сектант"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Сектант' за знатные заслуги перед сослуживцами.(73-101 часа.)")
				return
			if new_data <= 364000:
				if "глухарь" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Сектант"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Глухарь"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Глухарь'.\nПожалуй, стоит уважать этого бывалого воина(101 - 128 часов.)")
				return
			if new_data <= 464000:
				if "Решала" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Глухарь"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Решала"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Решала'.\nЛучше не попадаться ему на просторах Таркова...(128 - 156 часов.)")
				return
			if new_data <= 564000:
				if "Штурман" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Решала"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Штурман"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Штурман'\nУбойный воин, драк не боится, смерть приветствует.(156 - 184 часов.)")
				return
			if new_data <= 664000:
				if "Санитар" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Штурман"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Санитар"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Санитар'.\nПолечит, будь здоров 👻.(128 - 184 часов.)")
				return
			if new_data <= 764000:
				if "Big Pipe" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Санитар"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Killa"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Big Pipe'.\nГоворят у него действительно Big Pipe, но свидетелей нет💀. \n(184 - 212 часов.)")
				return
			if new_data <= 864000:
				if "Big Pipe" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Killa"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Big Pipe"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Big Pipe'.\nГоворят у него действительно Big Pipe, но свидетелей нет💀. \n(184 - 212 часов.)")
				return
			if new_data <= 964000:
				if "Bird Eye" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Big Pipe"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Bird Eye"))
					await channel.send(
						f"{member.mention} получает повышение до роли 'Bird Eye'.\nУчует твою задницу за милю, можешь и не прятатся🕵️‍♂️.\n(212 - 240 часов.)")
				return
			else:
				if "Dead Knight" not in users_role:
					try:
						await member.remove_roles(nextcord.utils.get(guild.roles, name="Bird Eye"))
					except Exception:
						pass
					await member.add_roles(nextcord.utils.get(guild.roles, name="Dead Knight"))
					await channel.send(
						f"{member.mention} получает максимальный ранг в клане.\nГоворят, в последний раз его видели на Маяке, но лучше бы вам его не искать😈.(240 - ... часов.)")
				return


bot.run(settings['token'])
