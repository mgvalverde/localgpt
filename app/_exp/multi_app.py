# when we import hydralit, we automatically get all of Streamlit
import streamlit as st
import logging
from pathlib import Path
import hydra
import hydralit as hy
from omegaconf import DictConfig, OmegaConf
# from localgpt.app.chat import app as chat_app
from hydra import compose, initialize
from omegaconf import OmegaConf
from hydra.utils import to_absolute_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: take those to a config file
openai_model_options = ["gpt-3.5-turbo", "gpt-4"]
agent_tools = ["llm-math"]
db_path = "~/.localgpt/chat_history.db"
model_temperature = 0
play_streaming = True
db_history_table_name = "message_store"
title_default_len = 12

app = hy.HydraApp(title="Local GPT")

# with initialize(version_base=None, config_path=to_absolute_path(str(Path.home()/".localgpt/config/")), job_name="local-gpt"):
#     cfg = compose(config_name="config")

cfg = hydra.main(config_path=str(Path.home() / ".localgpt/config/config.yaml"))(lambda x: x)()


@app.addapp(is_home=True, title="Chat", icon="💬")
def app_chat() -> None:
    hy.info("Hello from Home! 💬")
    hy.info(OmegaConf.to_yaml(cfg))


@app.addapp(title="History", icon="📖")
def app_history():
    hy.info("History 📖")


@app.addapp(title="Config", icon="⚙️")
def app_config():
    hy.info("Hello from ⚙")


if __name__ == "__main__":
    app.run()
