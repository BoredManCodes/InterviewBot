import time
import random
import discord
import asyncio

#import sentry_sdk
from decouple import config
from discord.ext import commands, tasks
from urllib import request, parse
import json

from discord.ext.commands import CommandNotFound
from discord_slash import ButtonStyle, ComponentContext, SlashCommand
from discord_slash.context import InteractionContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component
#sentry_sdk.init(
#    config('SENTRY'),
#    traces_sample_rate=1.0)

intents = discord.Intents.all()
token = config('TOKEN')

bot = commands.Bot(command_prefix="!", intents=intents)
bot.debug = False
#bot.recruiter_ping = "Boop"
bot.recruiter_ping = "<@&908691607006642216>"
slash = SlashCommand(bot, sync_commands=True)


bot.remove_command('help')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Debug mode: {bot.debug}')
    print('------')
#    await bot.user.edit(avatar="https://cdn.discordapp.com/attachments/861275842009235457/1046308071305138206/FZTr_fzXwAIneN0.jpg")
   # input_file = open('queue.json', "r")
   # json_array = json.load(input_file)
   # counter = 0
   # for item in json_array['queue']:
   #     counter += 1
   # print(f"{counter} queued members loaded")
   # queue_channel = bot.get_channel(id=953462744827433020)
   # await queue_channel.edit(name=f"{counter} Queued Members")
   # input_file.close()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="the border for sneaky rats"))

    channel_update.start()


@bot.event
async def on_member_remove(member):
    if member.guild.id == 861018927752151071:  # Only detect if the user left the interview guild
        if member.bot:
            return
        else:
            staff = bot.get_channel(861275842009235457)
            await staff.send(f"{member} left the interview server")
           # input_file = open('queue.json', "r")
           # json_array = json.load(input_file)
           # for member in json_array['queue']:
           #     if member == member.id:
           #         await staff.send(
           #             f"{member.name} left\nRemoved them from the queue")
           #         json_array['queue'].remove(member)
           # jsonString = json.dumps(json_array)
           # output_file = open('queue.json', "w")
           # output_file.write(jsonString)
           # output_file.close()


@bot.event
async def on_member_join(ctx):
    if ctx.bot:
        return
    if ctx.guild.id != 861018927752151071:  # if user joined main server kick them from interview server
        guild = bot.get_guild(861018927752151071)
        await guild.kick(ctx)
        return
    else:
        staff_channel = bot.get_channel(861275842009235457)
        # Send a message to the mods
        if time.time() - ctx.created_at.timestamp() < 2592000:
            # Send a message to the mods
            title = f"{ctx.display_name} is potentially suspicious"
            embed = discord.Embed(title=title, color=discord.Color.red())
            embed.set_footer(text=f"Discord name: {ctx.name}\nDiscord ID: {ctx.id}",
                             icon_url=ctx.avatar_url)
            date_format = "%a, %d %b %Y %I:%M %p"
            embed.set_thumbnail(
                url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Warning.svg/1200px-Warning.svg.png")
            embed.add_field(name="Joined Discord", value=ctx.created_at.strftime(date_format), inline=False)
            await staff_channel.send(embed=embed)
        else:
            title = f"{ctx.display_name} joined the server"
            embed = discord.Embed(title=title, color=discord.Color.green())
            embed.set_footer(text=f"Discord name: {ctx.name}\nDiscord ID: {ctx.id}", icon_url=ctx.avatar_url)
            date_format = "%a, %d %b %Y %I:%M %p"
            embed.add_field(name="Joined Discord", value=ctx.created_at.strftime(date_format), inline=False)
        await staff_channel.send(embed=embed)
        await staff_channel.send(bot.recruiter_ping)
        await staff_channel.send("https://tenor.com/view/new-member-gif-21052846")

        category_name = "APPLICATIONS"
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        channel_name = "application-for-" + ctx.name

        staff = discord.utils.get(ctx.guild.roles, name="Staff")
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx: discord.PermissionOverwrite(read_messages=True),
            staff: discord.PermissionOverwrite(read_messages=True),
        }
        member = ctx
        if category is None:
            category = await ctx.guild.create_category(category_name, overwrites=None, reason=None)
        channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, reason=None, category=category)
        channel_msg = f"Welcome to Prism SMP {ctx.mention} your application has been automatically generated\n" \
                      "`If you leave a question unanswered for 10 minutes your application will be closed automatically`\n**Please only send one message per question.**"
        await channel.send(channel_msg)

        questions = ["How old are you?", "What part of the world are you from?", "What are your pronouns?",
                     "You arrive at your base after a day of mining to discover your diamonds are gone, what do you do?",
                     "Do you have Minecraft Java Edition?",
                     "What is your minecraft skillset? (Are you a builder, redstoner etc.)",
                     "Are you a content creator? (if yes, please include a link)",
                     "Any additional information about yourself?",
                     "How did you get invited to the server? If Reddit please include the subreddit.",
                     "Any other questions for us?"]
        answers = []

        def check(m):
            return m.author == ctx

        for i in questions:
            await channel.send(i)
            try:
                msg = await bot.wait_for('message', timeout=600, check=check)
            except asyncio.TimeoutError:
                await channel.send("You took too long, your application has been closed."
                                   "\nType `!apply` to restart the process")

                return
            else:
                answers.append(msg)
        answer_channel = bot.get_channel(861290025891135489)
        await answer_channel.send("<@&908691607006642216>")
        await channel.send("Your application has been completed. Please wait for a member to assess your answers")
        embed = discord.Embed(color=discord.colour.Color.red())
        embed.title = f"{ctx.name}'s answers"
        button = [
            create_button(
                style=ButtonStyle.green,
                label="Accept",
                custom_id=f"{ctx.id}accept"
            ), create_button(
                style=ButtonStyle.danger,
                label="Deny",
                custom_id=f"{ctx.id}deny"
            #), create_button(
            #    style=ButtonStyle.blue,
            #    label="Queue",
            #    custom_id=f"{ctx.id}queue"
            )
        ]
        action_row = create_actionrow(*button)
        embed.description = f"**{questions[0]}**: ```{answers[0].content}```\n**{questions[1]}**: ```{answers[1].content}```\n" \
                        f"**{questions[2]}**: ```{answers[2].content}```\n**{questions[3]}**: ```{answers[3].content}```\n" \
                        f"**{questions[4]}**: ```{answers[4].content}```\n**{questions[5]}**: ```{answers[5].content}```\n" \
                        f"**{questions[6]}**: ```{answers[6].content}```\n**{questions[7]}**: ```{answers[7].content}```\n" \
                        f"**{questions[8]}**: ```{answers[8].content}```**{questions[9]}**: ```{answers[9].content}```\n"
        await answer_channel.send(embed=embed, components=[action_row])
        completed_role = discord.utils.get(ctx.guild.roles, id=953781813774540860)
        await ctx.add_roles(completed_role)
        user_id = ctx.id
        user_name = ctx.display_name
        ctx: ComponentContext = await wait_for_component(bot, components=action_row)
        await ctx.edit_origin(components=None)
        if ctx.custom_id == f"{user_id}accept":
            welcome_channel = bot.get_channel(id=861317568807829535)
            mod_log = bot.get_channel(id=897765157940396052)
            invitelink = await welcome_channel.create_invite(max_uses=1, unique=True)
            await answer_channel.send(f"Here's your invite to send to {member.name}\n{invitelink}")
            await mod_log.send(embed=embed)
        elif ctx.custom_id == f"{user_id}deny":
            staff_channel = bot.get_channel(861275842009235457)
            await channel.delete()
            denied_msg = f":x: {member.display_name} was denied entry and kicked by {ctx.author.display_name}"
            await staff_channel.send(denied_msg)
            await member.send(
                "Sorry to say your application has been denied as we have reached our capacity for new members.\n"
                "Thank you for applying though! You can apply another time in the future and hope for the best!")
            await member.kick(reason="Denied")
            for msg in await staff_channel.history(limit=200).flatten():
                bot_messages = ["https://tenor.com/view/new-member-gif-21052846", "<@&908691607006642216>"]
                if any(keyword in msg.content.lower() for keyword in bot_messages):
                    if msg.author == bot.user:
                        await msg.delete()
        elif ctx.custom_id == f"{user_id}queue":
            input_file = open('queue.json', "r")
            json_array = json.load(input_file)
            json_array['queue'].append(user_id)
            jsonString = json.dumps(json_array)
            output_file = open('queue.json', "w")
            output_file.write(jsonString)
            output_file.close()
            await ctx.send(f"Queued {user_name}\nQueue now has {len(json_array['queue'])} members")


@tasks.loop(seconds=15)
async def channel_update():
    # Queue updater
    #input_file = open('queue.json', "r")
    #json_array = json.load(input_file)
    #counter = 0
    #for item in json_array['queue']:
    #    counter += 1
    #queue_channel = bot.get_channel(id=953462744827433020)
    #if not queue_channel.name == f"{counter} Queued Members":
    #    await queue_channel.edit(name=f"{counter} Queued Members")
    #    print("Changing counter channel numbers")
    #input_file.close()
    # New member and total member counter
    new_member_channel = bot.get_channel(id=958914882659565569)
    total_member_channel = bot.get_channel(id=958914922572550174)
    prism = bot.get_guild(id=858547359804555264)
    new_members = discord.utils.get(prism.roles, name="New Member")
    if not new_member_channel.name == f"{len(new_members.members)} New Members":
        await new_member_channel.edit(name=f"{len(new_members.members)} New Members")
    if not total_member_channel.name == f"{len(total_member_channel.members)} Total Members":
        await total_member_channel.edit(name=f"{len(prism.members)} Total Members")


#@slash.slash(name="queue", description="List all members in the queue", guild_ids=[861018927752151071])
#async def queue(ctx: InteractionContext):
#    input_file = open('queue.json', "r")
#    json_array = json.load(input_file)
#    counter = 0
#    queued_members = []
#    for item in json_array['queue']:
#        member = discord.utils.get(bot.get_all_members(), id=item)
#        queued_members.append(member.display_name)
#        counter += 1
#    await ctx.send(str(queued_members).replace('[', '').replace(']', '').replace("'", "").replace(', ', '\n'))
#    input_file.close()


#@slash.slash(name="remove", description="Removes a queued member from the queue", guild_ids=[861018927752151071], options=[
#                 create_option(
#                     name="user",
#                     description="The queued user to remove",
#                     option_type=6,
#                     required=True
#                 )
#             ])
#async def remove(ctx: InteractionContext, user: discord.Member):
#    recruit_role = discord.utils.get(ctx.guild.roles, id=908691607006642216)
#    if recruit_role not in ctx.author.roles:
#        await ctx.send("You are not authorised to do that")
#        return
#    else:
#        staff_channel = bot.get_channel(id=861275842009235457)
#        await ctx.send(f"Removed {user.mention} from the queue", hidden=True)
#        await staff_channel.send(f"{ctx.author.display_name} just removed {user.display_name} from the queue")
#        input_file = open('queue.json', "r")
#        json_array = json.load(input_file)
#        for member in json_array['queue']:
#            if member == user.id:
#                json_array['queue'].remove(member)
#        jsonString = json.dumps(json_array)
#        output_file = open('queue.json', "w")
#        output_file.write(jsonString)
#        output_file.close()#


#@slash.slash(name="accept", description="Accepts a queued member", guild_ids=[861018927752151071], options=[
#                 create_option(
#                     name="user",
#                     description="The queued user to accept",
#                     option_type=6,
#                     required=True
#                 )
#             ])
#async def accept(ctx: InteractionContext, user: discord.Member):
#    recruit_role = discord.utils.get(ctx.guild.roles, id=908691607006642216)
#    if recruit_role not in ctx.author.roles:
#        await ctx.send("You are not authorised to do that")
#        return
#    else:
#        category_name = "APPLICATIONS"
#        category = discord.utils.get(ctx.guild.categories, name=category_name)
#        channel_name = "application-for-" + user.display_name#
#
#        bored = await ctx.guild.fetch_member(324504908013240330)
#        staff = discord.utils.get(ctx.guild.roles, name="Staff")
#        overwrites = {
#            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
#            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
#            user: discord.PermissionOverwrite(read_messages=True),
#            bored: discord.PermissionOverwrite(read_messages=True),
#            staff: discord.PermissionOverwrite(read_messages=True),
#        }
#        if category is None:
#            category = await ctx.guild.create_category(category_name, overwrites=None, reason=None)
#        channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, reason=None,
#                                                      category=category)
#        welcome_channel = bot.get_channel(id=861317568807829535)
#        staff_channel = bot.get_channel(id=861275842009235457)
#        invitelink = await welcome_channel.create_invite(max_uses=1, unique=True)
#        await ctx.send(f"Here's your invite to send to {user.display_name}\n{invitelink}", hidden=True)
#        await staff_channel.send(f"{ctx.author.display_name} just accepted {user.display_name} to Prism")
#        input_file = open('queue.json', "r")
#        json_array = json.load(input_file)
#        for member in json_array['queue']:
#            if member == user.id:
#                json_array['queue'].remove(member)
#        jsonString = json.dumps(json_array)
#        output_file = open('queue.json', "w")
#        output_file.write(jsonString)
#        output_file.close()#


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    embed = discord.Embed(title=f"**Error in command: {ctx.command}**", description=f"```\n{error}\n```", colour=discord.Color.red())
    await ctx.send(embed=embed)
    raise error


@bot.command()
async def apply(ctx):
    if ctx.channel.category_id != 985909184728010752:

        await ctx.send("https://media.giphy.com/media/3oKHW6zXvJ02pDmqTC/giphy.gif")
        await ctx.send("You can't do that here. If you need to fill out another application for some reason (you shouldn't need to) leave and re-join the server to trigger the process")
    else:
        member = ctx.author
        application_channel = ctx.channel
        channel_msg = f"Welcome to Prism SMP {ctx.author.mention} your application has been automatically generated\n"\
                      "`If you leave a question unanswered for 10 minutes your application will be closed automatically`\n**Please only send one message per question.**"
        await ctx.send(str(channel_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))

        questions = ["How old are you?", "What part of the world are you from?", "What are your pronouns?",
                     "You arrive at your base after a day of mining and discover all your diamonds are missing, what do you do?",
                     "Do you have Minecraft Java Edition?",
                     "What is your minecraft skillset? (Are you a builder, redstoner etc.)",
                     "Are you a content creator? (if yes, please include a link)",
                     "Any additional information about yourself?",
                     "How did you get invited to the server? If Reddit please include the subreddit.",
                     "Any other questions for us?"]
        answers = []

        def check(m):
            return m.author == ctx.author

        for i in questions:
            await ctx.send(i)
            try:
                msg = await bot.wait_for('message', timeout=600, check=check)
            except asyncio.TimeoutError:
                await ctx.send("You took too long, your application has been closed."
                                   "\nType `!apply` to restart the process")

                return
            else:
                answers.append(msg)
        completed_role = discord.utils.get(ctx.guild.roles, id=953781813774540860)
        await ctx.author.add_roles(completed_role)
        answer_channel = bot.get_channel(861290025891135489)
        await answer_channel.send("<@&908691607006642216>")
        await ctx.send("Your application has been completed. Please wait for a member to assess your answers")
        embed = discord.Embed(color=ctx.author.color)
        embed.title = f"{ctx.author.name}'s answers"
        button = [
            create_button(
                style=ButtonStyle.green,
                label="Accept",
                custom_id="accept"
            ),create_button(
                style=ButtonStyle.danger,
                label="Deny",
                custom_id="deny"
            ),
        ]
        action_row = create_actionrow(*button)
        embed.description = f"**{questions[0]}**: ```{answers[0].content}```\n**{questions[1]}**: ```{answers[1].content}```\n" \
                        f"**{questions[2]}**: ```{answers[2].content}```\n**{questions[3]}**: ```{answers[3].content}```\n" \
                        f"**{questions[4]}**: ```{answers[4].content}```\n**{questions[5]}**: ```{answers[5].content}```\n" \
                        f"**{questions[6]}**: ```{answers[6].content}```\n**{questions[7]}**: ```{answers[7].content}```\n" \
                        f"**{questions[8]}**: ```{answers[8].content}```**{questions[9]}**: ```{answers[9].content}```\n"
        await answer_channel.send(embed=embed, components=[action_row])
        ctx: ComponentContext = await wait_for_component(bot, components=action_row)
        await ctx.edit_origin(components=None)
        if ctx.custom_id == "accept":
            welcome_channel = bot.get_channel(id=861317568807829535)
            mod_log = bot.get_channel(id=897765157940396052)
            invitelink = await welcome_channel.create_invite(max_uses=1, unique=True)
            await answer_channel.send(f"Here's your invite to send to {member.name}\n{invitelink}")
            await mod_log.send(embed=embed)
        elif ctx.custom_id == "deny":
            staff_channel = bot.get_channel(861275842009235457)
            await application_channel.delete()
            denied_msg = f":x: {member.display_name} was denied entry and kicked by {ctx.author.display_name}"
            await staff_channel.send(
                str(denied_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))
            await member.send(
                "Sorry to say your application has been denied as we have reached our capacity for new members.\n"
                "Thank you for applying though! You can apply another time in the future and hope for the best!")
            await member.kick(reason="Denied")
            for msg in await staff_channel.history(limit=200).flatten():
                bot_messages = ["https://tenor.com/view/new-member-gif-21052846", "<@&908691607006642216>"]
                if any(keyword in msg.content.lower() for keyword in bot_messages):
                    if msg.author == bot.user:
                        await msg.delete()

@bot.command()
@commands.has_any_role('Moderator', 'Administrator', 'Discord Admin', 'Staff')
async def close(ctx):
    if ctx.channel.category_id != 985909184728010752:
        await ctx.send("https://media.giphy.com/media/3oKHW6zXvJ02pDmqTC/giphy.gif")
        await ctx.send("You can't do that here. This command will delete the channel and we wouldn't want that")
    else:
        staff_channel = bot.get_channel(861275842009235457)
        closed_channel = str(ctx.channel.name).replace("application-for-", "")
        await staff_channel.send(f"{closed_channel}'s application was closed by {ctx.message.author.display_name}")
        await ctx.channel.delete()
        #messages = await staff_channel.history(limit=200).flatten()
        for msg in await staff_channel.history(limit=200).flatten():
            bot_messages = ["https://tenor.com/view/new-member-gif-21052846", "<@&908691607006642216>"]
            if any(keyword in msg.content.lower() for keyword in bot_messages):
                if msg.author == bot.user:
                    await msg.delete()



@bot.command(name='help', aliases=['h'], pass_context=True)
async def help(ctx):
    if ctx.guild.id != 861018927752151071:
        return
    help = "`!apply` restarts a timed out or otherwise broken application\n" \
           "`!close` marks an application as closed and deletes it's channel\n" \
           "`!nuke` does what it says on the tin and nukes all the applications\n" \
           "`!deny <mentioned discord user>` denies the @'ed user's application by DMing them and kicking them"
    embed = discord.Embed(title="**Prism Interview Bot Help**", description=help, color=discord.Color.blue())
    embed.set_footer(text="Requested by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


@bot.command(name='deny', pass_contect=True)
@commands.has_any_role('Moderator', 'Administrator', 'Discord Admin', 'Staff')
async def deny(ctx, *, member: discord.Member):
    if ctx.channel.category_id != 907041085312872489:

        await ctx.send("https://media.giphy.com/media/3oKHW6zXvJ02pDmqTC/giphy.gif")
        await ctx.send("You can't do that here. This command will delete the channel and we wouldn't want that")
    else:
        staff_channel = bot.get_channel(861275842009235457)
        await ctx.channel.delete()
        denied_msg = ":x:", member.display_name, "was denied entry and kicked"
        await staff_channel.send(str(denied_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))
        await member.send("Sorry to say your application has been denied as we have reached our capacity for new members.\n"
                          "Thank you for applying though! You can apply another time in the future and hope for the best!")
        await member.kick(reason="Denied")
        for msg in await staff_channel.history(limit=200).flatten():
            bot_messages = ["https://tenor.com/view/new-member-gif-21052846", "<@&908691607006642216>"]
            if any(keyword in msg.content.lower() for keyword in bot_messages):
                if msg.author == bot.user:
                    await msg.delete()


@bot.event
async def on_message(message):
    if not message.guild:
        if not message.author == bot.user:
            staff_channel = bot.get_channel(861275842009235457)
            message_filtered = str(message.content).replace('www', '').replace('http', '')
            url = 'https://neutrinoapi.net/bad-word-filter'
            params = {
                'user-id': 'BoredManSwears',
                'api-key': config("NaughtyBoy_key"),
                'content': message_filtered,
                'censor-character': '•',
                'catalog': 'strict'
            }
            postdata = parse.urlencode(params).encode()
            req = request.Request(url, data=postdata)
            response = request.urlopen(req)
            result = json.loads(response.read().decode("utf-8"))
            print(message.content)
            await staff_channel.send(f"{message.author.display_name} sent me a message: {result['censored-content']}")
            await message.channel.send('Lol hi')
    await bot.process_commands(message)


bot.run(token)
