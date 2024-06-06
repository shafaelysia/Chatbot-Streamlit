import streamlit as st
import huggingface_hub
from documents_service import retrieve_documents

def authorize_hf():
    HUGGINGFACEHUB_API_TOKEN = st.secrets.hf.HUGGINGFACEHUB_API_TOKEN
    huggingface_hub.login(HUGGINGFACEHUB_API_TOKEN)

def load_llm_model(model_name):
    pass

def generate_prompt_template(query, embedding_model):
    docs = retrieve_documents(query, embedding_model)
    messages = [
        {
            "role": "system",
            "content": "Kamu adalah chatbot yang bertugas untuk memberikan informasi terkait SMP Santo Leo III. Dengan menggunakan informasi yang terdapat dalam konteks, berikan jawaban yang komprehensif untuk pertanyaan tersebut. Tanggapi hanya pertanyaan yang diajukan, jawaban harus ringkas dan relevan dengan pertanyaan. Jika konteks tidak relevan dengan pertanyaan, abaikan konteks yang diberikan."
        },
        {
            "role": "question",
            "content": f"Konteks: {docs[0].page_content} ---- Sekarang, inilah pertanyaan yang perlu kamu jawab. Pertanyaan: {query}"
        }
    ]
    return messages

def model_inference(messages, model, tokenizer):
    authorize_hf()

    device = "cuda"
    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    generated_ids = model.generate(
        input_ids=model_inputs.input_ids,
        # attention_mask=model_inputs.attention_mask,
        max_new_tokens=512,
        # eos_token_id=tokenizer.eos_token_id,
        top_k=10,
        top_p=0.8,
        temperature=0.8,
        do_sample=True
    )

    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response

def generate_response(query, model, tokenizer, embedding_model):
    prompt = generate_prompt_template(query, embedding_model)
    response = model_inference(prompt, model, tokenizer)
    return response