import discord
import asyncio
from decouple import config
from discord.ext import commands
from sys import platform

intents = discord.Intents.all()
token = config('TOKEN')

if platform == "linux" or platform == "linux2":
    bot = commands.Bot(command_prefix="!", intents=intents)
    bot.debug = False
    bot.recruiter_ping = "<@&908691607006642216>"


elif platform == "win32":
    bot = commands.Bot(command_prefix="dev!", intents=intents)
    bot.debug = True
    bot.recruiter_ping = "Detected test environment. Recruiter ping removed for sanity"


bot.remove_command('help')


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print(f'Debug mode: {bot.debug}')
    print('------')


@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        embed = discord.Embed(title="We ran into an error", description="You are not staff", color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="We ran into an error", description="You forgot to define a member", color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.BotMissingPermissions):
        embed = discord.Embed(title="We ran into an error", description="I am missing permissions to delete my invoking command", color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.CommandNotFound):
        embed = discord.Embed(title="Can you don\'t?", description="That command doesn't exist friendo. Did you mean `!apply`?", color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="We ran into an undefined error", description=error, color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)


@bot.event
async def on_member_join(ctx):
    if ctx.bot:
        return
    else:
        staff_channel = bot.get_channel(861275842009235457)
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

        if category is None:
            category = await ctx.guild.create_category(category_name, overwrites=None, reason=None)
        channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, reason=None, category=category)
        channel_msg = f"Welcome to Prism SMP {ctx.mention} your application has been automatically generated\n"\
                      "`If you leave a question unanswered for 10 minutes your application will be closed automatically`\n**Please only send one message per question.**"

        await channel.send(str(channel_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))

        questions = ["How old are you?", "What are your pronouns?",
                     "When faced with conflict, what is your go-to solution/reaction?", "Do you have Minecraft Java Edition?",
                     "What is your minecraft skillset? (Are you a builder, redstoner etc.)",
                     "Are you a content creator? (if yes, please include a link)", "Any additional information about yourself?",
                     "How did you get invited to the server?", "Any other questions for us?"]

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
        await answer_channel.send(bot.recruiter_ping)
        await channel.send("Your application has been completed. Please wait for a member to assess your answers")
        e = discord.Embed(color=ctx.color)
        e.title = ctx.name
        e.description = f"**{questions[0]}**: ```{answers[0].content}```\n**{questions[1]}**: ```{answers[1].content}```" \
                        f"\n**{questions[2]}**: ```{answers[2].content}```\n**{questions[3]}**: ```{answers[3].content}```\n" \
                        f"**{questions[4]}**: ```{answers[4].content}```\n**{questions[5]}**: ```{answers[5].content}```\n" \
                        f"**{questions[6]}**: ```{answers[6].content}```\n**{questions[7]}**: ```{answers[7].content}```\n" \
                        f"**{questions[8]}**: ```{answers[8].content}```\n"
        await answer_channel.send(embed=e)


@bot.command(pass_context=True)
@commands.has_any_role('Moderator', 'Administrator', 'Discord Admin', 'Staff')
async def nuke(ctx):
    await ctx.message.delete()
    category = discord.utils.get(ctx.guild.categories, name="APPLICATIONS")
    channels = category.channels
    channel_count = 0
    for channel in channels:
        try:
            channel_count += 1
            await channel.delete()
        except AttributeError:
            pass
    if channel_count > 1:
        channel_count_msg = "Deleted", channel_count, "applications"
    elif channel_count == 0:
        channel_count_msg = "There were no applications"
    elif channel_count == 1:
        channel_count_msg = "Deleted", channel_count, "application"
    else:
        channel_count_msg = "Something funky is going on, I'm going to call dad. <@324504908013240330>"
    await ctx.send(str(channel_count_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))


@bot.command()
async def clear(ctx):
    return


@bot.command()
async def apply(ctx):
    blacklisted = [861275842009235457, 861290025891135489, 906739301394567189, 861279044162420766, 861279509110194207, 906747833825243146]
    if ctx.channel.id in blacklisted:
        await ctx.send("https://media.giphy.com/media/3oKHW6zXvJ02pDmqTC/giphy.gif")
        await ctx.send("You can't do that here. If you need to fill out another application for some reason (you shouldn't need to) leave and re-join the server to trigger the process")
    else:
        channel_msg = "Welcome to Prism SMP", ctx.author.mention, "your application has been re-opened\n"\
                      "`If you leave a question unanswered for 10 minutes your application will be closed automatically`"
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
        await answer_channel.send(bot.recruiter_ping)
        await ctx.send("Your application has been completed. Please wait for a member to assess your answers")
        e = discord.Embed(color=ctx.author.color)
        e.title = ctx.author.name
        e.description = f"**{questions[0]}**: ```{answers[0].content}```\n**{questions[1]}**: ```{answers[1].content}```\n" \
                        f"**{questions[2]}**: ```{answers[2].content}```\n**{questions[3]}**: ```{answers[3].content}```\n" \
                        f"**{questions[4]}**: ```{answers[4].content}```\n**{questions[5]}**: ```{answers[5].content}```\n" \
                        f"**{questions[6]}**: ```{answers[6].content}```\n**{questions[7]}**: ```{answers[7].content}```\n" \
                        f"**{questions[8]}**: ```{answers[8].content}```\n"
        await answer_channel.send(embed=e)


@bot.command()
@commands.has_any_role('Moderator', 'Administrator', 'Discord Admin', 'Staff')
async def close(ctx):
    blacklisted = [861275842009235457, 861290025891135489, 906739301394567189, 861279044162420766, 861279509110194207, 906747833825243146]
    if ctx.channel.id in blacklisted:
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
    blacklisted = [861275842009235457, 861290025891135489, 906739301394567189, 861279044162420766, 861279509110194207, 906747833825243146]
    if ctx.channel.id in blacklisted:
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
            message_filtered = str(message.content).replace('nigger', '`n-word`').replace('nigga', '`n-word`').replace('niga', '`n-word`').replace('nigg', '`n-word`').replace('nig', '`n-word`').replace('fuck', '`f-word`').replace('fuk', '`f-word`').replace('fuc', '`f-word`').replace('cunt', '`c-word`').replace('faggot', '`homophobic slur`').replace('www', '').replace('http', '')
            await staff_channel.send(f"{message.author.display_name} sent me a message: {message_filtered}")
            await message.channel.send('Lol hi')
    await bot.process_commands(message)


bot.run(token)
