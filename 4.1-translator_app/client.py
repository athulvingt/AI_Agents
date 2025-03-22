from langserve import RemoteRunnable

remote_chain = RemoteRunnable("http://localhost:8000/chain/")
translated_text = remote_chain.invoke({"text": "I love programming in Python!"})
print(translated_text)