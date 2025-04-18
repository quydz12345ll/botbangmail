import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- BƯỚC 1: CẤU HÌNH BOT ---

# Thay bằng TOKEN bạn lấy từ BotFather
BOT_TOKEN = "7321073275:AAG9uLKsoHIiwhxtmci4Nirob0K-ymhacm8"

# Thay bằng Telegram ID của admin (dùng @userinfobot để lấy)
ADMIN_ID = 7518215176

# Danh sách sản phẩm + file chứa tài khoản tương ứng
PRODUCTS = {
    "gmail": {
        "name": "Gmail Premium",
        "price": "2k",
        "file": "gmail.txt"
    },
    "facebook": {
        "name": "Facebook cổ",
        "price": "80k",
        "file": "facebook.txt"
    }
}

# --- BƯỚC 2: XỬ LÝ LỆNH /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Tạo menu sản phẩm
    buttons = [
        [InlineKeyboardButton(prod["name"], callback_data=key)]
        for key, prod in PRODUCTS.items()
    ]
    await update.message.reply_text("Chào bạn, chọn sản phẩm muốn mua:",
                                    reply_markup=InlineKeyboardMarkup(buttons))

# --- BƯỚC 3: HIỂN THỊ THÔNG TIN SẢN PHẨM ---
async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    product_key = query.data
    product = PRODUCTS.get(product_key)

    if product:
        message = (
            f"Sản phẩm: {product['name']}\n"
            f"Giá: {product['price']}\n\n"
            f"Vui lòng chuyển khoản đến STK:\n"
            f"Ngân hàng: MB Bank\n"
            f"Số tài khoản: 0325839461\n"
            f"Nội dung: {query.from_user.username or query.from_user.id}\n\n"
            f"Sau khi thanh toán, admin xác nhận, bot sẽ gửi tài khoản tự động."
        )
        await query.edit_message_text(message)

# --- BƯỚC 4: ADMIN XÁC NHẬN (SAU NÀY CÓ THỂ NÂNG CẤP THÀNH TỰ ĐỘNG) ---
# Cú pháp: /xacnhan @username gmail
async def xacnhan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Bạn không có quyền dùng lệnh này.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Cú pháp: /xacnhan @username sản_phẩm")
        return

    username = context.args[0]
    product_key = context.args[1]

    product = PRODUCTS.get(product_key)
    if not product:
        await update.message.reply_text("Sản phẩm không tồn tại.")
        return

    acc_file = product["file"]
    if not os.path.exists(acc_file):
        await update.message.reply_text("File acc không tồn tại.")
        return

    with open(acc_file, "r") as f:
        accounts = f.readlines()

    if not accounts:
        await update.message.reply_text("Hết tài khoản!")
        return

    # Lấy acc đầu tiên và xoá khỏi file
    account = accounts[0].strip()
    with open(acc_file, "w") as f:
        f.writelines(accounts[1:])

    # Gửi acc cho người dùng
    try:
        await context.bot.send_message(
            chat_id=username,
            text=(
                f"Bạn đã mua thành công {product['name']}\n"
                f"Tài khoản: `{account}`\n"
                f"Chúc bạn sử dụng vui vẻ!"
            ),
            parse_mode="Markdown"
        )
        await update.message.reply_text(f"Đã gửi acc cho {username}")
    except Exception as e:
        await update.message.reply_text(f"Lỗi khi gửi: {e}")

# --- BƯỚC 5: KHỞI ĐỘNG BOT ---
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(show_product))
    app.add_handler(CommandHandler("xacnhan", xacnhan))

    print("Bot đang chạy...")
    app.run_polling()
