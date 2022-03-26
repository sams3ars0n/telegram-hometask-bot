from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from utils import save_database, read_database, get_date, detect_day, get_int_of_week, get_year, get_good_date, get_int_of_month, get_current_day, get_date_from_now, get_beauty_date
from utils import days, days_week, months, days_per_month, int_months
from configparser import ConfigParser
from os import environ

db_read = read_database()

try:
    cfp = ConfigParser()
    cfp.read("config.ini")
    API_ID = cfp["pyrogram"]["api_id"]
    API_HASH = cfp["pyrogram"]["api_hash"]
    BOT_TOKEN = cfp["pyrogram"]["bot_token"]
    OWNER_ID = int(cfp["bot"]["OWNER_ID"])
except:
    API_ID = environ.get("API_ID")
    API_HASH = environ.get("API_HASH")
    BOT_TOKEN = environ.get("BOT_TOKEN")
    OWNER_ID = int(environ.get("OWNER_ID"))

if db_read is None:
    db = {"Chats": {}, "LogsGroupID": None}
else:
    db = db_read

app = Client("hometask-telegram-group-bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_callback_query()
async def handle_callbacks(client, callback_query):
    data = callback_query.data
    logs_chat_id = db["LogsGroupID"]
    if data.split(";")[0] == "timetable":
        show_date = data.split(";")[1]
        date = get_good_date(data.split(";")[1])
        chat_id = int(data.split(";")[2])
        if logs_chat_id is not None:
            user_mention = callback_query.from_user.mention
            try:
                await app.send_message(chat_id=int(logs_chat_id), text=f"User: {user_mention}\nChat: {chat_id}\nRequested timetable")
            except:
                pass
        if chat_id not in db["Chats"]:
            return await callback_query.answer("This chat is not supported by the bot.", show_alert=True)
        if date not in db["Chats"][chat_id]["Timetable"]:
            return await callback_query.answer("The specified date was not found in this chat's timetable.", show_alert=True)
        if db["Chats"][chat_id]["Timetable"][date]["Timetable"] is None:
            return await callback_query.answer("There is no timetable for this day.", show_alert=True)
        output = f"__**Hometask Telegram Group Bot**__\n\Timetable for {db['Chats'][chat_id]['Timetable'][date]['Day']} ({get_beauty_date(show_date)}):\n"
        for num, subject in enumerate(db["Chats"][chat_id]["Timetable"][date]["Timetable"]):
            if type(db['Chats'][chat_id]['Timetable'][date]['Timetable'][subject]) == str:
                output += f"{num + 1}. {subject}\n**Homework:** {db['Chats'][chat_id]['Timetable'][date]['Timetable'][subject]}\n"
            elif type(db['Chats'][chat_id]['Timetable'][date]['Timetable'][subject]) == dict:
                output += f"{num + 1}. {subject}\n**Homework:**\n__1 group__: {db['Chats'][chat_id]['Timetable'][date]['Timetable'][subject][1]}\n__2 group__: {db['Chats'][chat_id]['Timetable'][date]['Timetable'][subject][2]}\n"
        await callback_query.answer()
        if len(db['Chats'][chat_id]['Timetable'][date]["Media"]) != 0:
            reply_markup_send = []
            for subject in db['Chats'][chat_id]['Timetable'][date]["Media"]:
                if subject[-1].isdigit():
                    reply_markup_send.append([InlineKeyboardButton(f"View photos by subject {subject} {subject[-1]} group", callback_data=f"show_image;{chat_id};{subject};{date}")])
                else:
                    reply_markup_send.append([InlineKeyboardButton(f"View photos by subject {subject}", callback_data=f"show_image;{chat_id};{subject};{date}")])
            return await app.send_message(chat_id=chat_id, text=output, reply_markup=InlineKeyboardMarkup(reply_markup_send), disable_web_page_preview=True)
        return await app.send_message(chat_id=chat_id, text=output, disable_web_page_preview=True)
    elif data.split(";")[0] == "add":
        chat_id = int(data.split(";")[1])
        subject = data.split(";")[2]
        show_subject = subject
        add_command_requested_id = int(data.split(";")[3])
        user_id = callback_query.from_user.id
        callback_message = callback_query.message
        if logs_chat_id is not None:
            user_mention = callback_query.from_user.mention
            try:
                await app.send_message(chat_id=logs_chat_id, text=f"User: {user_mention}\nChat: {chat_id}\nRequested adding")
            except:
                pass
        if chat_id not in db["Chats"]:
            return await callback_query.answer("This chat is not supported by the bot.", show_alert=True)
        if user_id != OWNER_ID and user_id not in db["Chats"][chat_id]["Editors"]:
            return await callback_query.answer("You are not the editor of this chat.", show_alert=True)
        if user_id != add_command_requested_id:
            return await callback_query.answer("You cannot use this writting session because another user started it.", show_alert=True)
        await callback_query.answer()
        await callback_message.delete()
        if subject[-1].isdigit():
            show_subject = subject[:-1:]
        return await app.send_message(chat_id=chat_id, text=f"Send a homework message in response to this message. Subject: {show_subject}\n\nREQID={subject}_{user_id}")
    elif data.split(";")[0] == "delete":
        show_date = data.split(";")[1]
        date = get_good_date(data.split(";")[1])
        chat_id = int(data.split(";")[2])
        right_user_id = int(data.split(";")[3])
        user_id = callback_query.from_user.id
        message_id = callback_query.message.message_id
        if logs_chat_id is not None:
            user_mention = callback_query.from_user.mention
            try:
                await app.send_message(chat_id=logs_chat_id, text=f"User: {user_mention}\nUser id: {user_id}\nRight user id: {right_user_id}\nChat: {chat_id}\nRequested deleting")
            except:
                pass
        if chat_id not in db["Chats"]:
            return await callback_query.answer("This chat is not supported by the bot.", show_alert=True)
        if user_id != OWNER_ID and user_id not in db["Chats"][chat_id]["Editors"]:
            return await callback_query.answer("You are not the editor of this chat.", show_alert=True)
        if date not in db["Chats"][chat_id]["Timetable"]:
            return await callback_query.answer("The specified date was not found in this chat's timetable.", show_alert=True)
        if user_id != right_user_id:
            return await callback_query.answer("You cannot use this homework session because another user started it.", show_alert=True)
        await callback_query.answer()
        reply_markup_send = []
        output = f"__**Hometask Telegram Group Bot**__\n\nDelete homework on {db['Chats'][chat_id]['Timetable'][date]['Day']} ({get_beauty_date(show_date)}) by subject:"
        for subject in db["Chats"][chat_id]["Timetable"][date]["Timetable"]:
            if subject in db["Chats"][chat_id]["2grp"]:
                reply_markup_send.append([InlineKeyboardButton(f"{subject} - 1 group", callback_data=f"fd;{chat_id};{subject}1;{date};{right_user_id}")])
                reply_markup_send.append([InlineKeyboardButton(f"{subject} - group 2", callback_data=f"fd;{chat_id};{subject}2;{date};{right_user_id}")])
            else:
                reply_markup_send.append([InlineKeyboardButton(f"{subject}", callback_data=f"fd;{chat_id};{subject};{date};{right_user_id}")])
        return await app.edit_message_text(chat_id=chat_id, message_id=message_id, text=output, reply_markup=InlineKeyboardMarkup(reply_markup_send))
    elif data.split(";")[0] == "fd":
        show_date = data.split(";")[3]
        date = get_good_date(data.split(";")[3])
        subject =  data.split(";")[2]
        chat_id = int(data.split(";")[1])
        right_user_id = int(data.split(";")[4])
        user_id = callback_query.from_user.id
        callback_message = callback_query.message
        if logs_chat_id is not None:
            user_mention = callback_query.from_user.mention
            try:
                await app.send_message(chat_id=logs_chat_id, text=f"User: {user_mention}\nChat: {chat_id}\nUser id: {user_id}\nRight user id: {right_user_id}\nRequested deleting subject {subject}")
            except:
                pass
        if chat_id not in db["Chats"]:
            return await callback_query.answer("This chat is not supported by the bot.", show_alert=True)
        if user_id != OWNER_ID and user_id not in db["Chats"][chat_id]["Editors"]:
            return await callback_query.answer("You are not the editor of this chat.", show_alert=True)
        if date not in db["Chats"][chat_id]["Timetable"]:
            return await callback_query.answer("The specified date was not found in this chat's timetable.", show_alert=True)
        if user_id != right_user_id:
            return await callback_query.answer("You cannot use this homework session because another user started it.", show_alert=True)
        await callback_query.answer()
        group = None
        if subject[-1].isdigit() and subject[:-1:] in db["Chats"][chat_id]["2grp"]:
            group = int(subject[-1])
            subject = subject[:-1:]
        if group is None and subject not in db["Chats"][chat_id]["2grp"]:
            db["Chats"][chat_id]["Timetable"][date]["Timetable"][subject] = ""
            if subject in db["Chats"][chat_id]["Timetable"][date]["Media"]:
                del db["Chats"][chat_id]["Timetable"][date]["Media"][subject]
            await callback_message.delete()
            save_database(db)
            return await app.send_message(chat_id=chat_id, text=f"__**Hometask Telegram Group Bot**__\n\nHometask for {db['Chats'][chat_id]['Timetable'][date]['Day']} ({ get_beauty_date(date)}) on the subject {subject} was deleted successfully.")
        else:
            db["Chats"][chat_id]["Timetable"][date]["Timetable"][subject][group] = ""
            media_check = f"{subject}{group}"
            if media_check in db["Chats"][chat_id]["Timetable"][date]["Media"]:
                del db["Chats"][chat_id]["Timetable"][date]["Media"][media_check]
            await callback_message.delete()
            save_database(db)
            return await app.send_message(chat_id=chat_id, text=f"__**Hometask Telegram Group Bot**__\n\nHometask for {db['Chats'][chat_id]['Timetable'][date]['Day']} ({ get_beauty_date(date)}) on subject {subject} for group {group} was deleted successfully.")
    elif data.split(";")[0] == "show_image":
        chat_id = int(data.split(";")[1])
        subject = data.split(";")[2]
        date = data.split(";")[3]
        if logs_chat_id is not None:
            user_mention = callback_query.from_user.mention
            try:
                await app.send_message(chat_id=logs_chat_id, text=f"User: {user_mention}\nChat: {chat_id}\nRequested showing image")
            except:
                pass
        if chat_id not in db["Chats"]:
            return await callback_query.answer("This chat is not supported by the bot.", show_alert=True)
        if date not in db["Chats"][chat_id]["Timetable"]:
            return await callback_query.answer("The date was not found in the timetable.", show_alert=True)
        if subject not in db["Chats"][chat_id]["Timetable"][date]["Media"]:
            return await callback_query.answer("No photos were found for this item for this date.", show_alert=True)
        await callback_query.answer()
        if len(db["Chats"][chat_id]["Timetable"][date]["Media"][subject]) > 1:
            media_pack = []
            for media_file in db["Chats"][chat_id]["Timetable"][date]["Media"][subject]:
                media_pack.append(InputMediaPhoto(media_file))
            return await app.send_media_group(chat_id=chat_id, media=media_pack)
        elif len(db["Chats"][chat_id]["Timetable"][date]["Media"][subject]) == 1:
            return await app.send_photo(chat_id=chat_id, photo=db["Chats"][chat_id]["Timetable"][date]["Media"][subject][0])
    elif data[:15:] == "full_user_info:":
        user_id = callback_query.from_user.id
        callback_message = callback_query.message
        if user_id == OWNER_ID and callback_message.chat.id == OWNER_ID:
            return await app.send_message(chat_id=OWNER_ID, text=str(data[15::]), disable_notification=True)
    elif data[:18:] == "full_message_info:":
        user_id = callback_query.from_user.id
        callback_message = callback_query.message
        if user_id == OWNER_ID and callback_message.chat.id == OWNER_ID:
            return await app.send_message(chat_id=OWNER_ID, text=str(data[18::]), disable_notification=True)
    return


@app.on_message(filters.private & ~filters.user(OWNER_ID))
async def catch_motherfuckers(client, message):
    await app.send_message(chat_id=OWNER_ID, text=f"Someone sent a private message to me. Info:\n\nUser: {message.from_user.mention}\nMessage text: {message.text}\nDoes message contain media: {message.media}")
    owner = await app.get_users(OWNER_ID)
    return await message.reply_text(f"Only {owner.mention} is allowed to control the bot via private messages.")


@app.on_message(filters.command("help") & filters.private & filters.user(OWNER_ID))
async def owner_help(client, message):
    return await message.reply_text(f"Telegram Hometask Group Bot\n\nRelease: 2.0\nStatus: alive\nDate: {get_date()}\n\nList of commands:\nManage chats:\n/add_chat\n/list_chat\n/remove_chat\n/leave_chat\n\nManage timetable:\n/set_timetable\n/apply_timetable")


@app.on_message(filters.command("add_chat") & filters.private & filters.user(OWNER_ID))
async def addchat_command(client, message):
    if len(message.text.split()) != 2:
        return await message.reply_text("Command syntax: /addchat [Chat ID]")
    new_chat_id = int(message.text.split()[1])
    try:
        chat_info = await app.get_chat(new_chat_id)
    except:
        return await message.reply_text("I'm not in the chat whose ID you provided.")
    else:
        db["Chats"][new_chat_id] = {"Timetable": {}, "BaseTimetable":
            {'Monday': None, 'Tuesday': None, 'Wednesday': None, 'Thursday': None, 'Friday': None, 'Sunday': None, 'Saturday': None}, "Title": chat_info.title, "Editors": [], "Subjects": [], "2grp": []}
        save_database(db)
    return await message.reply_text(f'Chat "{chat_info.title}" added to the list of supported.')


@app.on_message(filters.command("list_chat") & filters.private & filters.user(OWNER_ID))
async def listchat_command(client, message):
    output = "List of chats supported by the bot:\n"
    if len(db["Chats"]) == 0:
        return await message.reply_text("The bot has no supported chats.")
    for chat_id in db["Chats"]:
        try:
            chat_info = await app.get_chat(chat_id)
        except:
            output += f'- "{db["Chats"][chat_id]["Title"]}" ({chat_id}) | Failed to retrieve chat information. Most likely, the bot is no longer in this chat.\n'
        else:
            if chat_info.title != db["Chats"][chat_id]["Title"]:
                db["Chats"][chat_id]["Title"] = chat_info.title
            output += f'- "{db["Chats"][chat_id]["Title"]}" ({chat_id})\n'
    save_database(db)
    return await message.reply_text(output)


@app.on_message(filters.command("remove_chat") & filters.private & filters.user(OWNER_ID))
async def removechat_command(client, message):
    if len(message.text.split()) != 2:
        return await message.reply_text("Command syntax: /removechat [Chat ID]")
    chat_id = int(message.text.split()[1])
    if chat_id not in db["Chats"]:
        return await message.reply_text("The specified chat is not supported by the bot, or you have already removed it from the list of supported ones.")
    chat_title = db["Chats"][chat_id]["Title"]
    del db["Chats"][chat_id]
    save_database(db)
    return await message.reply_text(f'Chat "{chat_title}" ({chat_id}) has been removed from the list of supported chats. Use the /leave_chat command to leave this chat.')


@app.on_message(filters.command("leave_chat") & filters.private & filters.user(OWNER_ID))
async def leavechat_command(client, message):
    if len(message.text.split()) != 2:
        return await message.reply_text("Command syntax: /leave_chat [Chat ID]")
    chat_id = int(message.text.split()[1])
    try:
        chat_info = await app.get_chat(chat_id)
    except:
        return await message.reply_text("I'm not in the chat whose ID you provided.")
    try:
        await chat_info.leave()
    except:
        return await message.reply_text("An error occurred while trying to leave the chat.")
    else:
        return await message.reply_text(f'Bot successfully left the "{chat_info.title}" chat ({chat_id}).')


@app.on_message(filters.command("set_timetable") & filters.private & filters.user(OWNER_ID))
async def set_timetable(client, message):
    if len(message.text.split()) < 4:
        return await message.reply_text("Command syntax: /set_timetable [Chat ID] [Day of the week] [Lessons in order, separated by semicolons]")
    chat_id = int(message.text.split()[1])
    day_of_week = list(message.text.split()[2].lower())
    day_of_week[0] = day_of_week[0].upper()
    day_of_week = "".join(day_of_week)
    subjects = message.text[message.text.find(message.text.split()[3])::].split(";")
    subj_add = {}
    for subject in subjects:
        if subject[-2::] == "[]":
            subj_add[subject[:-2:]] = {1: "", 2: ""}
        else:
            subj_add[subject] = ""
    if chat_id not in db["Chats"]:
        return await message.reply_text("This chat is not supported by the bot. Add it using /add_chat command")
    if day_of_week not in days:
        return await message.reply_text("Unknown day of the week.")
    day_of_week = detect_day(day_of_week)
    if len(subjects) <= 0:
        return await message.reply_text("None of the items were written.")
    db["Chats"][chat_id]["BaseTimetable"][day_of_week] = subj_add
    save_database(db)
    output_timetable = ""
    for i in range(len(subjects)):
        if subjects[i][-2::] == "[]":
            output_timetable += f"{i + 1}. {subjects[i][:-2:]} (Two groups)\n"
        else:
            output_timetable += f"{i+1}. {subjects[i]}\n"
    return await message.reply_text(f"The default timetable for {db['Chats'][chat_id]['Title']} has been set to day {day_of_week}:\n{output_timetable}")


@app.on_message(filters.command("apply_timetable") & filters.private & filters.user(OWNER_ID))
async def apply_timetable(client, message):
    if len(message.text.split()) != 2:
        return await message.reply_text("Command syntax: /apply_timtable [Chat ID]")
    chat_id = int(message.text.split()[1])
    if chat_id not in db["Chats"]:
        return await message.reply_text("This chat is not supported by the bot. Add it using the /addchat command")
    current_date_day = get_current_day()
    current_month = get_int_of_month()
    current_day = get_int_of_week() + 1
    current_year = get_year()[2::]
    for num, month in enumerate(months):
        if current_month == int(months[month]):
            month_to_start_from = num + 1
            current_month_str = month
            break
    for i in range(current_date_day, days_per_month[current_month_str] + 1):
        if current_day == 8:
            current_day = 1
        date = f"{i}.{current_month}.{current_year}"
        db["Chats"][chat_id]["Timetable"][date] = {"Day": days_week[current_day], "Timetable": db["Chats"][chat_id]["BaseTimetable"][days_week[current_day]], "Media": {}}
        current_day += 1
    for month in list(months)[month_to_start_from::]:
        if current_year != "22" and month == "January":
            current_year = "22"
        current_month_days = days_per_month[month]
        for i in range(1, current_month_days + 1):
            if current_day == 8:
                current_day = 1
            date = f"{i}.{months[month]}.{current_year}"
            db["Chats"][chat_id]["Timetable"][date] = {"Day": days_week[current_day], "Timetable": db["Chats"][chat_id]["BaseTimetable"][days_week[current_day]], "Media": {}}
            current_day += 1
    subjects_list = []
    for day in db["Chats"][chat_id]["BaseTimetable"]:
        if db["Chats"][chat_id]["BaseTimetable"][day] is not None:
            for subject in db["Chats"][chat_id]["BaseTimetable"][day]:
                subjects_list.append(subject)
                if type(db["Chats"][chat_id]["BaseTimetable"][day][subject]) == dict:
                    db["Chats"][chat_id]["2grp"].append(subject)
    db["Chats"][chat_id]["Subjects"] = sorted(set(subjects_list))
    save_database(db)
    return await message.reply_text(f'Successfully applied timetable for chat "{db["Chats"][chat_id]["Title"]}"')


@app.on_message(filters.command("set_logs_group") & filters.private & filters.user(OWNER_ID))
async def set_logs_group(client, message):
    chat_id = int(message.text.split()[1])
    try:
        logs_chat = await app.get_chat(chat_id)
    except:
        return await message.reply_text("I'm not in the log chat with the ID you provided.")
    db["LogsGroupID"] = chat_id
    save_database(db)
    return await message.reply_text(f'Now the logs will be sent to the group "{logs_chat.title}" ({chat_id}).')


@app.on_message(filters.command("logs_group") & filters.private & filters.user(OWNER_ID))
async def set_logs_group(client, message):
    if db["LogsGroupID"] is None:
        return await message.reply_text("This bot has no logging group configured.")
    chat_id = int(db["LogsGroupID"])
    try:
        logs_chat = await app.get_chat(chat_id)
    except:
        return await message.reply_text("An error occurred while getting group information for logs.")
    return await message.reply_text(f'This bot has a group for logs - "{logs_chat.title}" ({chat_id}).')


@app.on_message(filters.command("remove_logs_group") & filters.private & filters.user(OWNER_ID))
async def set_logs_group(client, message):
    if db["LogsGroupID"] is None:
        return await message.reply_text("This bot has no logging group configured.")
    chat_id = int(db["LogsGroupID"])
    try:
        await app.leave_chat(chat_id)
    except:
        return await message.reply_text("An error occurred while leaving the logging group.")
    return await message.reply_text(f'The bot has successfully left the log group.')


@app.on_message(filters.command(["help", "help@HometaskTelegramBot"]) & ~filters.private)
async def group_help(client, message):
    if message.chat.id in list(db["Chats"].keys()):
        return await app.send_message(message.chat.id, "__**Hometask Telegram bot**__ by @sams3arson\n\nCommands:\n/timetable - view the timetable with homework for this week\n/add - write down homework\n/delete - delete homework for any subject for a day")
    else:
        return await app.send_message(message.chat.id, "This chat is not supported by the bot.")


@app.on_message(filters.command(["timetable", "timetable@HometaskTelegramBot"]) & ~filters.private)
async def check_timetable(client, message):
    if message.chat.id in list(db["Chats"].keys()):
        logs_chat_id = db["LogsGroupID"]
        if logs_chat_id is not None:
            user_mention = message.from_user.mention
            try:
                await app.send_message(chat_id=logs_chat_id, text=f"User: {user_mention}\nChat: {message.chat.id}\nRequested timetable")
            except:
                pass
        reply_markup_send = []
        current_day = get_int_of_week() + 1
        for i in range(8):
            if current_day == 8:
                current_day = 1
            reply_markup_send.append([InlineKeyboardButton(f"{days_week[current_day]} - {get_date_from_now(i)}", callback_data=f"timetable;{get_date_from_now(i)};{message.chat.id}")])
            current_day += 1
        return await app.send_message(message.chat.id, "__**Hometask Telegram Group Bot**__\n\nView timetable for:", reply_markup=InlineKeyboardMarkup(reply_markup_send))
    else:
        return await app.send_message(message.chat.id, "This chat is not supported by the bot.")


@app.on_message(filters.command(["add", "add@HometaskTelegramBot"]) & ~filters.private)
async def add_hometask(client, message):
    if message.chat.id in list(db["Chats"].keys()):
        chat_id = message.chat.id
        if message.from_user.id == OWNER_ID or message.from_user.id in db["Chats"][chat_id]["Editors"]:
            if len(db["Chats"][chat_id]["Subjects"]) == 0:
                return await message.reply_text("This chat is not timetabled.")
            reply_markup = []
            for subject in db["Chats"][chat_id]["Subjects"]:
                if subject in db["Chats"][chat_id]["2grp"]:
                    reply_markup.append([InlineKeyboardButton(f"{subject} - 1 group", callback_data=f"add;{message.chat.id};{subject}1;{message.from_user.id}")])
                    reply_markup.append([InlineKeyboardButton(f"{subject} - group 2", callback_data=f"add;{message.chat.id};{subject}2;{message.from_user.id}")])
                else:
                    reply_markup.append([InlineKeyboardButton(subject, callback_data=f"add;{message.chat.id};{subject};{message.from_user.id}")])
            return await app.send_message(message.chat.id, "__**Hometask Telegram Group Bot**__\n\nSelect an item to write to:", reply_markup=InlineKeyboardMarkup(reply_markup))
        else:
            return await message.reply_text("You are not the editor of this chat.")
    else:
        return await app.send_message(message.chat.id, "This chat is not supported by the bot.")


@app.on_message(filters.command(["delete", "delete@HometaskTelegramBot"]) & ~filters.private)
async def delete_hometask(client, message):
    if message.chat.id in list(db["Chats"].keys()):
        chat_id = message.chat.id
        if message.from_user.id == OWNER_ID or message.from_user.id in db["Chats"][chat_id]["Editors"]:
            reply_markup_send = []
            current_day = get_int_of_week() + 1
            for i in range(8):
                if current_day == 8:
                    current_day = 1
                reply_markup_send.append([InlineKeyboardButton(f"{days_week[current_day]} - {get_date_from_now(i)}", callback_data=f"delete;{get_date_from_now(i)};{message.chat.id};{message.from_user.id}")])
                current_day += 1
            return await app.send_message(message.chat.id, "__**Hometask Telegram Group Bot**__\n\nSelect the day you want to delete homework for:", reply_markup=InlineKeyboardMarkup(reply_markup_send))
        else:
            return await message.reply_text("You are not the editor of this chat.")
    else:
        return await app.send_message(message.chat.id, "This chat is not supported by the bot.")


@app.on_message(filters.command(["set_editors", "set_editors@HometaskTelegramBot"]) & ~filters.private & filters.user(OWNER_ID))
async def set_editors(client, message):
    if message.chat.id in list(db["Chats"].keys()):
        text = message.text
        if len(text.split()) < 2:
            return await message.reply_text("Usage: /set_editors [IDs of users allowed to edit homework separated by a semicolon]")
        try:
            editors_list = list(map(int, text[text.find(text.split()[1])::].split(";")))
        except:
            return await message.reply_text("Invalid user IDs.")
        chat_members = await app.get_chat_members(chat_id=message.chat.id)
        chat_id = message.chat.id
        output = f'New users in the group "{db["Chats"][chat_id]["Title"]}":\n'
        for editor in editors_list:
            found = False
            for chat_member in chat_members:
                if editor == chat_member.user.id:
                    found = True
                    output += f"- {chat_member.user.mention} ({chat_member.user.id})\n"
            if not found:
                return await app.send_message(chat_id=chat_id, text=f"User with ID {editor} was not found in this chat.")
        try:
            db["Chats"][message.chat.id]["Editors"].extend(editors_list)
            save_database(db)
        except:
            return await message.reply_text("Failed to add these users to the list of editing d / z.")
        else:
            return await message.reply_text(output)
    else:
        return await app.send_message(message.chat.id, "This chat is not supported by the bot.")


@app.on_message(filters.command(["list_editors", "list_editors@HometaskTelegramBot"]) & ~filters.private & filters.user(OWNER_ID))
async def list_editors(client, message):
    if message.chat.id in list(db["Chats"].keys()):
        text = message.text
        if len(text.split()) != 1:
            return await message.reply_text("Usage: /list_editors")
        chat_id = message.chat.id
        output = f'List of editing homework in group "{db["Chats"][chat_id]["Title"]}":\n'
        if len(db['Chats'][chat_id]['Editors']) == 0:
            return await app.send_message(chat_id=chat_id, text=f'The list of editing homework in the group "{db["Chats"][chat_id]["Title"]}" is empty.')
        for editor in db['Chats'][chat_id]['Editors']:
            try:
                temp_user_info = await app.get_users(editor)
            except:
                output += f"- Failed to get information about this user. ({editor})"
            else:
                output += f"- {temp_user_info.mention} ({temp_user_info.id})\n"
        return await message.reply_text(output)
    else:
        return await app.send_message(message.chat.id, "This chat is not supported by the bot.")


@app.on_message(filters.command(["remove_editors", "remove_editors@HometaskTelegramBot"]) & ~filters.private & filters.user(OWNER_ID))
async def remove_editors(client, message):
    if message.chat.id in list(db["Chats"].keys()):
        text = message.text
        if len(text.split()) < 2:
            return await message.reply_text("Usage: /remove_editors [IDs of users to be removed from the editing files separated by a semicolon]")
        try:
            editors_list = list(map(int, text[text.find(text.split()[1])::].split(";")))
        except:
            return await message.reply_text("Invalid user IDs.")
        chat_id = message.chat.id
        output = f'The following users have been removed from editing homework in the group "{db["Chats"][chat_id]["Title"]}":\n'
        for editor in editors_list:
            try:
                temp_user_info = await app.get_users(editor)
            except:
                if editor not in db["Chats"][chat_id]["Editors"]:
                    return await message.reply_text(f"The user ({editor}) whose information could not be retrieved is not in the list of editors for this chat.")
                del db["Chats"][chat_id]["Editors"][editor]
                output += f"- {editor} (Could not get information about this user)."
            else:
                if editor not in db["Chats"][chat_id]["Editors"]:
                    return await message.reply_text(f"The user {temp_user_info.mention} ({temp_user_info.id}) is not in the list of editing children for this chat.")
                editor_index = [x for x in range(len(db["Chats"][chat_id]["Editors"])) if db["Chats"][chat_id]["Editors"][x] == editor][0]
                del db["Chats"][chat_id]["Editors"][editor_index]
                output += f"- {temp_user_info.mention} ({temp_user_info.id})\n"
        save_database(db)
        return await message.reply_text(output)
    else:
        return await app.send_message(message.chat.id, "This chat is not supported by the bot.")


@app.on_message(filters.command(["clear_editors", "clear_editors@HometaskTelegramBot"]) & ~filters.private & filters.user(OWNER_ID))
async def clear_editors(client, message):
    if message.chat.id in list(db["Chats"].keys()):
        text = message.text
        if len(text.split()) != 1:
            return await message.reply_text("Usage: /clear_editors")
        chat_id = message.chat.id
        output = f'The list of editing homework in the group "{db["Chats"][chat_id]["Title"]}" has been completely cleared.'
        db["Chats"][chat_id]["Editors"] = []
        save_database(db)
        return await message.reply_text(output)


@app.on_message(~filters.private & filters.reply)
async def handle_hometask_adding(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if chat_id in db["Chats"] and (user_id in db["Chats"][chat_id]["Editors"] or user_id == OWNER_ID) and message.reply_to_message.from_user.is_self and message.reply_to_message.text[:74:] == \
            "Send a homework message in response to this message. Subject:":
        subject = message.reply_to_message.text.split("=")[-1].split("_")[0]
        user_right_id = int(message.reply_to_message.text.split("=")[-1].split("_")[1])
        if user_id != user_right_id:
            return
        message_photo = False
        if message.media:
            if message.photo is not None:
                message_photo = True
                file_id = message.photo.file_id
                if message.caption is not None:
                    hometask = str(message.caption)
                else:
                    hometask = None
            else:
                return await message.reply_text("Only photos are supported.")
        else:
            hometask = str(message.text)
        group = None
        await message.reply_to_message.delete()
        if subject[-1].isdigit() and subject[:-1:] in db["Chats"][chat_id]["2grp"]:
            group = int(subject[-1])
            subject = subject[:-1:]
        if int(get_current_day()) == int(days_per_month[int_months[int(get_int_of_month())]]):
            if get_int_of_month() == 12:
                index = [x for x in range(len(list(db["Chats"][chat_id]["Timetable"].keys()))) if list(db["Chats"][chat_id]["Timetable"].keys())[x] == f"1.1.{int(get_year()[2::]) + 1}"]
            else:
                index = [x for x in range(len(list(db["Chats"][chat_id]["Timetable"].keys()))) if list(db["Chats"][chat_id]["Timetable"].keys())[x] == f"1.{int(get_int_of_month()) + 1}.{get_year()[2::]}"]
        else:
            index = [x for x in range(len(list(db["Chats"][chat_id]["Timetable"].keys()))) if list(db["Chats"][chat_id]["Timetable"].keys())[x] == f"{get_current_day() + 1}.{get_int_of_month()}.{get_year()[2::]}"]
        if len(index) == 0:
            return await message.reply_text(f"An error occurred while searching for this day in the timetable.")
        index = index[0]
        for date in list(db["Chats"][chat_id]["Timetable"].keys())[index::]:
            if db["Chats"][chat_id]["Timetable"][date]["Timetable"] is not None and subject in db["Chats"][chat_id]["Timetable"][date]["Timetable"]:
                if group is None:
                    if message_photo:
                        file_path = await app.download_media(file_id)
                        if file_path is None:
                            return await message.reply_text("Failed to download photo.")
                        if hometask is not None:
                            db["Chats"][chat_id]["Timetable"][date]["Timetable"][subject] = hometask
                        if subject not in db["Chats"][chat_id]["Timetable"][date]["Media"]:
                            db["Chats"][chat_id]["Timetable"][date]["Media"][subject] = []
                        db["Chats"][chat_id]["Timetable"][date]["Media"][subject].append(file_path)
                        save_database(db)
                        return await message.reply_text(f"Homework with photos on subject {subject} on {get_beauty_date(date)} ({db['Chats'][chat_id]['Timetable'][date]['Day']}) successfully written.")
                    db["Chats"][chat_id]["Timetable"][date]["Timetable"][subject] = hometask
                    save_database(db)
                    return await message.reply_text(f"{subject} homework on {get_beauty_date(date)} ({db['Chats'][chat_id]['Timetable'][date]['Day']}) successfully written.")
                else:
                    if message_photo:
                        subject_add = f"{subject}{group}"
                        file_path = await app.download_media(file_id)
                        if file_path is None:
                            return await message.reply_text("Failed to download photo.")
                        if hometask is not None:
                            db["Chats"][chat_id]["Timetable"][date]["Timetable"][subject][group] = hometask
                        if subject_add not in db["Chats"][chat_id]["Timetable"][date]["Media"]:
                            db["Chats"][chat_id]["Timetable"][date]["Media"][subject_add] = []
                        db["Chats"][chat_id]["Timetable"][date]["Media"][subject_add].append(file_path)
                        save_database(db)
                        return await message.reply_text(f"Homework with photos on subject {subject} for {group} group on {get_beauty_date(date)} ({db['Chats'][chat_id]['Timetable'][date]['Day']}) was written successfully.")
                    db["Chats"][chat_id]["Timetable"][date]["Timetable"][subject][group] = hometask
                    save_database(db)
                    return await message.reply_text(f"{subject} homework for {group} group on {get_beauty_date(date)} ({db['Chats'][chat_id]['Timetable'][date]['Day']}) was written successfully.")
app.run()