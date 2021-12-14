import discord
import asyncio
from decouple import config
from discord.ext import commands
from urllib import request, parse
import json

from discord.ext.commands import CommandNotFound
from discord_slash import ButtonStyle, ComponentContext, SlashCommand
from discord_slash.utils.manage_components import create_button, create_actionrow, wait_for_component

intents = discord.Intents.all()
token = config('TOKEN')

bot = commands.Bot(command_prefix="!", intents=intents)
bot.debug = False
bot.recruiter_ping = "<@&908691607006642216>"
slash = SlashCommand(bot, sync_commands=True)


bot.remove_command('help')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Debug mode: {bot.debug}')
    print('------')


@bot.event
async def on_member_join(ctx):
    if ctx.bot:
        return
    if ctx.guild.id != 861018927752151071:
        return
    else:
        staff_channel = bot.get_channel(861275842009235457)
        # Send a message to the mods
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

        bored = await ctx.guild.fetch_member(324504908013240330)
        staff = discord.utils.get(ctx.guild.roles, name="Staff")
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
            ctx: discord.PermissionOverwrite(read_messages=True),
            bored: discord.PermissionOverwrite(read_messages=True),
            staff: discord.PermissionOverwrite(read_messages=True),
        }
        member = ctx
        if category is None:
            category = await ctx.guild.create_category(category_name, overwrites=None, reason=None)
        channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, reason=None, category=category)
        channel_msg = f"Welcome to Prism SMP {ctx.mention} your application has been automatically generated\n" \
                      "`If you leave a question unanswered for 10 minutes your application will be closed automatically`\n**Please only send one message per question.**"
        await channel.send(channel_msg)

        questions = ["How old are you?", "What are your pronouns?",
                     "When faced with conflict, what is your go-to solution/reaction?",
                     "Do you have Minecraft Java Edition?",
                     "What is your minecraft skillset? (Are you a builder, redstoner etc.)",
                     "Are you a content creator? (if yes, please include a link)",
                     "Any additional information about yourself?",
                     "How did you get invited to the server?",
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
        await answer_channel.send("recruiter ping removed")
        await channel.send("Your application has been completed. Please wait for a member to assess your answers")
        embed = discord.Embed(color=discord.colour.Color.red())
        embed.title = f"{ctx.name}'s answers"
        button = [
            create_button(
                style=ButtonStyle.green,
                label="Accept",
                custom_id="accept"
            ), create_button(
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
                            f"**{questions[8]}**: ```{answers[8].content}```\n"
        await answer_channel.send(embed=embed, components=[action_row])
        ctx: ComponentContext = await wait_for_component(bot, components=action_row)
        await ctx.edit_origin(components=None)
        if ctx.custom_id == "accept":
            welcome_channel = bot.get_channel(id=861317568807829535)
            invitelink = await welcome_channel.create_invite(max_uses=1, unique=True)
            await answer_channel.send(f"Here's your invite to send to the user\n{invitelink}")
        elif ctx.custom_id == "deny":
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


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    embed = discord.Embed(title=f"**Error in command: {ctx.command}**", description=f"```\n{error}\n```", colour=discord.Color.red())
    await ctx.send(embed=embed)
    raise error


@bot.command()
async def apply(ctx):
    if ctx.channel.category_id != 907041085312872489:

        await ctx.send("https://media.giphy.com/media/3oKHW6zXvJ02pDmqTC/giphy.gif")
        await ctx.send("You can't do that here. If you need to fill out another application for some reason (you shouldn't need to) leave and re-join the server to trigger the process")
    else:
        member = ctx.author
        application_channel = ctx.channel
        channel_msg = f"Welcome to Prism SMP {ctx.author.mention} your application has been automatically generated\n"\
                      "`If you leave a question unanswered for 10 minutes your application will be closed automatically`\n**Please only send one message per question.**"
        await ctx.send(str(channel_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))

        questions = ["How old are you?", "What are your pronouns?",
                     "When faced with conflict, what is your go-to solution/reaction?",
                     "Do you have Minecraft Java Edition?",
                     "What is your minecraft skillset? (Are you a builder, redstoner etc.)",
                     "Are you a content creator? (if yes, please include a link)",
                     "Any additional information about yourself?",
                     "How did you get invited to the server?",
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
        answer_channel = bot.get_channel(861290025891135489)
        await answer_channel.send("recruiter ping removed")
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
                        f"**{questions[8]}**: ```{answers[8].content}```\n"
        await answer_channel.send(embed=embed, components=[action_row])
        ctx: ComponentContext = await wait_for_component(bot, components=action_row)
        await ctx.edit_origin(components=None)
        if ctx.custom_id == "accept":
            welcome_channel = bot.get_channel(id=861317568807829535)
            invitelink = await welcome_channel.create_invite(max_uses=1, unique=True)
            await answer_channel.send(f"Here's your invite to send to the user\n{invitelink}")
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
    if ctx.channel.category_id != 907041085312872489:
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
