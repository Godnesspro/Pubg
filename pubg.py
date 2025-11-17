import telebot
from telebot import types
import sqlite3
import random

BOT_TOKEN = "8057271235:AAGjgPJmCEOWM-Uh0YmWMLM8fIQIzO-Iw4g"  # BURAYA TOKENİNİ YAZ
bot = telebot.TeleBot(BOT_TOKEN)

# REDEEM KODLARI LİSTESİ
REDEEM_KODLARI = [
    "Pubggamecodecity–1.000uc",
    "PGMB20- 3.000 gümüş parça",
    "Pubgmbgcctoday- rastgele üst silah",
    "Gamecodecitypubgmobile- Ücretsiz rastgele cilt",
    "Pubgmobgiftfree- Ücretsiz Elite Royale Pass",
    "CMCKZBZBAW- Sea Breeze Efsanesi Kuponu",
    "Pubgmbrauc- Brezilya Şampiyonası kıyafeti",
    "Clpozezveg- 20 meydan okuma puanı için kullanın",
    "Clpozdz6pp- 20 meydan okuma puanı için kullanın",
    "Clpozcztvw- 20 meydan okuma puanı için kullanın",
    "Clpozbz6je- 20 meydan okuma puanı için kullanın",
    "Clhfzfz7ve- 20 meydan okuma puanı için kullanın",
    "Pubgmbennymoza1- Benny Moza Koleksiyon Paketi 1",
    "Pubgmbennymoza2- Benny Moza Koleksiyon Paketi 2"
]

UC_KODU = "PUBG-9X7H-2LQM-4BPF"

def db_init():
    conn = sqlite3.connect('uc_bot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        referans_sayisi INTEGER DEFAULT 0,
        son_redeem_davet INTEGER DEFAULT 0,
        son_uc_davet INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS referanslar (
        referrer_id INTEGER,
        referred_id INTEGER
    )''')
    conn.commit()
    conn.close()

db_init()

@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    user_id = message.from_user.id
    
    # Referans kontrolü
    if len(args) > 1 and args[1].startswith('ref_'):
        try:
            referrer_id = int(args[1].split('_')[1])
            if referrer_id != user_id:
                conn = sqlite3.connect('uc_bot.db')
                c = conn.cursor()
                c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
                c.execute("INSERT OR IGNORE INTO referanslar VALUES (?, ?)", (referrer_id, user_id))
                c.execute("UPDATE users SET referans_sayisi = referans_sayisi + 1 WHERE user_id=?", (referrer_id,))
                conn.commit()
                conn.close()
                
                bot.send_message(user_id, "🎉 Botu başlattın! Davet edene +1 puan eklendi!")
                bot.send_message(referrer_id, "✅ YENİ DAVET GELDİ! Davet sayın arttı!")
        except:
            pass
    
    # Normal giriş
    conn = sqlite3.connect('uc_bot.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()
    
    ref_link = f"https://t.me/{bot.get_me().username}?start=ref_{user_id}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Davet Linki", callback_data=f"link_{user_id}"))
    markup.add(types.InlineKeyboardButton("📊 Durumum", callback_data="durum"))
    
    bot.send_message(message.chat.id,
        "🎮 PUBG MOBILE UC & REDEEM BOTU!\n\n"
        "💎 Her 10 davet → 60 UC\n"
        "🎁 Her 5 davet → 1 Redeem Kodu\n\n"
        "Hemen davet etmeye başla! 👇", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('link_'))
def link(call):
    user_id = int(call.data.split('_')[1])
    ref_link = f"https://t.me/{bot.get_me().username}?start=ref_{user_id}"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Paylaş", url=ref_link))
    markup.add(types.InlineKeyboardButton("📊 Durum", callback_data="durum"))
    bot.edit_message_text(f"🔗 Davet Linkin:\n<code>{ref_link}</code>\n\nHer gelen +1 davet!", 
                         call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: call.data == 'durum')
def durum(call):
    user_id = call.from_user.id
    conn = sqlite3.connect('uc_bot.db')
    c = conn.cursor()
    c.execute("SELECT referans_sayisi, son_redeem_davet, son_uc_davet FROM users WHERE user_id=?", (user_id,))
    data = c.fetchone() or (0, 0, 0)
    conn.close()
    
    ref_sayisi = data[0]
    son_redeem = data[1]
    son_uc = data[2]
    
    mesaj = f"📊 <b>DURUMUN:</b>\n👥 Toplam Davet: <b>{ref_sayisi}</b>\n\n"
    
    # Redeem kodları
    yeni_redeem = (ref_sayisi // 5) - (son_redeem // 5)
    if yeni_redeem > 0:
        mesaj += "🎁 <b>YENİ REDEEM KODLARIN:</b>\n"
        for i in range(yeni_redeem):
            kod = random.choice(REDEEM_KODLARI)
            mesaj += f"{i+1}. <code>{kod}</code>\n"
        conn = sqlite3.connect('uc_bot.db')
        c = conn.cursor()
        c.execute("UPDATE users SET son_redeem_davet=? WHERE user_id=?", (ref_sayisi // 5 * 5, user_id))
        conn.commit()
        conn.close()
    
    # 60 UC
    yeni_uc = (ref_sayisi // 10) - (son_uc // 10)
    if yeni_uc > 0:
        mesaj += f"\n💎 <b>YENİ 60 UC KODU:</b>\n<code>{UC_KODU}</code>\n"
        conn = sqlite3.connect('uc_bot.db')
        c = conn.cursor()
        c.execute("UPDATE users SET son_uc_davet=? WHERE user_id=?", (ref_sayisi // 10 * 10, user_id))
        conn.commit()
        conn.close()
    
    kalan_redeem = 5 - (ref_sayisi % 5)
    kalan_uc = 10 - (ref_sayisi % 10)
    if ref_sayisi % 5 != 0: mesaj += f"\n⏳ {kalan_redeem} davet → Redeem Kodu"
    if ref_sayisi % 10 != 0: mesaj += f"\n⏳ {kalan_uc} davet → 60 UC"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Davet Linki", callback_data=f"link_{user_id}"))
    bot.edit_message_text(mesaj, call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode="HTML")

print("PUBG UC BOTU ÇALIŞIYOR – DAVETLER ANINDA GÖRÜNÜYOR!")
bot.polling(none_stop=True)
