import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# === CONFIGURACIÓN DEL WEB SERVER FALSO PARA RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Discord activo"

def run_web():
    app.run(host='0.0.0.0', port=10000)  # Puerto fijo para Render

Thread(target=run_web).start()

# === BOT DE DISCORD ===

TOKEN = os.getenv("DISCORD_TOKEN")
STREAM_URL = os.getenv("STREAM_URL")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

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
        await ctx.send("🔊 Reproduciendo Radio CB.")
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
    voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)
    if voice_client and voice_client.is_connected():
        if len(voice_client.channel.members) == 1:
            await asyncio.sleep(10)
            if len(voice_client.channel.members) == 1:
                await voice_client.disconnect()
                print(f"Bot desconectado de {voice_client.channel.name} porque quedó solo.")

bot.run(TOKEN)
