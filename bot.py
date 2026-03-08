import discord
from discord.ext import commands
import datetime
import os
from database import init_db, add_time, get_top, reset_all

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

join_times = {}

@bot.event
async def on_ready():
    init_db()
    print(f"ログイン完了: {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:
        join_times[member.id] = datetime.datetime.now()

    elif before.channel is not None and after.channel is None:
        if member.id in join_times:
            join_time = join_times.pop(member.id)
            stay_seconds = int((datetime.datetime.now() - join_time).total_seconds())
            add_time(member.id, stay_seconds)

@bot.command()
async def top(ctx):
    ranking = get_top()
    embed = discord.Embed(title="🎧 VC滞在ランキング TOP10", color=0x00ffcc)

    for i, (user_id, seconds) in enumerate(ranking, start=1):
        user = ctx.guild.get_member(user_id)
        name = user.display_name if user else "Unknown"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        embed.add_field(
            name=f"{i}位：{name}",
            value=f"{hours}時間 {minutes}分",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(administrator=True)
async def reset(ctx):
    reset_all()
    await ctx.send("⛔ 全メンバーのVC滞在時間をリセットしました！")

bot.run(os.getenv("BOT_TOKEN"))