# School FAQ Chatbot System

## Project Description
This project is a chatbot system designed to handle frequently asked questions (FAQs) for a school (SMP Santo Leo III). It uses LangChain for natural language processing, Streamlit for the web interface, MongoDB for data storage and retrieval, and retrieval-augmented generation (RAG) techniques to improve the quality of responses. The chatbot is powered by open-source large language models (LLMs) from Hugging Face.

## Web App
The chatbot system is hosted on Streamlit Cloud and is accessible via the following link:
[Chatbot App](https://smpsantoleo3-chat.streamlit.app/)

## Features
- Real-time interaction with users to answer school-related FAQs.
- Retrieval-augmented generation to provide accurate and contextually relevant answers.
- Easy-to-use web interface built with Streamlit.
- Integration with Hugging Face LLMs for advanced language understanding.
- MongoDB database for efficient data storage and retrieval.

## Technologies Used
- **LangChain**: Framework for building applications with LLMs.
- **Streamlit**: Open-source app framework for creating interactive web applications.
- **Hugging Face Transformers**: Pre-trained LLMs used to power the chatbot.
  - [firqaaa/indo-sentence-bert-base](https://huggingface.co/firqaaa/indo-sentence-bert-base)
  - [meta-llama/Meta-Llama-3-8B-Instruct](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct)
  - [mistralai/Mistral-7B-Instruct-v0.3](https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3)
  - [HuggingFaceH4/zephyr-7b-beta](https://huggingface.co/HuggingFaceH4/zephyr-7b-beta)
- **MongoDB**: NoSQL database used to store and retrieve FAQ data.
- **Retrieval-Augmented Generation (RAG)**: Method used to retrieve relevant information from a knowledge base before generating responses.
