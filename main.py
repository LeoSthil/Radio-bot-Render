import discord
from discord.ext import commands
import os
import asyncio
from flask import Flask
from threading import Thread

# === SERVIDOR FLASK PARA RENDER ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot de Discord activo"

def run_web():
    app.run(host='0.0.0.0', port=10000)

Thread(target=run_web).start()

# === CONFIGURACIÓN DEL BOT ===
TOKEN = os.getenv("DISCORD_TOKEN")
STREAM_URL = os.getenv("STREAM_URL")  # URL principal: One

# Diccionario de radios disponibles
RADIOS = {
    "one": STREAM_URL,
    "ibiza": "https://cdn-peer022.streaming-pro.com:8025/ibizaglobalradio.mp3"
}

# Variable para guardar la radio activa
current_stream = {"url": RADIOS["one"]}

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    activity=discord.Activity(type=discord.ActivityType.listening, name="la mejor música")
)

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")

@bot.command()
async def radios(ctx):
    mensaje = "**🎧 Radios disponibles:**\n"
    for nombre, url in RADIOS.items():
        mensaje += f"• `{nombre}` → {url}\n"
    await ctx.send(mensaje)

@bot.command()
async def setradio(ctx, nombre: str):
    nombre = nombre.lower()
    if nombre not in RADIOS:
        opciones = ', '.join([f"`{r}`" for r in RADIOS.keys()])
        await ctx.send(f"❌ Radio no encontrada.\nRadios disponibles: {opciones}")
        return

    current_stream["url"] = RADIOS[nombre]

    if ctx.author.voice:
        voice_channel = ctx.author.voice.channel

        try:
            if ctx.voice_client is None:
                vc = await voice_channel.connect()
            else:
                vc = ctx.voice_client
                if vc.channel != voice_channel:
                    await vc.move_to(voice_channel)
        except discord.ClientException:
            vc = ctx.voice_client

        if vc.is_playing():
            vc.stop()

        try:
            vc.play(
                discord.FFmpegPCMAudio(
                    current_stream["url"],
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    options="-vn"
                )
            )
            await ctx.send(f"📻 Cambiada y reproduciendo: **{nombre.title()}**")
        except Exception as e:
            await ctx.send("⚠️ Error al reproducir el nuevo stream.")
            print("Error al reproducir con FFmpeg:", e)
    else:
        await ctx.send(f"📻 Radio cambiada a **{nombre.title()}**. Únete a un canal de voz y usa `!radio` para escuchar.")

@bot.command()
async def radio(ctx):
    if ctx.author.voice:
        voice_channel = ctx.author.voice.channel
        try:
            vc = await voice_channel.connect()
        except discord.ClientException:
            vc = ctx.voice_client

        try:
            vc.play(
                discord.FFmpegPCMAudio(
                    current_stream["url"],
                    before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                    options="-vn"
                )
            )
            await ctx.send("🔊 Reproduciendo la radio seleccionada.")
        except Exception as e:
            await ctx.send("⚠️ Error al reproducir el stream.")
            print("Error al reproducir con FFmpeg:", e)
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
                print(f"🔌 Bot desconectado de {voice_client.channel.name} por estar solo.")

bot.run(TOKEN)

