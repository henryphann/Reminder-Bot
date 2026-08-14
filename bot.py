import os
import asyncio
from datetime import datetime
import discord
from discord.ext import commands, tasks
from discord import app_commands
from dotenv import load_dotenv
from database import init_db, add_reminder, get_pending_reminders, delete_reminder

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Setting up a Bot subclass is the cleanest way to sync slash commands
class ReminderBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

    async def setup_hook(self):
        # This synchronizes the new slash commands to Discord when the bot starts
        await self.tree.sync()
        check_reminders.start()

bot = ReminderBot()

@bot.event
async def on_ready():
    init_db()
    print(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    print("Slash commands synced and ready to go!")

# ---------------------------------------------------------
# Slash Command: /remind
# ---------------------------------------------------------
@bot.tree.command(name="remind", description="Sets a personal reminder.")
@app_commands.describe(
    date_str="The date (Format: YYYY-MM-DD)",
    time_str="The time (Format: HH:MM in 24-hour time)",
    message="What do you want to be reminded about?"
)
async def remind(interaction: discord.Interaction, date_str: str, time_str: str, message: str):
    try:
        full_time_str = f"{date_str} {time_str}"
        remind_dt = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")
        
        if remind_dt <= datetime.now():
            # ephemeral=True means only the user who typed the command sees this error
            await interaction.response.send_message("❌ Error: The reminder time must be in the future.", ephemeral=True)
            return

        add_reminder(interaction.user.id, interaction.channel_id, message, remind_dt.strftime("%Y-%m-%d %H:%M"))
        await interaction.response.send_message(f"✅ Success! I will remind you here about: **{message}** on `{full_time_str}`.")

    except ValueError:
        await interaction.response.send_message("❌ Invalid format! Please use YYYY-MM-DD for the date and HH:MM for the time.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ An unexpected error occurred: {e}", ephemeral=True)

# ---------------------------------------------------------
# Slash Command: /remindother
# ---------------------------------------------------------
@bot.tree.command(name="remindother", description="Sets a reminder for someone else.")
@app_commands.describe(
    member="Select the user to remind",
    date_str="The date (Format: YYYY-MM-DD)",
    time_str="The time (Format: HH:MM in 24-hour time)",
    message="What do you want to remind them about?"
)
async def remindother(interaction: discord.Interaction, member: discord.Member, date_str: str, time_str: str, message: str):
    try:
        full_time_str = f"{date_str} {time_str}"
        remind_dt = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")
        
        if remind_dt <= datetime.now():
            await interaction.response.send_message("❌ Error: The reminder time must be in the future.", ephemeral=True)
            return

        add_reminder(member.id, interaction.channel_id, message, remind_dt.strftime("%Y-%m-%d %H:%M"))
        await interaction.response.send_message(f"✅ Success! I will remind {member.display_name} here about: **{message}** on `{full_time_str}`.")

    except ValueError:
        await interaction.response.send_message("❌ Invalid format! Please use YYYY-MM-DD for the date and HH:MM for the time.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"⚠️ An unexpected error occurred: {e}", ephemeral=True)

# ---------------------------------------------------------
# Background Task
# ---------------------------------------------------------
@tasks.loop(seconds=30)
async def check_reminders():
    """Background loop to check and dispatch due reminders."""
    try:
        pending = get_pending_reminders()
        for row in pending:
            reminder_id, user_id, channel_id, reminder_text, remind_at = row
            channel = bot.get_channel(channel_id)
            if channel:
                try:
                    await channel.send(f"⏰ <@{user_id}> **Reminder Alert!** You asked me to remind you: *{reminder_text}*")
                except discord.Forbidden:
                    print(f"Could not send message to channel {channel_id} (Missing permissions).")
            delete_reminder(reminder_id)
    except Exception as e:
        print(f"Error in background task: {e}")

bot.run(TOKEN)
