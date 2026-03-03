import discord
from discord.ext import commands
from discord.ui import Button, View
from flask import Flask, request
import threading
import os

# --- 設定（RenderのEnvironment Variablesで設定するのが安全です） ---
# 直接書き込む場合は ' ' の中に入れてください
TOKEN = os.getenv('TOKEN', 'ここにボットのトークン')
LOG_CHANNEL_ID = int(os.getenv('LOG_CHANNEL_ID', '0'))   # 通知用チャンネルID
LIST_CHANNEL_ID = int(os.getenv('LIST_CHANNEL_ID', '0')) # 名簿用チャンネルID

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# 既に名簿に載った人を記録するセット
user_list = set()

# 「詳細を表示」ボタンの動作
class DetailView(View):
    def __init__(self, uid, name):
        super().__init__(timeout=None)
        self.uid = uid
        self.name = name

    @discord.ui.button(label="詳細を表示", style=discord.ButtonStyle.primary)
    async def show_details(self, interaction: discord.Interaction, button: discord.ui.Button):
        # 押した本人にだけ見えるメッセージ
        detail_msg = (
            f"**【{self.name} の詳細データ】**\n"
            f"🆔 ユーザーID: `{self.uid}`\n"
            f"🔗 プロフィール: https://www.roblox.com/users/{self.uid}/profile"
        )
        await interaction.response.send_message(detail_msg, ephemeral=True)

# --- Robloxからデータを受け取るサーバー設定 ---
app = Flask('')

@app.route('/log', methods=['POST'])
def log_received():
    data = request.json
    name = data.get("name", "Unknown")
    uid = data.get("id", "0")
    
    # Discord送信処理を予約
    bot.loop.create_task(send_to_discord(name, uid))
    return "OK", 200

async def send_to_discord(name, uid):
    # 1. 通知チャンネル（ボタン付き）
    log_ch = bot.get_channel(LOG_CHANNEL_ID)
    if log_ch:
        view = DetailView(uid, name)
        await log_ch.send(f"🚀 **{name}** がスクリプトを起動しました！", view=view)

    # 2. 名簿チャンネル（初めての人だけ記録）
    list_ch = bot.get_channel(LIST_CHANNEL_ID)
    if list_ch and uid not in user_list:
        user_list.add(uid)
        await list_ch.send(f"👤 **新規ユーザー登録:** {name} (ID: {uid})")

# サーバー起動用の関数
def run_server():
    app.run(host='0.0.0.0', port=10000)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# サーバーとボットを同時に動かす
threading.Thread(target=run_server).start()
bot.run(TOKEN)
