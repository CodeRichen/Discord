import os

import discord
from discord.ext import commands
from discord.ui import View, Button

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# 🔹 你的身分組名稱（要跟 Discord 完全一樣）
ROLE_ENCRYPT = "miku"
ROLE_DECRYPT = "richen"

# 🔹 自動發送按鈕的頻道 ID
#    把這個數字改成你要自動貼按鈕的文字頻道 ID
AUTO_SEND_CHANNEL_ID =988454341834854410

_startup_button_sent = False


def can_manage_role(guild: discord.Guild, target_role: discord.Role) -> bool:
    bot_member = guild.me or guild.get_member(bot.user.id if bot.user else 0)
    if bot_member is None:
        return False

    return bot_member.guild_permissions.manage_roles and target_role < bot_member.top_role


def get_bot_token() -> str:
    token = os.getenv("DISCORD_BOT_TOKEN") or os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
    if not token:
        raise SystemExit(
            "缺少 Discord token。請在部署環境設定 DISCORD_BOT_TOKEN，或改用 DISCORD_TOKEN / TOKEN。"
        )
    return token

# 🔹 按鈕 UI
class RoleView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="加密組 🔐",
        style=discord.ButtonStyle.primary,
        custom_id="role_encrypt"
    )
    async def encrypt(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_ENCRYPT)
        other = discord.utils.get(interaction.guild.roles, name=ROLE_DECRYPT)

        if role and not can_manage_role(interaction.guild, role):
            await interaction.response.send_message(
                f"❌ 無法管理【{ROLE_ENCRYPT}】。請把機器人的角色移到它上方，並開啟「管理身分組」權限。",
                ephemeral=True,
            )
            return

        if other and not can_manage_role(interaction.guild, other):
            await interaction.response.send_message(
                f"❌ 無法移除【{ROLE_DECRYPT}】。請把機器人的角色移到它上方，並開啟「管理身分組」權限。",
                ephemeral=True,
            )
            return

        if role:
            await interaction.user.add_roles(role)
        if other:
            await interaction.user.remove_roles(other)

        await interaction.response.send_message(f"已加入【{ROLE_ENCRYPT}】", ephemeral=True)

    @discord.ui.button(
        label="解密組 🔓",
        style=discord.ButtonStyle.success,
        custom_id="role_decrypt"
    )
    async def decrypt(self, interaction: discord.Interaction, button: Button):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_DECRYPT)
        other = discord.utils.get(interaction.guild.roles, name=ROLE_ENCRYPT)

        if role and not can_manage_role(interaction.guild, role):
            await interaction.response.send_message(
                f"❌ 無法管理【{ROLE_DECRYPT}】。請把機器人的角色移到它上方，並開啟「管理身分組」權限。",
                ephemeral=True,
            )
            return

        if other and not can_manage_role(interaction.guild, other):
            await interaction.response.send_message(
                f"❌ 無法移除【{ROLE_ENCRYPT}】。請把機器人的角色移到它上方，並開啟「管理身分組」權限。",
                ephemeral=True,
            )
            return

        if role:
            await interaction.user.add_roles(role)
        if other:
            await interaction.user.remove_roles(other)

        await interaction.response.send_message(f"已加入【{ROLE_DECRYPT}】", ephemeral=True)

# 🔹 Bot 上線
@bot.event
async def on_ready():
    global _startup_button_sent

    print(f"Bot 已上線：{bot.user}")
    bot.add_view(RoleView())  # 讓按鈕永久有效

    if _startup_button_sent or AUTO_SEND_CHANNEL_ID == 0:
        return

    channel = bot.get_channel(AUTO_SEND_CHANNEL_ID)
    if channel is None:
        channel = await bot.fetch_channel(AUTO_SEND_CHANNEL_ID)

    await channel.send("請選擇你的組別：", view=RoleView())
    _startup_button_sent = True

# 🔹 發送按鈕
@bot.command()
async def role(ctx):
    await ctx.send("請選擇你的組別：", view=RoleView())



def main():
    bot.run(get_bot_token())


if __name__ == "__main__":
    main()