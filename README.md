# LocalGPT

Streamlit interface to access via API OpenAI models.
Subscription model: pay-as-you-go

## Features
 * Creates a SQLite database to store your chat history.
 * Allows chat of several interactions
 * Access to several OpenAI models

## How to
1. Create OpenAI API key

2. Install the components:
```bash
poetry install
```
3. Edit `template.env` to `.env`, and add the API key

4. Run the streamlit app:
```bash
streamlit run app/chat_app.py
```


## Create an alias in Linux 

Add the following chunk to `~/.bash_alias` or `~/.bashrc` 

```bash
# localgpt

localgpt() {  
    local PREV_DIR=$PWD
    cd <PATH/TO/REPO>/localgpt &&\
    source launchapp.sh &&\
    cd $PREV_DIR
}

alias lgpt='localgpt'

```



