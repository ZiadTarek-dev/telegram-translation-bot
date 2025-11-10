from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import json
import os

# File to store data
DATA_FILE = "translations.json"

# Load existing data if available
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "users": {},        # user_id : fixed number (1-10)
        "translations": {}  # number : translated text
    }

# Function to save data to file
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# /start command: welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send your translation directly. "
        "If this is your first time, I will ask for your number (1-10)."
    )

# /compile command: send all translations in one long message
async def compile_translations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    compiled = []
    for i in range(1, 11):
        part = data["translations"].get(str(i))
        if part:
            compiled.append(f"Part {i}:\n{part}")
        else:
            compiled.append(f"Part {i}:\n(No translation yet)")
    final_text = "\n\n".join(compiled)
    await update.message.reply_text(final_text)

# /clear command: clear all saved translations
async def clear_translations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data["translations"] = {}
    save_data()
    await update.message.reply_text("✅ All translations have been cleared.")

# Handle messages: save translation and confirm
async def handle_translation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text.strip()

    # Ask for number if first time
    if user_id not in data["users"]:
        if text.isdigit() and 1 <= int(text) <= 10:
            data["users"][user_id] = int(text)
            save_data()
            await update.message.reply_text(f"✅ Your number {text} is registered. Now send your translation.")
        else:
            await update.message.reply_text("Please send your number (1-10) first.")
        return

    # Get fixed number for user
    user_number = data["users"][user_id]

    # Save translation and confirm
    data["translations"][str(user_number)] = text
    save_data()
    await update.message.reply_text(f"✅ Your translation has been saved, Number {user_number}!")

# Setup bot application
app = ApplicationBuilder().token("8269289595:AAHHtyqvHHzxlHSRS_p4UxDQ07MwY_VvUi8").build()

# Add command and message handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("compile", compile_translations))
app.add_handler(CommandHandler("clear", clear_translations))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_translation))

print("Bot is running...")
app.run_polling()
