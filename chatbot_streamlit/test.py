import streamlit as st

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
from langchain_huggingface import ChatHuggingFace
from langchain_huggingface import HuggingFacePipeline

llm = HuggingFacePipeline.from_model_id(
    model_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    pipeline_kwargs=dict(
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
    ),
)
messages = [
    SystemMessage(content="You're a helpful assistant"),
    HumanMessage(
        content="What happens when an unstoppable force meets an immovable object?"
    ),
]

chat_model = ChatHuggingFace(llm=llm)
res = chat_model.invoke(messages)
print(res.content)

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
chain = LLMChain(llm=model, prompt=prompt_template, memory=memory)

# from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_core.messages.human import HumanMessage
# from langchain_core.messages.ai import AIMessage
# # from langchain_openai import ChatOpenAI

# chat_message_history = MongoDBChatMessageHistory(
#     session_id="2",
#     connection_string="mongodb+srv://teloronta1863:HKASUqNQtMlWDdFh@cluster0.j7dyd6v.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0",
#     database_name="chatbot_db",
#     collection_name="chat_histories",
# )

# chat_message_history.add_user_message("Hello")
# chat_message_history.add_ai_message("Hi")

# print(type(chat_message_history.messages[0]))

# # # Retrieve messages
# messages = chat_message_history.messages

# # Display each message
# for message in messages:
#     if isinstance(message, HumanMessage):
#         with st.chat_message("user"):
#             st.write(message.content)
#     elif isinstance(message, AIMessage):
#         with st.chat_message("assistant"):
#             st.write(message.content)

# prompt = ChatPromptTemplate.from_messages(
#     [
#         ("system", "You are a helpful assistant."),
#         MessagesPlaceholder(variable_name="history"),
#         ("human", "{question}"),
#     ]
# )
# chain = prompt

# chain_with_history = RunnableWithMessageHistory(
#     chain,
#     lambda session_id: MongoDBChatMessageHistory(
#         session_id=session_id,
#         connection_string="mongodb://mongo_user:password123@mongo:27017",
#         database_name="my_db",
#         collection_name="chat_histories",
#     ),
#     input_messages_key="question",
#     history_messages_key="history",
# )