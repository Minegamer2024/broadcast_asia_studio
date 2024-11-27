import discord
from discord.ext import commands
from art import text2art
from dotenv import load_dotenv
import os
import json
from typing import Literal
load_dotenv()
token = os.getenv("TOKEN")
intents = discord.Intents.all()
client = commands.Bot(command_prefix="!", intents=intents)
@client.event
async def on_ready():
    art_ready = text2art("Asia studio")
    print(art_ready)
    print(f"ready {client.user}")
    await client.tree.sync()
@client.tree.command(name="role", description="لأضافة رتبة التي يمكنها استخدام البرودكاست")
@discord.app_commands.default_permissions(administrator=True)
async def add_role(interaction: discord.Interaction, func: Literal["اضافة", "ازالة"]):
    server_id = str(interaction.guild.id)
    with open("role.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    if server_id not in data:
        data[server_id] = {}
    else:
        pass
    if func == "اضافة":
        id_role = discord.ui.TextInput(
            label="ايدي",
            placeholder="يرجى كتابة ايدي الرتبة هنا",
            style=discord.TextStyle.short
        )
        modal = discord.ui.Modal(title="ايدي الرتبة")
        modal.add_item(id_role)
        async def on_submit(interaction: discord.Interaction):
            role = interaction.guild.get_role(int(id_role.value))
            if not role:
                await interaction.response.send_message("هذا الايدي غير موجود في رتب السيرفر", ephemeral=True)
                return
            print(role.id)
            if role.name in data[server_id]:
                await interaction.response.send_message("اسم هذه الرتبة موجود بالفعل ان كانت هذه رتبة جديدة فا يرجى تغيير اسمها")
            else:
                data[server_id][role.name] = role.id
                await interaction.response.send_message("تم ادخال الرتبة في قاعدة البيانات", ephemeral=True)
                with open("role.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
        modal.on_submit = on_submit
        await interaction.response.send_modal(modal)
    elif func == "ازالة":
        await interaction.response.defer(ephemeral=True)
        if not data[server_id]:
            await interaction.followup.send("لا يوجد اي رتب لألتها", ephemeral=True)
        else:
            option = []
            for role_delete in data[server_id]:
                option.append(discord.SelectOption(label=role_delete, value=role_delete))
            view = discord.ui.View(timeout=None)
            select = discord.ui.Select(placeholder="يرجى اختيار الرتبة", options=option)
            view.add_item(select)
            async def select_callback(interaction: discord.Interaction):
                del data[server_id][select.values[0]]
                with open("role.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                await interaction.response.edit_message(content="تم ازالة الرتبة من قاعدة البيانات", view=None)
            select.callback = select_callback
            await interaction.followup.send("يرجى اختيار الرتبة التي تريد ازالتها", view=view, ephemeral=True)
image_extension = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
@client.tree.command(name="broadcast_setup", description="لأرسال لوحة تحكم البرودكاست")
@discord.app_commands.default_permissions(administrator=True)
async def broadcast_member(interaction: discord.Interaction, description: str, channel: discord.TextChannel = None, image: discord.Attachment = None):
    try:
        server_id = str(interaction.guild.id)
        with open("role.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        if server_id not in data or not data[server_id]:
            await interaction.response.send_message("لا يوجد اي رتب في الوقت الحالي لأرسال لوحة البرودكاست", ephemeral=True)
        else:
            if channel == None:
                channel = interaction.channel
            else:
                pass
            view = discord.ui.View(timeout=None)
            online_button = discord.ui.Button(label="الاعضاء المتصلين", style=discord.ButtonStyle.green, emoji="🟢")
            offline_button = discord.ui.Button(label="الاعضاء الغير متصلين", style=discord.ButtonStyle.red, emoji="🔴")
            all_button = discord.ui.Button(label="لجميع الاعضاء", style=discord.ButtonStyle.primary, emoji="👤")
            member_button = discord.ui.Button(label="عضو معين", style=discord.ButtonStyle.gray, emoji="🙍🏻‍♂️")
            view.add_item(all_button)
            view.add_item(online_button)
            view.add_item(offline_button)
            view.add_item(member_button)
            async def online_callback(interaction: discord.Interaction):
                try:
                    roless = []
                    for i in data[server_id]:
                        roless.append(data[server_id][i])
                    user_roles = [role.id for role in interaction.user.roles]
                    if any(role_id in user_roles for role_id in roless):
                        message = discord.ui.TextInput(
                            label="الرسالة",
                            placeholder="يرجى كتابة الرسالة التي تريدها",
                            style=discord.TextStyle.paragraph
                        )
                        modal = discord.ui.Modal(title="كتابة الرسالة للاعضاء المتصلين")
                        modal.add_item(message)
                        async def on_submit(interaction: discord.Interaction):
                            try:
                                for m in interaction.guild.members:
                                    if not m.bot and m.status is not discord.Status.offline:
                                        await interaction.response.send_message("تم الارسال لجميع الاعضاء المتصلين", ephemeral=True)
                                        await m.send(f"{message.value}\n\n{m.mention}")
                                else:
                                    pass
                            except:
                                await interaction.response.send_message("يوجد خطأ يبدو انه لا يوجد اي اعضاء متصلين", ephemeral=True)
                        modal.on_submit = on_submit
                        await interaction.response.send_modal(modal)
                    else:
                        await interaction.response.send_message("انت لا تملك الصلاحية لأستخدام البوت", ephemeral=True)
                except:
                    await interaction.response.send_message("يوجد خطأ تقني لا يمكن فتح صفحة الارسال", ephemeral=True)
            async def offline_callback(interaction: discord.Interaction):
                try:
                    roless = []
                    for i in data[server_id]:
                        roless.append(data[server_id][i])
                    user_roles = [role.id for role in interaction.user.roles]
                    if any(role_id in user_roles for role_id in roless):
                        message = discord.ui.TextInput(
                            label="الرسالة",
                            placeholder="يرجى كتابة الرسالة التي تريدها",
                            style=discord.TextStyle.paragraph
                        )
                        modal = discord.ui.Modal(title="كتابة الرسالة للاعضاء الغير متصلين")
                        modal.add_item(message)
                        async def on_submit(interaction: discord.Interaction):
                            try:
                                for m in interaction.guild.members:
                                    if not m.bot and m.status is discord.Status.offline:
                                        await interaction.response.send_message("تم الارسال لجميع الاعضاء الغير متصلين", ephemeral=True)
                                        await m.send(f"{message.value}\n\n{m.mention}")
                                    else:
                                        pass
                            except:
                                await interaction.response.send_message("يوجد خطأ يبدو انه لا يوجد اي اعضاء غير متصلين", ephemeral=True)
                        modal.on_submit = on_submit
                        await interaction.response.send_modal(modal)
                    else:
                        await interaction.response.send_message("انت لا تملك الصلاحية لأستخدام البوت", ephemeral=True)
                except:
                    await interaction.response.send_message("يوجد خطأ تقني لا يمكن فتح صفحة الارسال", ephemeral=True)
            async def all_callback(interaction: discord.Interaction):
                try:
                    roless = []
                    for i in data[server_id]:
                        roless.append(data[server_id][i])
                    user_roles = [role.id for role in interaction.user.roles]
                    if  any(role_id in user_roles for role_id in roless):
                        message = discord.ui.TextInput(
                            label="الرسالة",
                            placeholder="يرجى كتابة الرسالة التي تريدها",
                            style=discord.TextStyle.paragraph
                        )
                        modal = discord.ui.Modal(title="كتابة الرسالة لجميع الاعضاء")
                        modal.add_item(message)
                        async def on_submit(interaction: discord.Interaction):
                            for m in interaction.guild.members:
                                if not m.bot:
                                    await interaction.response.send_message("تم الارسال لجميع الاعضاء ", ephemeral=True)
                                    await m.send(f"{message.value}\n\n{m.mention}")
                                else:
                                    pass
                        modal.on_submit = on_submit
                        await interaction.response.send_modal(modal)
                    else:
                        await interaction.response.send_message("انت لا تملك الصلاحية لأستخدام البوت", ephemeral=True)
                except:
                    await interaction.response.send_message("يوجد خطأ تقني لا يمكن فتح صفحة الارسال", ephemeral=True)
            async def member_callback(interaction: discord.Interaction):
                try:
                    roless = []
                    for i in data[server_id]:
                        roless.append(data[server_id][i])
                    user_roles = [role.id for role in interaction.user.roles]
                    if any(role_id in user_roles for role_id in roless):
                        id_member = discord.ui.TextInput(
                            label="الايدي",
                            placeholder="يرجى كتابة ايدي الشخص الذي سوف يرسل له الرسالة",
                            style=discord.TextStyle.short
                        )
                        message = discord.ui.TextInput(
                            label="الرسالة",
                            placeholder="يرجى كتابة الرسالة التي تريدها",
                            style=discord.TextStyle.paragraph
                        )
                        modal = discord.ui.Modal(title="برجى كتابة الرسالة وايدي العضو")
                        modal.add_item(id_member)
                        modal.add_item(message)
                        async def on_submit(interaction: discord.Interaction):
                            try:
                                member_check = interaction.guild.get_member(int(id_member.value))
                                if member_check:
                                    if not member_check.bot:
                                        await interaction.response.send_message(f"تم ارسال الرسالة الى العضو {member_check.mention}", ephemeral=True)
                                        await member_check.send(f"{message.value}\n\n{member_check.mention}")
                                    else:
                                        await interaction.response.send_message("لا يمكنك ارسال رسائل للبوتات", ephemeral=True)  
                                else:
                                    await interaction.response.send_message("هذا العضو غير موجود في السيرفر", ephemeral=True)
                            except:
                                await interaction.response.send_message("يوجد خطأ لا يمكنني تحديد العضو يرحى التأكد من انك ادخلت ايدي العضو بشكل صحيح", ephemeral=True)
                        modal.on_submit = on_submit
                        await interaction.response.send_modal(modal)
                    else:
                        await interaction.response.send_message("انت لا تملك الصلاحية لأستخدام البوت", ephemeral=True)
                except:
                    await interaction.response.send_message("يوجد خطأ تقني لا يمكن فتح صفحة الارسال", ephemeral=True)
            online_button.callback = online_callback
            offline_button.callback = offline_callback
            all_button.callback = all_callback
            member_button.callback = member_callback
            embed = discord.Embed(title=f"{interaction.guild.name} Broadcast", description=description, color=discord.Color.blue())
            if image and image.filename.endswith(image_extension):
                embed.set_image(url=image.url)
            else:
                pass
            embed.set_thumbnail(url=interaction.guild.icon)
            embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon)
            await interaction.response.send_message(f"تم الارسال في روم {channel.mention}", ephemeral=True)
            await channel.send(embed=embed, view=view)
    except:
        await interaction.response.send_message("يوجد خطأ لا يمكن ارسال قائمة البرودكاست")
client.run(token)
