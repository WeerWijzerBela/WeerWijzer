import logging
from datetime import datetime
from logtail import LogtailHandler

# Configureer logfiles
logging.basicConfig(
    filename=f"logfiles/{datetime.today().strftime('%Y-%m-%d')}.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# Logtail configuratie
handler = LogtailHandler(source_token="26NkjQezsymTKrzueVAB9aV8")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.handlers = []
logger.addHandler(handler)