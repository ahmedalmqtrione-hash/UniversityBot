import os
import logging
import time
import subprocess
import sys
from datetime import datetime

import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

from config import TOKEN, DEVELOPER_NAME, UNIVERSITY_NAME, BOT_NAME
from database import load_data, save_data
from security import security
from ui_builder import get_student_menu, get_admin_menu, get_back_menu, get_secure_links_menu, get_files_list, get_media_gallery_menu

# التثبيت التلقائي للمكتبات
def install_packages():
    required = ['requests', 'pillow', 'imageio']
    for package in required:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

install_packages()
import requests

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# معالج الأخطاء
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, telegram.error.BadRequest):
        return
    elif isinstance(context.error, telegram.error.Conflict):
        print("⚠️ تم اكتشاف تعارض. سيتم إعادة التشغيل...")
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        logging.error(f"Update {update} caused error {context.error}")

# الجدول الذكي
def get_smart_schedule():
    now = datetime.now()
    days = ["الاثنين","الثلاثاء","الأربعاء","الخميس","الجمعة","السبت","الأحد"]
    today = days[now.weekday()]
    SCHEDULE = {
        "السبت":"10-8 لغة C++ (أ/ رحاب) | 12-10 إنجليزي (أ/ اسري)",
        "الأحد":"11-8 احتمالات (د/ الصلوي) | 2-12 ويب (أ/ بشينة)",
        "الاثنين":"10-8 محاسبة (أ/ سارة) | 12-10 عربي (د/ رضوان)",
        "الثلاثاء":"10-8 ويب عملي (أ/ أمنية) | 12-10 ويب عملي (أ/ أمنية)",
        "الأربعاء":"10-8 مهارات (د/ المشرفي) | 12-10 C++ عملي (أ/ الشيباني)",
        "الخميس":"🎉 إجازة رسمية 🎉",
        "الجمعة":"🎉 إجازة أسبوعية 🎉"
    }
    return f"📅 *اليوم: {today}*\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n📚 *المحاضرات:*\n{SCHEDULE.get(today, 'لا يوجد جدول')}"

# معالج البدء
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)
    
    if user_id == 123456789:  # ضع معرفك هنا
        if user_id not in data["admins"]:
            data["admins"].append(user_id)
            save_data(data)
    
    if not data["admins"]:
        data["admins"].append(user_id)
        save_data(data)
    
    await update.message.reply_text(
        f"🔥 *النظام الخارق النهائي V-Final*\n📌 المطور: {DEVELOPER_NAME}\nاختر قسمك:",
        parse_mode='Markdown',
        reply_markup=get_student_menu()
    )

# معالج الأزرار (القلب)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    data = load_data()

    if query.data == 'back':
        await query.edit_message_text("🔙 رجوع", reply_markup=get_back_menu())
        return

    if query.data == 'home':
        await query.edit_message_text("🏠 القائمة الرئيسية:", reply_markup=get_student_menu())
        return

    if query.data == 'schedule':
        await query.edit_message_text(get_smart_schedule(), parse_mode='Markdown', reply_markup=get_back_menu())
        return

    if query.data == 'view_announcements':
        announcements = data.get("announcements", [])
        if not announcements:
            await query.edit_message_text("📢 لا توجد تعميمات.", reply_markup=get_back_menu())
            return
        keyboard = []
        for i, ann in enumerate(announcements):
            keyboard.append([InlineKeyboardButton(f"📌 {ann['title']}", callback_data=f"ann_{i}")])
        keyboard.append([InlineKeyboardButton("🔙", callback_data='back')])
        await query.edit_message_text("📢 *قائمة التعميمات:*", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data.startswith('ann_'):
        idx = int(query.data.replace('ann_', ''))
        announcements = data.get("announcements", [])
        if 0 <= idx < len(announcements):
            await query.edit_message_text(
                f"📢 *{announcements[idx]['title']}*\n\n{announcements[idx]['text']}",
                parse_mode='Markdown', reply_markup=get_back_menu()
            )
        return

    if query.data == 'view_links':
        links = data.get("links", [])
        keyboard = [[InlineKeyboardButton(l['title'], url=l['url'])] for l in links]
        keyboard.append([InlineKeyboardButton("🔙", callback_data='back')])
        await query.edit_message_text("🔗 *الروابط العادية:*", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if query.data == 'view_secure_links':
        secure_links = data.get("secure_links", [])
        if not secure_links:
            await query.edit_message_text("🔐 لا توجد روابط مشفرة.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("🔐 *الروابط المشفرة:*\nاضغط للحصول على رمز الدخول.", parse_mode='Markdown', reply_markup=get_secure_links_menu(secure_links))
        return

    if query.data.startswith('secure_'):
        idx = int(query.data.replace('secure_', ''))
        secure_links = data.get("secure_links", [])
        if 0 <= idx < len(secure_links):
            token = security.generate_token(secure_links[idx]['link'])
            await query.edit_message_text(
                f"🔑 *رمز الدخول:* `{token}`\n⏰ صالح لمدة 5 دقائق.\n\nانسخ الرمز وأرسله للبوت لفتح الرابط.",
                parse_mode='Markdown', reply_markup=get_back_menu()
            )
        return

    # ==========================================
    # قسم عرض الوسائط (Media Gallery)
    # ==========================================
    if query.data == 'view_media':
        files = data.get("files", [])
        if not files:
            await query.edit_message_text("📂 لا توجد وسائط مرفوعة بعد.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("📂 *صالة العرض (عرض مباشر داخل البوت):*", parse_mode='Markdown', reply_markup=get_media_gallery_menu(files))
        return

    if query.data.startswith('play_'):
        idx = int(query.data.replace('play_', ''))
        files = data.get("files", [])
        if 0 <= idx < len(files):
            file_name = files[idx]['name']
            file_url = files[idx]['url']
            
            # إرسال الوسائط بدون تحميل
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                await update.callback_query.message.reply_photo(photo=file_url, caption=f"🖼️ *{file_name}*", parse_mode='Markdown')
            elif file_name.lower().endswith(('.mp4', '.avi', '.mkv', '.webm')):
                await update.callback_query.message.reply_video(video=file_url, caption=f"🎬 *{file_name}*", parse_mode='Markdown')
            elif file_name.lower().endswith('.pdf'):
                await update.callback_query.message.reply_document(document=file_url, caption=f"📄 *{file_name}* (عرض/تحميل)", parse_mode='Markdown')
            else:
                await update.callback_query.message.reply_document(document=file_url, caption=f"📂 *{file_name}*", parse_mode='Markdown')
            
            await query.edit_message_text("✅ تم تشغيل الوسائط.", reply_markup=get_back_menu())
        return

    if query.data == 'games':
        await query.edit_message_text("🎮 *الألعاب*", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 ألعاب ذكاء", url="https://poki.com")],
            [InlineKeyboardButton("💻 محاكي كالي", url="https://www.onlinekali.com")],
            [InlineKeyboardButton("🔙", callback_data='back')]
        ]))
        return

    if query.data == 'admin':
        if user_id not in data["admins"]:
            await query.edit_message_text("⛔ هذا القسم للمدير فقط.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("⚙️ *لوحة تحكم المدير*", parse_mode='Markdown', reply_markup=get_admin_menu())
        return

    if query.data == 'announce':
        if user_id not in data["admins"]:
            await query.edit_message_text("⛔ هذا القسم للمدير فقط.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("📢 أرسل نص التعميم (سيتم إضافته للقائمة):", parse_mode='Markdown', reply_markup=get_back_menu())
        context.user_data['state'] = 'announce_text'
        return

    if query.data == 'upload_file':
        if user_id not in data["admins"]:
            await query.edit_message_text("⛔ هذا القسم للمدير فقط.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("📂 أرسل الملف (فيديو، PDF، صورة، وورد، إكسل):", parse_mode='Markdown', reply_markup=get_back_menu())
        context.user_data['state'] = 'upload_file'
        return

    if query.data == 'add_link':
        if user_id not in data["admins"]:
            await query.edit_message_text("⛔ هذا القسم للمدير فقط.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("🔗 أرسل: العنوان, الرابط", reply_markup=get_back_menu())
        context.user_data['state'] = 'add_link'
        return

    if query.data == 'add_secure':
        if user_id not in data["admins"]:
            await query.edit_message_text("⛔ هذا القسم للمدير فقط.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("🔐 أرسل الرابط الذي تريد تشفيره:", reply_markup=get_back_menu())
        context.user_data['state'] = 'add_secure'
        return

    if query.data == 'add_user':
        if user_id not in data["admins"]:
            await query.edit_message_text("⛔ هذا القسم للمدير فقط.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("👑 أرسل معرف المستخدم أو المدير الجديد (رقم):", reply_markup=get_back_menu())
        context.user_data['state'] = 'add_user'
        return

    if query.data == 'broadcast':
        if user_id not in data["admins"]:
            await query.edit_message_text("⛔ هذا القسم للمدير فقط.", reply_markup=get_back_menu())
            return
        await query.edit_message_text("📤 *البث الذكي*", reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📤 واتساب", url="https://wa.me/?text=تعميم_من_البوت")],
            [InlineKeyboardButton("📤 تليجرام", url="https://t.me/share/url?text=تعميم_من_البوت")],
            [InlineKeyboardButton("🔙", callback_data='back')]
        ]))
        return

# معالج الرسائل
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    state = context.user_data.get('state')
    data = load_data()

    if state == 'announce_text':
        if user_id not in data["admins"]:
            await update.message.reply_text("⛔ هذا القسم للمدير فقط.", reply_markup=get_back_menu())
            context.user_data.clear()
            return
        data.setdefault("announcements", []).append({"title": "تعميم جديد", "text": text, "date": str(datetime.now())})
        save_data(data)
        await update.message.reply_text("✅ تم إضافة التعميم بنجاح.", reply_markup=get_admin_menu())
        context.user_data.clear()
        return

    if state == 'upload_file':
        await update.message.reply_text("📂 تم استلام الأمر. أرسل الملف الآن.", reply_markup=get_back_menu())
        context.user_data['file_upload'] = True
        return

    if state == 'add_link':
        parts = text.split(',')
        if len(parts) == 2:
            data["links"].append({"title": parts[0].strip(), "url": parts[1].strip()})
            save_data(data)
            await update.message.reply_text("✅ تم إضافة الرابط.", reply_markup=get_admin_menu())
        else:
            await update.message.reply_text("⚠️ التنسيق: العنوان, الرابط", reply_markup=get_admin_menu())
        context.user_data.clear()
        return

    if state == 'add_secure':
        token = security.generate_token(text)
        data["secure_links"].append({"token": token, "link": text})
        save_data(data)
        await update.message.reply_text(
            f"🔐 *رابط مشفر*\n🔑 رمز الدخول: `{token}`\n⏰ صالح لمدة 5 دقائق",
            parse_mode='Markdown', reply_markup=get_admin_menu()
        )
        context.user_data.clear()
        return

    if state == 'add_user':
        try:
            new_id = int(text.strip())
            if new_id not in data["users"]:
                data["users"].append(new_id)
                save_data(data)
                await update.message.reply_text(f"👤 تم إضافة المستخدم {new_id}.", reply_markup=get_admin_menu())
            else:
                await update.message.reply_text("⚠️ هذا المعرف موجود مسبقاً.", reply_markup=get_admin_menu())
        except:
            await update.message.reply_text("⚠️ أرسل رقماً صحيحاً.", reply_markup=get_admin_menu())
        context.user_data.clear()
        return

# معالج الملفات
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = load_data()
    if user_id not in data["admins"]:
        await update.message.reply_text("⛔ رفع الملفات للمدير فقط.", reply_markup=get_back_menu())
        return
    
    file = await update.message.document.get_file() if update.message.document else await update.message.photo[-1].get_file()
    file_bytes = await file.download_as_bytearray()
    file_name = update.message.document.file_name if update.message.document else f"photo_{datetime.now().timestamp()}.jpg"
    file_url = f"https://universityai-bot.onrender.com/uploads/{file_name}"
    data["files"].append({"name": file_name, "url": file_url})
    save_data(data)
    await update.message.reply_text(
        f"📂 *تم رفع الملف بنجاح!*\n\n📄 الاسم: {file_name}\n🔗 اضغط للعرض أو التحميل:\n{file_url}",
        parse_mode='Markdown',
        reply_markup=get_admin_menu()
    )

# التشغيل الرئيسي
def start_bot():
    try:
        print("🤖 تشغيل البوت الخارق...")
        app = Application.builder().token(TOKEN).connect_timeout(30).read_timeout(30).write_timeout(30).build()
        app.add_error_handler(error_handler)
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))
        app.run_polling()
    except Exception as e:
        print(f"⚠️ حدث خطأ جوهري: {e}")
        print("🔄 إعادة التشغيل خلال 10 ثواني...")
        time.sleep(10)
        start_bot()

if __name__ == "__main__":
    start_bot()
