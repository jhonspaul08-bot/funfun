import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from database import (
    init_db, get_or_create_user, get_balance, update_balance,
    add_transaction, get_history, get_total_users, get_total_transactions
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "MASUKKAN_TOKEN_DISINI")

# ===================== KEYBOARD =====================
def main_keyboard():
    keyboard = [
        [KeyboardButton("📥 Deposit"), KeyboardButton("📤 Withdraw")],
        [KeyboardButton("💰 Balance"), KeyboardButton("🔄 Exchange")],
        [KeyboardButton("📢 Ads Post & Earn 🎁")],
        [KeyboardButton("❓ Help"), KeyboardButton("📋 S&K"), KeyboardButton("📊 Statistik")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# ===================== /start =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or "", user.full_name)

    text = (
        f"👋 Halo, *{user.first_name}*!\n\n"
        f"Selamat datang di *WalletBot* 💼\n\n"
        f"✅ Akun kamu sudah terdaftar.\n"
        f"Gunakan menu di bawah untuk mulai:"
    )
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=main_keyboard())

# ===================== BALANCE =====================
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or "", user.full_name)
    bal = get_balance(user.id)

    text = (
        f"💰 *Saldo Kamu*\n\n"
        f"👤 {user.first_name}\n"
        f"💵 Saldo: *Rp{bal:,.0f}*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ===================== DEPOSIT =====================
async def deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Rp5.000", callback_data="deposit_5000"),
         InlineKeyboardButton("Rp10.000", callback_data="deposit_10000")],
        [InlineKeyboardButton("Rp25.000", callback_data="deposit_25000"),
         InlineKeyboardButton("Rp50.000", callback_data="deposit_50000")],
        [InlineKeyboardButton("Rp100.000", callback_data="deposit_100000")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel")],
    ]
    text = (
        "📥 *Deposit*\n\n"
        "Pilih nominal deposit:"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if query.data == "cancel":
        await query.edit_message_text("❌ Dibatalkan.")
        return

    amount = int(query.data.replace("deposit_", ""))
    get_or_create_user(user.id, user.username or "", user.full_name)
    update_balance(user.id, amount)
    add_transaction(user.id, "deposit", amount, f"Deposit Rp{amount:,}")
    new_bal = get_balance(user.id)

    text = (
        f"✅ *Deposit Berhasil!*\n\n"
        f"💵 Nominal: *Rp{amount:,.0f}*\n"
        f"💰 Saldo sekarang: *Rp{new_bal:,.0f}*"
    )
    await query.edit_message_text(text, parse_mode="Markdown")

# ===================== WITHDRAW =====================
async def withdraw_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or "", user.full_name)
    bal = get_balance(user.id)

    keyboard = [
        [InlineKeyboardButton("Rp5.000", callback_data="withdraw_5000"),
         InlineKeyboardButton("Rp10.000", callback_data="withdraw_10000")],
        [InlineKeyboardButton("Rp25.000", callback_data="withdraw_25000"),
         InlineKeyboardButton("Rp50.000", callback_data="withdraw_50000")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel")],
    ]
    text = (
        f"📤 *Withdraw*\n\n"
        f"💰 Saldo kamu: *Rp{bal:,.0f}*\n\n"
        f"Pilih nominal withdraw:"
    )
    await update.message.reply_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def withdraw_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    if query.data == "cancel":
        await query.edit_message_text("❌ Dibatalkan.")
        return

    amount = int(query.data.replace("withdraw_", ""))
    get_or_create_user(user.id, user.username or "", user.full_name)
    bal = get_balance(user.id)

    if bal < amount:
        await query.edit_message_text(
            f"❌ *Saldo tidak cukup!*\n\n"
            f"💰 Saldo kamu: Rp{bal:,.0f}\n"
            f"📤 Withdraw: Rp{amount:,.0f}",
            parse_mode="Markdown"
        )
        return

    update_balance(user.id, -amount)
    add_transaction(user.id, "withdraw", -amount, f"Withdraw Rp{amount:,}")
    new_bal = get_balance(user.id)

    text = (
        f"✅ *Withdraw Berhasil!*\n\n"
        f"📤 Nominal: *Rp{amount:,.0f}*\n"
        f"💰 Saldo tersisa: *Rp{new_bal:,.0f}*"
    )
    await query.edit_message_text(text, parse_mode="Markdown")

# ===================== EXCHANGE =====================
async def exchange(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🔄 *Exchange Rate*\n\n"
        "💵 1 USD = Rp16.000\n"
        "💶 1 EUR = Rp17.500\n"
        "🪙 1 USDT = Rp16.100\n"
        "₿ 1 BTC = Rp1.600.000.000\n"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ===================== HISTORY =====================
async def cekhis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    get_or_create_user(user.id, user.username or "", user.full_name)
    history = get_history(user.id, 10)

    if not history:
        await update.message.reply_text("📋 Belum ada riwayat transaksi.")
        return

    text = "📋 *Riwayat Transaksi (10 terakhir)*\n\n"
    for tx in history:
        tx_type, amount, desc, created_at = tx
        emoji = "📥" if amount > 0 else "📤"
        sign = "+" if amount > 0 else ""
        text += f"{emoji} {sign}Rp{amount:,.0f}\n"
        text += f"   📝 {desc}\n"
        text += f"   🕐 {created_at}\n\n"

    await update.message.reply_text(text, parse_mode="Markdown")

# ===================== ADS =====================
async def ads(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📢 *Ads Post & Earn* 🎁\n\n"
        "Dapatkan saldo gratis dengan cara:\n\n"
        "1️⃣ Share bot ini ke teman-teman kamu\n"
        "2️⃣ Setiap teman yang join = *Rp1.000* untuk kamu\n"
        "3️⃣ Tidak ada batas referral!\n\n"
        f"🔗 Link referral kamu:\n"
        f"`https://t.me/NamaBotKamu?start={update.effective_user.id}`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ===================== HELP =====================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "❓ *Bantuan*\n\n"
        "📥 *Deposit* — Tambah saldo\n"
        "📤 *Withdraw* — Tarik saldo\n"
        "💰 *Balance* — Cek saldo kamu\n"
        "🔄 *Exchange* — Lihat kurs mata uang\n"
        "📋 */cekhis* — Riwayat transaksi\n"
        "📊 *Statistik* — Statistik bot\n\n"
        "📩 Hubungi admin: @Swp_rank"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ===================== S&K =====================
async def sk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "📋 *Syarat & Ketentuan*\n\n"
        "1. Pengguna wajib menjaga keamanan akun masing-masing\n"
        "2. Dilarang melakukan transaksi yang melanggar hukum\n"
        "3. Saldo yang sudah di-withdraw tidak dapat dikembalikan\n"
        "4. Bot berhak membekukan akun yang mencurigakan\n"
        "5. Layanan dapat berubah sewaktu-waktu tanpa pemberitahuan\n\n"
        "Dengan menggunakan bot ini, kamu setuju dengan semua syarat di atas."
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ===================== STATISTIK =====================
async def statistik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_users = get_total_users()
    total_tx = get_total_transactions()

    text = (
        "📊 *Statistik Bot*\n\n"
        f"👥 Total pengguna: *{total_users}*\n"
        f"💸 Total transaksi: *{total_tx}*"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ===================== MAIN =====================
def main():
    init_db()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cekhis", cekhis))
    app.add_handler(CommandHandler("balance", balance))

    app.add_handler(MessageHandler(filters.Regex("^💰 Balance$"), balance))
    app.add_handler(MessageHandler(filters.Regex("^📥 Deposit$"), deposit_start))
    app.add_handler(MessageHandler(filters.Regex("^📤 Withdraw$"), withdraw_start))
    app.add_handler(MessageHandler(filters.Regex("^🔄 Exchange$"), exchange))
    app.add_handler(MessageHandler(filters.Regex("^📢 Ads Post & Earn 🎁$"), ads))
    app.add_handler(MessageHandler(filters.Regex("^❓ Help$"), help_cmd))
    app.add_handler(MessageHandler(filters.Regex("^📋 S&K$"), sk))
    app.add_handler(MessageHandler(filters.Regex("^📊 Statistik$"), statistik))

    app.add_handler(CallbackQueryHandler(deposit_callback, pattern="^deposit_"))
    app.add_handler(CallbackQueryHandler(withdraw_callback, pattern="^withdraw_"))
    app.add_handler(CallbackQueryHandler(
        lambda u, c: u.callback_query.edit_message_text("❌ Dibatalkan."),
        pattern="^cancel$"
    ))

    logger.info("Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
