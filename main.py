import discord
import asyncio
from decouple import config
from discord.ext import commands
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)
token = config('TOKEN')
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


@bot.event
async def on_command_error(ctx, error):
    print(error)
    if isinstance(error, commands.errors.CheckFailure):
        embed = discord.Embed(title="We ran into an error", description="You are not staff", color=discord.Color.red())
        embed.set_footer(text="Caused by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(title="We ran into an error", description="You forgot to define a message", color=discord.Color.red())
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
    category_name = "APPLICATIONS"
    category = discord.utils.get(ctx.guild.categories, name=category_name)
    channel_name = "application-for-" + ctx.name

    bored = await ctx.guild.fetch_member(324504908013240330)
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
        ctx: discord.PermissionOverwrite(read_messages=True),
        bored: discord.PermissionOverwrite(read_messages=True)
    }

    if category is None:
        category = await ctx.guild.create_category(category_name, overwrites=None, reason=None)
    channel = await ctx.guild.create_text_channel(channel_name, overwrites=overwrites, reason=None, category=category)
    channel_msg = "Welcome to Prism SMP", ctx.mention, "your application has been automatically generated"
    await channel.send(str(channel_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))

    questions = ["How old are you?", "What are your pronouns?",
                 "When faced with conflict, what is your go-to solution/reaction?", "Do you have Minecraft Java Edition?",
                 "What is your minecraft skillset? (Are you a builder, redstoner etc.)",
                 "Are you a content creator? (if yes, please include a link)", "Any additional information about yourself?",
                 "How did you get invited to the server?", "Any other questions for us?"] # Create your list of answers

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
    await channel.send("Your application has been completed. Please wait for a <@&907041826182148136> member to assess your answers")
    answer_channel = bot.get_channel(861290025891135489)
    e = discord.Embed(color=ctx.author.color)
    e.title = ctx.author.name
    e.description = f"**{questions[0]}**: ```{answers[0].content}```\n**{questions[1]}**: ```{answers[1].content}```\n**{questions[2]}**: ```{answers[2].content}```\n**{questions[3]}**: ```{answers[3].content}```\n**{questions[4]}**: ```{answers[4].content}```\n**{questions[5]}**: ```{answers[5].content}```\n**{questions[6]}**: ```{answers[6].content}```\n**{questions[7]}**: ```{answers[7].content}```\n**{questions[8]}**: ```{answers[8].content}```\n"
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
    if channel_count < 1:
        channel_count_msg = "Deleted", channel_count, "applications"

    else:
        channel_count_msg = "Deleted", channel_count, "application"
    msg = await ctx.send(str(channel_count_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))



@bot.command()
async def apply(ctx):
    blacklisted = [861275842009235457, 861290025891135489, 906739301394567189, 861279044162420766, 861279509110194207, 906747833825243146]
    if ctx.channel.id in blacklisted:
        await ctx.send("https://media.giphy.com/media/3oKHW6zXvJ02pDmqTC/giphy.gif")
        await ctx.send("You can't do that here. If you need to fill out another application for some reason (you shouldn't need to) leave and re-join the server to trigger the process")
    else:
        channel_msg = "Welcome to Prism SMP", ctx.author.mention, "your application has been re-opened"
        await ctx.send(str(channel_msg).replace('(', '').replace(')', '').replace(',', '').replace('\'', ''))

        questions = ["How old are you?", "What are your pronouns?",
                     "When faced with conflict, what is your go-to solution/reaction?",
                     "Do you have Minecraft Java Edition?",
                     "What is your minecraft skillset? (Are you a builder, redstoner etc.)",
                     "Are you a content creator? (if yes, please include a link)",
                     "Any additional information about yourself?",
                     "How did you get invited to the server?",
                     "Any other questions for us?"]  # Create your list of answers

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
        await ctx.send("Your application has been completed. Please wait for a <@&907041826182148136> member to assess your answers")
        answer_channel = bot.get_channel(861290025891135489)
        e = discord.Embed(color=ctx.author.color)
        e.title = ctx.author.name
        e.description = f"**{questions[0]}**: ```{answers[0].content}```\n**{questions[1]}**: ```{answers[1].content}```\n**{questions[2]}**: ```{answers[2].content}```\n**{questions[3]}**: ```{answers[3].content}```\n**{questions[4]}**: ```{answers[4].content}```\n**{questions[5]}**: ```{answers[5].content}```\n**{questions[6]}**: ```{answers[6].content}```\n**{questions[7]}**: ```{answers[7].content}```\n**{questions[8]}**: ```{answers[8].content}```\n"
        await answer_channel.send(embed=e)


@bot.command()
@commands.has_any_role('Moderator', 'Administrator', 'Discord Admin', 'Staff')
async def close(ctx):
    blacklisted = [861275842009235457, 861290025891135489, 906739301394567189, 861279044162420766, 861279509110194207, 906747833825243146]
    if ctx.channel.id in blacklisted:
        await ctx.send("https://media.giphy.com/media/3oKHW6zXvJ02pDmqTC/giphy.gif")
        await ctx.send("You can't do that here. This command will delete the channel and we wouldn't want that")
    else:
        await ctx.channel.delete()


@bot.command(name='help', aliases=['h'], pass_context=True)
async def help(ctx):

    help = "`!apply` restarts a timed out or otherwise broken application\n" \
           "`!close` marks an application as closed and deletes it's channel\n" \
           "`!nuke` does what it says on the tin and nukes all the applications"
    embed = discord.Embed(title="**Prism Interview Bot Help**", description=help, color=discord.Color.blue())
    embed.set_footer(text="Requested by " + ctx.message.author.name, icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


bot.run(token)
