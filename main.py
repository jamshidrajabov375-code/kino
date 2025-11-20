from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import json
import os

# Bot tokeningizni kiriting
BOT_TOKEN = "8531222565:AAEQzA4sZ3Q6qDtjan2phdxMHkVfXU1qaco"

# Admin ID (o'z telegram ID ingizni kiriting)
ADMIN_ID = 7877174037  # O'z ID ingizni kiriting

# Kinolar ma'lumotlari uchun fayl
MOVIES_FILE = "movies.json"
USERS_FILE = "users.json"
CHANNELS_FILE = "channels.json"

# Kinolar bazasini yuklash
def load_movies():
    if os.path.exists(MOVIES_FILE):
        with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Kinolar bazasini saqlash
def save_movies(movies):
    with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)

# Foydalanuvchilarni yuklash
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# Foydalanuvchilarni saqlash
def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# Kanallarni yuklash
def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

# Kanallarni saqlash
def save_channels(channels):
    with open(CHANNELS_FILE, 'w', encoding='utf-8') as f:
        json.dump(channels, f, ensure_ascii=False, indent=2)

movies_db = load_movies()
users_db = load_users()
channels_list = load_channels()

# Admin klaviaturasi
def admin_keyboard():
    keyboard = [
        [KeyboardButton("🎬 Kino yuklash")],
        [KeyboardButton("🔍 Kino izlash"), KeyboardButton("📝 Kino bot yasash")],
        [KeyboardButton("📊 Statistika"), KeyboardButton("📢 Yangilik tashlash")],
        [KeyboardButton("⚙️ Majburiy obuna")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Majburiy obuna sozlamalari klaviaturasi
def subscription_settings_keyboard():
    keyboard = [
        [KeyboardButton("➕ Kanal qo'shish")],
        [KeyboardButton("📋 Kanallar ro'yxati"), KeyboardButton("🗑 Kanal o'chirish")],
        [KeyboardButton("🔙 Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Obuna tekshirish funksiyasi
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    if not channels_list:
        return True  # Agar kanallar yo'q bo'lsa, ruxsat berish
    
    for channel in channels_list:
        try:
            member = await context.bot.get_chat_member(chat_id=channel['id'], user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"Xatolik kanal tekshirishda {channel['id']}: {e}")
            continue
    
    return True

# Obuna klaviaturasi
def subscription_keyboard():
    keyboard = []
    for channel in channels_list:
        keyboard.append([InlineKeyboardButton(f"✅ {channel['name']}", url=channel['link'])])
    keyboard.append([InlineKeyboardButton("♻️ Tekshirish", callback_data="check_subscription")])
    return InlineKeyboardMarkup(keyboard)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    # Foydalanuvchini bazaga qo'shish
    if str(user_id) not in users_db:
        users_db[str(user_id)] = {
            'id': user_id,
            'username': user.username,
            'first_name': user.first_name,
            'joined_date': update.message.date.strftime("%Y-%m-%d %H:%M:%S")
        }
        save_users(users_db)
    
    total_users = len(users_db)
    
    if user_id == ADMIN_ID:
        # Admin uchun
        welcome_text = f"""
👋 Salom Admin {user.first_name}!

👥 Bot obunachilari: {total_users} ta

🎬 Kino yuklash - Yangi kino qo'shish
🔍 Kino izlash - Kino kodini kiritib topish
📝 Kino bot yasash - Yangi bot yaratish
⚙️ Majburiy obuna - Kanallarni sozlash

Qaysi amalni bajarasiz?
"""
        await update.message.reply_text(
            welcome_text, 
            reply_markup=admin_keyboard()
        )
    else:
        # Oddiy foydalanuvchi uchun - obunani tekshirish
        if channels_list and not await check_subscription(user_id, context):
            await update.message.reply_text(
                f"👋 Salom {user.first_name}!\n\n"
                "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
                reply_markup=subscription_keyboard()
            )
        else:
            welcome_text = f"""
🎬 Salom {user.first_name}!

Kino botiga xush kelibsiz!

👥 Bot obunachilari: {total_users} ta
🎥 Jami kinolar: {len(movies_db)} ta

📝 Kino kodini kiriting va kino yuklang!

Misol: 1234
"""
            await update.message.reply_text(welcome_text)

# Callback handler (Tekshirish tugmasi)
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data == "check_subscription":
        if await check_subscription(user_id, context):
            total_users = len(users_db)
            await query.message.edit_text(
                f"✅ Obuna tasdiqlandi!\n\n"
                f"🎬 Kino botiga xush kelibsiz!\n\n"
                f"👥 Bot obunachilari: {total_users} ta\n"
                f"🎥 Jami kinolar: {len(movies_db)} ta\n\n"
                f"📝 Kino kodini kiriting va kino yuklang!\n\n"
                f"Misol: 1234"
            )
        else:
            await query.message.edit_text(
                "❌ Siz hali barcha kanallarga obuna bo'lmadingiz!\n\n"
                "Iltimos, barcha kanallarga obuna bo'ling va qayta tekshiring.",
                reply_markup=subscription_keyboard()
            )

# Admin tugmalarni boshqarish
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    # Oddiy foydalanuvchi uchun obunani tekshirish
    if user_id != ADMIN_ID:
        if channels_list and not await check_subscription(user_id, context):
            await update.message.reply_text(
                "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
                reply_markup=subscription_keyboard()
            )
            return
        # Obuna bo'lgan bo'lsa - kino kodini qidirish
        await search_by_code(update, context)
        return
    
    # Admin tugmalari
    if text == "🎬 Kino yuklash":
        context.user_data.clear()
        context.user_data['action'] = 'upload'
        context.user_data['step'] = 'code'
        await update.message.reply_text(
            "📝 Kino kodini kiriting:\n\n"
            "Misol: 1234"
        )
    
    elif text == "🔍 Kino izlash":
        context.user_data.clear()
        context.user_data['action'] = 'search'
        context.user_data['search_mode'] = True
        await update.message.reply_text(
            "🔍 Kino kodini kiriting:\n\n"
            "Misol: 1234\n\n"
            "❌ Bekor qilish uchun /cancel yozing"
        )
    
    elif text == "📝 Kino bot yasash":
        await update.message.reply_text(
            "📝 Kino bot yasash uchun menga lichkamga yozing:\n\n"
            f"👉 @Javookhr\n\n"
            "Yoki pastdagi tugmani bosing:",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✉️ Admin bilan bog'lanish", url=f"tg://user?id={ADMIN_ID}")
            ]])
        )
    
    elif text == "📊 Statistika":
        await show_statistics(update, context)
    
    elif text == "📢 Yangilik tashlash":
        context.user_data.clear()
        context.user_data['action'] = 'broadcast'
        await update.message.reply_text(
            "📢 Yangilikni yuboring:\n\n"
            "Matn, rasm, video yoki audio yuborishingiz mumkin.\n\n"
            "❌ Bekor qilish: /cancel"
        )
    
    elif text == "⚙️ Majburiy obuna":
        context.user_data.clear()
        await update.message.reply_text(
            "⚙️ Majburiy obuna sozlamalari\n\n"
            f"📊 Hozirda {len(channels_list)} ta kanal qo'shilgan\n\n"
            "Qaysi amalni bajarasiz?",
            reply_markup=subscription_settings_keyboard()
        )
    
    elif text == "➕ Kanal qo'shish":
        context.user_data.clear()
        context.user_data['action'] = 'add_channel'
        context.user_data['step'] = 'name'
        await update.message.reply_text(
            "📝 Kanal nomini kiriting:\n\n"
            "Misol: Kino Kanali"
        )
    
    elif text == "📋 Kanallar ro'yxati":
        await show_channels_list(update, context)
    
    elif text == "🗑 Kanal o'chirish":
        if not channels_list:
            await update.message.reply_text(
                "❌ Hozircha kanallar yo'q!",
                reply_markup=subscription_settings_keyboard()
            )
        else:
            context.user_data.clear()
            context.user_data['action'] = 'delete_channel'
            channels_text = "🗑 O'chirish uchun kanal raqamini kiriting:\n\n"
            for idx, channel in enumerate(channels_list, 1):
                channels_text += f"{idx}. {channel['name']}\n"
            channels_text += "\n❌ Bekor qilish: /cancel"
            await update.message.reply_text(channels_text)
    
    elif text == "🔙 Orqaga":
        context.user_data.clear()
        await update.message.reply_text(
            "🔙 Asosiy menyu",
            reply_markup=admin_keyboard()
        )
    
    else:
        # Admin uchun matn kiritilsa
        await handle_admin_input(update, context)

# Kanallar ro'yxatini ko'rsatish
async def show_channels_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not channels_list:
        await update.message.reply_text(
            "❌ Hozircha kanallar yo'q!",
            reply_markup=subscription_settings_keyboard()
        )
    else:
        channels_text = "📋 Majburiy obuna kanallari:\n\n"
        for idx, channel in enumerate(channels_list, 1):
            channels_text += f"{idx}. {channel['name']}\n"
            channels_text += f"   🔗 {channel['link']}\n"
            channels_text += f"   🆔 {channel['id']}\n\n"
        
        await update.message.reply_text(
            channels_text,
            reply_markup=subscription_settings_keyboard()
        )

# Admin ma'lumot kiritishi
async def handle_admin_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    action = context.user_data.get('action')
    step = context.user_data.get('step')
    text = update.message.text
    
    # Yangilik tashlash
    if action == 'broadcast':
        await broadcast_message(update, context)
        return
    
    # Kanal qo'shish
    if action == 'add_channel':
        if step == 'name':
            context.user_data['channel_name'] = text
            context.user_data['step'] = 'link'
            await update.message.reply_text(
                "🔗 Kanal havolasini kiriting:\n\n"
                "Misol: https://t.me/your_channel"
            )
        elif step == 'link':
            context.user_data['channel_link'] = text
            context.user_data['step'] = 'id'
            await update.message.reply_text(
                "🆔 Kanal ID sini kiriting:\n\n"
                "Misol: @your_channel yoki -1001234567890\n\n"
                "⚠️ Muhim: Botni kanalga admin qilib qo'shing!"
            )
        elif step == 'id':
            channel_id = text.strip()
            channel_name = context.user_data.get('channel_name')
            channel_link = context.user_data.get('channel_link')
            
            # Kanalni qo'shish
            new_channel = {
                'name': channel_name,
                'link': channel_link,
                'id': channel_id
            }
            channels_list.append(new_channel)
            save_channels(channels_list)
            
            await update.message.reply_text(
                f"✅ Kanal muvaffaqiyatli qo'shildi!\n\n"
                f"📝 Nom: {channel_name}\n"
                f"🔗 Havola: {channel_link}\n"
                f"🆔 ID: {channel_id}\n\n"
                f"📊 Jami kanallar: {len(channels_list)} ta",
                reply_markup=subscription_settings_keyboard()
            )
            context.user_data.clear()
    
    # Kanal o'chirish
    elif action == 'delete_channel':
        try:
            channel_num = int(text.strip())
            if 1 <= channel_num <= len(channels_list):
                deleted_channel = channels_list.pop(channel_num - 1)
                save_channels(channels_list)
                await update.message.reply_text(
                    f"✅ Kanal o'chirildi!\n\n"
                    f"📝 Nom: {deleted_channel['name']}\n\n"
                    f"📊 Qolgan kanallar: {len(channels_list)} ta",
                    reply_markup=subscription_settings_keyboard()
                )
                context.user_data.clear()
            else:
                await update.message.reply_text(
                    f"❌ Noto'g'ri raqam! 1 dan {len(channels_list)} gacha kiriting."
                )
        except ValueError:
            await update.message.reply_text("❌ Iltimos, raqam kiriting!")
    
    # Kino yuklash jarayoni
    elif action == 'upload':
        if step == 'code':
            context.user_data['movie_code'] = text
            context.user_data['step'] = 'info'
            await update.message.reply_text(
                "📋 Kino haqida ma'lumot kiriting:\n\n"
                "Misol:\n"
                "📌 Nomi: Avatar 2\n"
                "📅 Yili: 2022\n"
                "🎭 Janr: Fantastika\n"
                "⭐ Reyting: 8.5/10"
            )
        
        elif step == 'info':
            context.user_data['movie_info'] = text
            context.user_data['step'] = 'video'
            await update.message.reply_text(
                "🎥 Endi kino videosini yuboring:"
            )
    
    # Kino izlash
    elif action == 'search':
        movie_code = text.strip()
        
        if movie_code in movies_db:
            movie = movies_db[movie_code]
            await update.message.reply_video(
                video=movie['file_id'],
                caption=f"✅ Kino topildi!\n\n{movie['info']}\n\n📝 Kod: {movie_code}"
            )
            await update.message.reply_text(
                "🔍 Boshqa kino kodini kiriting yoki /cancel bosing"
            )
        else:
            await update.message.reply_text(
                f"❌ '{movie_code}' kodli kino topilmadi!\n\n"
                f"Boshqa kod kiriting yoki /cancel bosing"
            )

# Video qabul qilish
async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Siz faqat kino kodini kiritishingiz mumkin!")
        return
    
    action = context.user_data.get('action')
    step = context.user_data.get('step')
    
    # Yangilik tashlash uchun video
    if action == 'broadcast':
        await broadcast_message(update, context)
        return
    
    if action == 'upload' and step == 'video':
        video = update.message.video or update.message.document
        movie_code = context.user_data.get('movie_code')
        movie_info = context.user_data.get('movie_info')
        
        # Kinoni saqlash
        movies_db[movie_code] = {
            'code': movie_code,
            'info': movie_info,
            'file_id': video.file_id
        }
        save_movies(movies_db)
        
        await update.message.reply_text(
            f"✅ Kino muvaffaqiyatli qo'shildi!\n\n"
            f"📝 Kod: {movie_code}\n"
            f"📊 Jami kinolar: {len(movies_db)}\n\n"
            f"Foydalanuvchilar '{movie_code}' kodi orqali topishi mumkin.",
            reply_markup=admin_keyboard()
        )
        
        context.user_data.clear()
    else:
        await update.message.reply_text(
            "❌ Avval 'Kino yuklash' tugmasini bosing!",
            reply_markup=admin_keyboard()
        )

# Oddiy foydalanuvchi uchun kino qidirish
async def search_by_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Admin emas
    if user_id == ADMIN_ID:
        return
    
    movie_code = update.message.text.strip()
    
    # Agar faqat raqamlar bo'lsa - kod deb hisoblaymiz
    if movie_code.isdigit():
        if movie_code in movies_db:
            movie = movies_db[movie_code]
            await update.message.reply_video(
                video=movie['file_id'],
                caption=f"✅ Kino topildi!\n\n{movie['info']}\n\n📝 Kod: {movie_code}\n\n@YourBotUsername orqali"
            )
        else:
            await update.message.reply_text(
                f"❌ Bu kino topilmadi!\n\n"
                f"Boshqa kod kiriting yoki adminga murojaat qiling."
            )
    else:
        # Agar raqam emas - so'z kiritilgan
        await update.message.reply_text(
            "⚠️ Iltimos, faqat kino kodini kiriting!\n\n"
            "Misol: 1234"
        )

# /cancel komandasi
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if context.user_data:
        context.user_data.clear()
        
        if user_id == ADMIN_ID:
            await update.message.reply_text(
                "❌ Jarayon bekor qilindi.",
                reply_markup=admin_keyboard()
            )
        else:
            await update.message.reply_text(
                "❌ Jarayon bekor qilindi.\n\n"
                "Kino kodini kiritishingiz mumkin."
            )
    else:
        if user_id == ADMIN_ID:
            await update.message.reply_text(
                "Hech qanday jarayon yo'q.",
                reply_markup=admin_keyboard()
            )
        else:
            await update.message.reply_text("Hech qanday jarayon yo'q.")

# Statistika (admin uchun)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != ADMIN_ID:
        return
    
    await show_statistics(update, context)

# Batafsil statistika
async def show_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_movies = len(movies_db)
    total_users = len(users_db)
    total_channels = len(channels_list)
    
    stats_text = f"""
📊 Bot statistikasi:

👥 Jami obunachlar: {total_users} ta
🎬 Jami kinolar: {total_movies} ta
📢 Majburiy kanallar: {total_channels} ta

📝 Kino kodlari:
"""
    
    if movies_db:
        for code, movie in list(movies_db.items())[:10]:
            stats_text += f"\n• {code}"
        if len(movies_db) > 10:
            stats_text += f"\n\n... va yana {len(movies_db) - 10} ta kino"
    else:
        stats_text += "\n(Hozircha kinolar yo'q)"
    
    if channels_list:
        stats_text += "\n\n📢 Majburiy kanallar:\n"
        for channel in channels_list:
            stats_text += f"• {channel['name']}\n"
    
    await update.message.reply_text(stats_text)

# Barcha foydalanuvchilarga xabar yuborish
async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    sent_count = 0
    failed_count = 0
    
    await message.reply_text("📢 Yangilik yuborilmoqda...")
    
    for user_id in users_db.keys():
        try:
            # Turli xil xabar turlarini yuborish
            if message.text and not message.text.startswith('/'):
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text=f"📢 YANGILIK\n\n{message.text}"
                )
            elif message.photo:
                caption_text = message.caption if message.caption else ""
                await context.bot.send_photo(
                    chat_id=int(user_id),
                    photo=message.photo[-1].file_id,
                    caption=f"📢 YANGILIK\n\n{caption_text}" if caption_text else "📢 YANGILIK"
                )
            elif message.video:
                caption_text = message.caption if message.caption else ""
                await context.bot.send_video(
                    chat_id=int(user_id),
                    video=message.video.file_id,
                    caption=f"📢 YANGILIK\n\n{caption_text}" if caption_text else "📢 YANGILIK"
                )
            elif message.document:
                caption_text = message.caption if message.caption else ""
                await context.bot.send_document(
                    chat_id=int(user_id),
                    document=message.document.file_id,
                    caption=f"📢 YANGILIK\n\n{caption_text}" if caption_text else "📢 YANGILIK"
                )
            elif message.audio:
                caption_text = message.caption if message.caption else ""
                await context.bot.send_audio(
                    chat_id=int(user_id),
                    audio=message.audio.file_id,
                    caption=f"📢 YANGILIK\n\n{caption_text}" if caption_text else "📢 YANGILIK"
                )
            elif message.voice:
                await context.bot.send_voice(
                    chat_id=int(user_id),
                    voice=message.voice.file_id
                )
                await context.bot.send_message(
                    chat_id=int(user_id),
                    text="📢 YANGILIK (Ovozli xabar)"
                )
            
            sent_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Xatolik user {user_id}: {e}")
    
    context.user_data.clear()
    
    await message.reply_text(
        f"✅ Yangilik yuborildi!\n\n"
        f"📤 Yuborildi: {sent_count} ta\n"
        f"❌ Xatolik: {failed_count} ta",
        reply_markup=admin_keyboard()
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Handlerlar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.ALL, handle_video))
    app.add_handler(MessageHandler(filters.PHOTO, handle_admin_input))
    app.add_handler(MessageHandler(filters.AUDIO | filters.VOICE, handle_admin_input))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("🔥 Bot WEBHOOK orqali ishga tushdi!")
    print(f"🎬 Bazada {len(movies_db)} ta kino mavjud")
    print(f"📢 {len(channels_list)} ta majburiy kanal")

    # Railway PORT (majburiy)
    PORT = int(os.environ.get("PORT", 8080))

    # SENING WEBHOOK URL'ingni shu yerga qo'yasan!
    WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )


if name == "__main__":
    main()