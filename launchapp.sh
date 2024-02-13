#!/bin/bash

source .env
OPENAI_API_KEY=$OPENAI_API_KEY poetry run streamlit run app/chat_app.py --server.fileWatcherType none

