"""
Módulo de configuração para carregar variáveis de ambiente e configurações do sistema.
"""
import os
from dotenv import load_dotenv
from loguru import logger

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do Telegram
TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID")

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Configurações de apostas
DEFAULT_STAKE = float(os.getenv("DEFAULT_STAKE", 10))
MAX_STAKE = float(os.getenv("MAX_STAKE", 100))
MIN_STAKE = float(os.getenv("MIN_STAKE", 5))

# Configurações do navegador
BROWSER_TYPE = os.getenv("BROWSER_TYPE", "chrome")
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

# Configurações da aplicação
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Configuração do logger
logger.remove()
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="1 week",
    level=LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)
logger.add(
    lambda msg: print(msg),
    level=LOG_LEVEL,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

def get_config():
    """
    Retorna todas as configurações como um dicionário.
    """
    return {
        "telegram": {
            "api_id": TELEGRAM_API_ID,
            "api_hash": TELEGRAM_API_HASH,
            "bot_token": TELEGRAM_BOT_TOKEN,
            "group_id": TELEGRAM_GROUP_ID,
        },
        "supabase": {
            "url": SUPABASE_URL,
            "key": SUPABASE_KEY,
        },
        "betting": {
            "default_stake": DEFAULT_STAKE,
            "max_stake": MAX_STAKE,
            "min_stake": MIN_STAKE,
        },
        "browser": {
            "type": BROWSER_TYPE,
            "headless": HEADLESS,
        },
        "app": {
            "debug": DEBUG_MODE,
            "log_level": LOG_LEVEL,
        },
    }
