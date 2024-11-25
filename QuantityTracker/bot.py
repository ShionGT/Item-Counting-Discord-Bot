import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import re

# Load the .env file
load_dotenv()

# Get the token from the .env file
TOKEN = os.getenv("DISCORD_TOKEN")

# Intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent for reading messages

# Set up the bot
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to track counts per channel
channel_item_counts = {}

# Dictionary to track targets for items
item_targets = {}  # Format: {channel_id: {item: [(user_id, target_count)]}}

# Helper function to parse item counts from a message
def parse_items(message_content):
    # Match patterns like "+1,033 green apples", "+5 red apples", or "+1.5 green apples"
    pattern = r"\+([\d,]+(?:\.\d+)?)\s+([\w\s]+)"
    matches = re.findall(pattern, message_content.lower())

    # Sanitize item names and convert counts by removing commas
    sanitized_items = [(float(count.replace(",", "")), item.strip().replace("\n", " ")) for count, item in matches]
    return sanitized_items

# Helper function to get the counts dictionary for a specific channel
def get_channel_counts(channel_id):
    if channel_id not in channel_item_counts:
        channel_item_counts[channel_id] = {}
    return channel_item_counts[channel_id]

# Helper function to get or initialize targets for a channel
def get_channel_targets(channel_id):
    if channel_id not in item_targets:
        item_targets[channel_id] = {}
    return item_targets[channel_id]

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Bot is ready!")

@bot.event
async def on_message(message):
    # Ignore the bot's own messages
    if message.author == bot.user:
        return

    # Collect text from both the message content and embeds
    message_content = message.content  # Standard message content

    # Add embedded content if present
    if message.embeds:
        for embed in message.embeds:
            if embed.description:
                message_content += f"\n{embed.description}"  # Add the embed description
            if embed.title:
                message_content += f"\n{embed.title}"  # Add the embed title

            # If the embed has fields, add them too
            for field in embed.fields:
                message_content += f"\n{field.name}: {field.value}"

    # Parse items from the collected content
    items = parse_items(message_content)

    # Update the counts for the current channel
    channel_counts = get_channel_counts(message.channel.id)
    for count, item in items:
        if item in channel_counts:
            channel_counts[item] += count
        else:
            channel_counts[item] = count

    # Check for targets and notify users if met
    channel_targets = get_channel_targets(message.channel.id)
    for item, target_list in list(channel_targets.items()):  # Iterate over a copy to modify safely
        if item in channel_counts:
            current_count = channel_counts[item]
            for user_id, target_count in target_list:
                if current_count >= target_count:
                    user = await message.guild.fetch_member(user_id)
                    if user:
                        await message.channel.send(f"{user.mention}, the target count for '{item}' has been reached! 🎉 (Current count: {current_count})")
                    channel_targets[item].remove((user_id, target_count))  # Remove the fulfilled target

            # Remove item from targets if all targets are fulfilled
            if not channel_targets[item]:
                del channel_targets[item]

    # Acknowledge the message (optional)
    if items:
        await message.channel.send(f"Updated counts for this channel: {channel_counts}")

    # Ensure commands still work
    await bot.process_commands(message)


# Command: Show counts for the current channel
@bot.command()
async def counts(ctx):
    channel_counts = get_channel_counts(ctx.channel.id)
    if not channel_counts:
        await ctx.send("No items have been counted in this channel yet.")
    else:
        counts_message = "\n".join([f"{item}: {count}" for item, count in channel_counts.items()])
        await ctx.send(f"Current item counts for this channel:\n{counts_message}")

# Command: Reset counts for the current channel
@bot.command()
async def reset(ctx):
    channel_item_counts[ctx.channel.id] = {}
    await ctx.send("All item counts for this channel have been reset.")

# Command: Set a target for an item
@bot.command()
async def set_target(ctx, target_count: int, *, item: str):
    if target_count <= 0:
        await ctx.send("Please provide a valid target count greater than zero.")
        return

    # Sanitize item name
    item = item.strip().replace("\n", " ")

    channel_targets = get_channel_targets(ctx.channel.id)
    if item not in channel_targets:
        channel_targets[item] = []
    channel_targets[item].append((ctx.author.id, target_count))

    await ctx.send(f"Target set: I'll notify {ctx.author.mention} when '{item}' reaches {target_count}!")

# Command: Reset counts for all channels (admin only)
@bot.command()
@commands.has_permissions(administrator=True)
async def reset_all(ctx):
    channel_item_counts.clear()
    await ctx.send("All item counts for all channels have been reset.")

@bot.command()
async def stop(ctx):
    if str(ctx.author.id) == os.getenv("OWNER_ID"):
        print("Stop Requested. The bot will now go offline.")
        await ctx.send("Stop Requested. The bot will now go offline.")
        exit(0)
    await ctx.send("You do not have permissions to stop this bot.")

# Command: Show all targets for the current channel
@bot.command()
async def targets(ctx):
    channel_targets = get_channel_targets(ctx.channel.id)
    if not channel_targets:
        await ctx.send("No targets have been set in this channel.")
    else:
        targets_message = "\n".join([f"{item}: {', '.join([f'<@{user_id}> ({target_count})' for user_id, target_count in target_list])}" for item, target_list in channel_targets.items()])
        await ctx.send(f"Current targets for this channel:\n{targets_message}")

# Run the bot
bot.run(TOKEN)
