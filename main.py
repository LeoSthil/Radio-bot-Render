import discord
from discord.ext import commands
import os
import asyncio

TOKEN = os.getenv("DISCORD_TOKEN")
STREAM_URL = os.getenv("STREAM_URL")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True  # Necesario para detectar cambios de voz

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Conectado como {bot.user}")

@bot.command()
async def radio(ctx):
    if ctx.author.voice:
        voice_channel = ctx.author.voice.channel
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(STREAM_URL))
        await ctx.send("🔊 Reproduciendo la radio.")
    else:
        await ctx.send("❌ Debes estar en un canal de voz.")

@bot.command()
async def stop(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("⏹️ Radio detenida.")
    else:
        await ctx.send("❌ El bot no está en un canal de voz.")

@bot.event
async def on_voice_state_update(member, before, after):
    # Verifica si el bot está conectado en ese servidor
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    if voice_client and voice_client.is_connected():
        # Si el canal donde está el bot solo tiene al bot, desconéctalo
        if len(voice_client.channel.members) == 1:
            await asyncio.sleep(10)  # Espera 10 segundos antes de verificar
            if len(voice_client.channel.members) == 1:
                await voice_client.disconnect()
                print(f"Bot desconectado de {voice_client.channel.name} porque quedó solo.")

bot.run(TOKEN)