import discord
from discord.ext import commands
import os
import re

# --- 設定 ---
TOKEN = os.getenv("TOKEN")
# 監視したいWebhookが投稿されるチャンネルのID
WATCH_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID"))

intents = discord.Intents.default()
intents.message_content = True  # メッセージを読み取るために必須
bot = commands.Bot(command_prefix="!", intents=intents)

# 実行した人の名前を保存する
user_list = set()

@bot.event
async def on_ready():
    print(f'監視ボット起動: {bot.user}')

@bot.event
async def on_message(message):
    # 指定したチャンネル以外は無視
    if message.channel.id != WATCH_CHANNEL_ID:
        await bot.process_commands(message)
        return

    # Webhookやボットの投稿から名前を探す（例: "Player: Name" や "名前: Name" など）
    # ここでは正規表現を使って、メッセージ内の英数字の名前を抽出する例です
    # メッセージの形式に合わせて re.search の中身を調整できます
    content = message.content
    if not content and message.embeds:
        # 埋め込み(Embed)の中に名前がある場合
        content = str(message.embeds[0].to_dict())

    # 例: メッセージ内から「Name: (名前)」というパターンを探す
    match = re.search(r'(?:Name|Player|名前):\s*(\w+)', content, re.IGNORECASE)
    if match:
        player_name = match.group(1)
        user_list.add(player_name)
        print(f"リストに追加: {player_name}")

    await bot.process_commands(message)

@bot.command(name="List")
async def show_list(ctx):
    if not user_list:
        await ctx.send("まだ誰もリストに登録されていません。")
        return
    
    names = "\n".join([f"・{name}" for name in user_list])
    embed = discord.Embed(title="📜 Webhook抽出リスト", description=names, color=0x3498db)
    await ctx.send(embed=embed)

bot.run(TOKEN)
