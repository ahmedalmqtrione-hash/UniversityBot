from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_student_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📚 جدول المحاضرات", callback_data='schedule'),
         InlineKeyboardButton("📢 التعميمات", callback_data='view_announcements')],
        [InlineKeyboardButton("🔗 الروابط العادية", callback_data='view_links'),
         InlineKeyboardButton("🔐 الروابط المشفرة", callback_data='view_secure_links')],
        [InlineKeyboardButton("📂 الملفات والكورسات", callback_data='view_files'),
         InlineKeyboardButton("🎮 الألعاب", callback_data='games')],
        [InlineKeyboardButton("⚙️ لوحة تحكم المدير", callback_data='admin')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ])

def get_admin_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 إنشاء تعميم", callback_data='announce'),
         InlineKeyboardButton("📂 رفع ملف", callback_data='upload_file')],
        [InlineKeyboardButton("🔗 إضافة رابط (عادي)", callback_data='add_link'),
         InlineKeyboardButton("🔐 إضافة رابط (مشفر)", callback_data='add_secure')],
        [InlineKeyboardButton("👑 إضافة مستخدم/مدير", callback_data='add_user'),
         InlineKeyboardButton("📤 بث ذكي", callback_data='broadcast')],
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')]
    ])

def get_back_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 رجوع", callback_data='back')],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data='home')]
    ])

def get_secure_links_menu(links):
    keyboard = []
    for i, link in enumerate(links):
        keyboard.append([InlineKeyboardButton(f"🔒 رابط {i+1}", callback_data=f"secure_{i}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back')])
    return InlineKeyboardMarkup(keyboard)

def get_files_list(files):
    keyboard = []
    for i, file in enumerate(files):
        icon = "📄" if file['name'].endswith('.pdf') else "🖼️" if file['name'].endswith(('.jpg','.png','.jpeg')) else "🎬" if file['name'].endswith(('.mp4','.avi','.mkv')) else "📁"
        keyboard.append([InlineKeyboardButton(f"{icon} {file['name']}", callback_data=f"file_{i}")])
    keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data='back')])
    return InlineKeyboardMarkup(keyboard)
