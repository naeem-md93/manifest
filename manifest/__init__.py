import dotenv
import logging

ENV_PATH: str = dotenv.find_dotenv()

print(f"ENV LOADED: {dotenv.load_dotenv(ENV_PATH)} | {ENV_PATH}")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)