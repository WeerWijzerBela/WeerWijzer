import logging
from datetime import datetime

# Configureer logfiles
logging.basicConfig(filename=f"logfiles/{datetime.today().strftime('%Y-%m-%d')}.log", level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)