import discord
from discord.ext import commands
import asyncio

import configparser
import json

######################################################
# logger setup

import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler("discord.log", mode='a', maxBytes=5*1024*1024, 
                              backupCount=2, encoding=None, delay=0)
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger = logging.getLogger('root')
logger.setLevel(logging.INFO)
logger.addHandler(handler)

######################################################


######################################################
# Server settings

# channel_name = "313898116153606145"


######################################################

bot = commands.Bot(command_prefix='&', description="")
bot.remove_command('help')


queue = []
current_singer = 0

pinned_message = None

queue_file = open("queue.txt", "r").read()
if queue_file:
	queue = json.loads(queue_file)

@bot.event
async def on_ready():
  global pinned_message
  print('Logged in as')
  print(bot.user.name)
  print(bot.user.id)
  print('------')

  # For next iteration. Pinned message (with reactions)
  # try:
  #   pinned_message = await bot.get_message(bot.get_channel(channel_name),"3141943817664")
  # except discord.NotFound:
  #   pinned_message = await bot.send_message(bot.get_channel(channel_name), "Initializing..\n" + stringify_queue())



@bot.command()
async def help():
	msg = """
```
&add - Add yourself to the queue
&next [n] - Move to the next person in the queue. Optional [n] to jump to that person.
&prev - Move to the previous person in the queue
&remove [n] - Remove yourself from the queue. Provide [n] to remove others.
&display - Display the current queue
&clean - Clear the current queue
```
"""
	await bot.say(msg)

@bot.command(pass_context=True)
async def changenick(ctx):
	if author_id == "219453623254515712":
		await bot.edit_profile(username="Karaoke Bot")

@bot.command(pass_context=True)
async def display(ctx):
	"""Display the current queue"""
	msg = await bot.say(stringify_queue())
	# print(msg.content)
	# await asyncio.sleep(5)
	# await bot.delete_message(msg)
	# await asyncio.sleep(5)
	# await bot.delete_message(ctx.message)

@bot.command(pass_context=True)
async def next(ctx):
	global current_singer
	msg = ""
	msg_list = ctx.message.content.split(" ")
	if (len(msg_list) >=2 ):
		try:
			next_num = int(msg_list[1])
			if next_num > 0 and next_num <= len(queue)-1:
				current_singer = next_num - 1
			else:
				raise ValueError
		except ValueError:
			msg = "Invalid number"
	elif len(queue) == 1:
		current_singer = 0
	elif current_singer < len(queue)-1:
		current_singer = current_singer+1
	else:
		current_singer = 0

	if not msg:
		msg = stringify_queue()

	await bot.say(msg)
	# await bot.edit_message(pinned_message, stringify_queue())

@bot.command()
async def prev():
	prev_singer()
	await bot.say(stringify_queue())


@bot.command(pass_context=True)
async def remove(ctx):
	"""Remove yourself or others from the queue
	>r to remove yourself
	>r [n] where [n] is the number to remove others"""
	global queue

	rem = ctx.message.content.split(" ")

	if len(rem) >= 2:
		index = int(rem[1])
		if index > 0 and index <= len(queue):
			del queue[index-1]
			msg = "Removed\n" + stringify_queue()
		else:
			msg = "Invalid number"
	else:

		member = ctx.message.author.name
		queue.remove(member)
		msg = stringify_queue()

	# await bot.edit_message(pinned_message, stringify_queue())
	await bot.say(stringify_queue())

@bot.command(pass_context=True)
async def add(ctx):
	"""Add yourself to the queue"""
	member = ctx.message.author

	msg = ""
	if member.name in queue:
		msg = "You're already in the queue"
	else:
		queue.append(member.name)

	if len(queue) == 1:
		next_singer()

	await bot.say(stringify_queue())

@bot.command(pass_context=True)
async def clean(ctx):
	author_id = ctx.message.author.id
	if author_id == "219453623254515712":
		logger.info("author cleaning: " + str(ctx.message.author))
		del queue[:]
		await bot.say(stringify_queue())

#############################################################################
# helpers
#############################################################################

def prev_singer():
	global current_singer
	if len(queue) == 1:
		current_singer = 0
	elif current_singer == 0:
		current_singer = len(queue)-1
	elif current_singer <= len(queue)-1:
		current_singer = current_singer-1
	else:
		current_singer = 0

def stringify_queue():
	if not queue:
		return "Queue is empty!"

	s = "**The current queue is**:\n```\n------------------------------------------------------\n"
	for index, item in enumerate(queue):
		if (current_singer == index):
			s += str(index+1) +". " + item + " <<-\n"
		else:
			s += str(index+1) +". " + item + "\n"
	s += "------------------------------------------------------\n```"

	logger.info(s)
	return s


# exit handler.
import atexit

def exit_handler():
    logger.info("Program ending. Saving the queue")
    with open('queue.txt', 'w') as f:
    	json.dump(queue, f)


atexit.register(exit_handler)

config = configparser.ConfigParser()
config.read('secrets.cfg')
token = config['DEFAULT']['token']
bot.run(token)