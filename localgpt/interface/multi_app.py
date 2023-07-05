# when we import hydralit, we automatically get all of Streamlit
import streamlit as st
import hydralit as hy

app = hy.HydraApp(title="Private GPT")


@app.addapp(is_home=True, title="Chat", icon="💬")
def my_home():
    hy.info("Hello from Home!")
    st.info("Hello from Home!")


@app.addapp(title="History", icon="📖")
def app3():
    hy.info("History 📖")


@app.addapp(title="Config", icon="⚙️")
def app2():
    hy.info("Hello from ⚙")


# Run the whole lot, we get navbar, state management and app isolation, all with this tiny amount of work.
app.run()
