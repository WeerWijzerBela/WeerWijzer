import logging
from logtail import LogtailHandler

# Configureer logfiles
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Voeg LogtailHandler toe
handler = LogtailHandler(source_token="26NkjQezsymTKrzueVAB9aV8")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
logging.getLogger().addHandler(handler)