import os
import json
import streamlit as st
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
from tools.rag import get_all_vectors, delete_all_vectors, create_vectors, create_json_vectors, upload_pdf, delete_pdf, upload_json, delete_json

def docs_menu():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, "../../assets/pdfs")
    json_path = os.path.join(current_dir, "../../assets/json")

    if os.path.exists(pdf_path):
        dir_list = os.listdir(pdf_path)
        docs_col1, docs_col2 = st.columns([0.3, 0.7])

        if dir_list:
            dir_data_list = []
            for i, dir in enumerate(dir_list, start=1):
                if dir.endswith(".pdf"):
                    file = {
                        "No": i,
                        "File Name": dir,
                    }
                    dir_data_list.append(file)

            with docs_col1.container():
                st.subheader("PDFs List")
                docs_df = pd.DataFrame(dir_data_list)

                docs_event = st.dataframe(
                    docs_df,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="pdf"
                )

            with docs_col2:
                st.subheader("PDF Preview")
                if docs_event.selection and len(docs_event.selection['rows']):
                    selected_row = docs_event.selection['rows'][0]
                    filename = docs_df.iloc[selected_row]['File Name']
                    if st.button("Delete PDF", type="primary"):
                        delete_pdf(filename)
                        st.cache_data.clear()
                        st.rerun()
                    with st.container(border=True, height=500):
                        pdf_preview(filename, pdf_path)

        else:
            st.write("No documents found.")

        uploaded_pdf = st.file_uploader("Upload PDF", ["pdf"])
        if st.button("Submit PDF", type="primary"):
            upload_pdf(uploaded_pdf)
            st.cache_data.clear()
            st.rerun()
    else:
        st.write(f"Directory does not exist: {pdf_path}")
    st.divider()

    if os.path.exists(json_path):
        json_list = os.listdir(json_path)
        json_col1, json_col2 = st.columns([0.3, 0.7])

        if json_list:
            json_data_list = []
            for i, dir in enumerate(json_list, start=1):
                if dir.endswith(".json"):
                    file = {
                        "No": i,
                        "File Name": dir,
                    }
                    json_data_list.append(file)

            with json_col1.container():
                st.subheader("JSON List")
                json_df = pd.DataFrame(json_data_list)

                json_event = st.dataframe(
                    json_df,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="json"
                )

            with json_col2:
                st.subheader("JSON Preview")
                if json_event.selection and len(json_event.selection['rows']):
                    selected_row = json_event.selection['rows'][0]
                    filename = json_df.iloc[selected_row]['File Name']
                    if st.button("Delete JSON", type="primary"):
                        delete_json(filename)
                        st.cache_data.clear()
                        st.rerun()
                    with st.container(border=True, height=300):
                        json_file = open_json(filename, json_path)
                        st.json(json_file)

        else:
            st.write("No documents found.")

        uploaded_json = st.file_uploader("Upload JSON", ["json"])
        if st.button("Submit JSON", type="primary"):
            upload_json(uploaded_json)
            st.cache_data.clear()
            st.rerun()
    else:
        st.write(f"Directory does not exist: {json_path}")
    st.divider()


    with st.container():
        st.subheader("Vector stores in DB")
        vectors = get_all_vectors()

        if vectors:
            vectors_data_list = []
            for i, vector in enumerate(vectors, start=1):
                vec = {
                    "No.": i,
                    "Text": vector["text"],
                }
                vectors_data_list.append(vec)

            vectors_df = pd.DataFrame(vectors_data_list)
            st.dataframe(
                vectors_df,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                column_config={
                    "No.": st.column_config.Column(
                        "No.",
                        width="small",
                    ),
                    "Text": st.column_config.Column(
                        "Text",
                        width="large",
                    )
                },
                width=700
            )
        else:
            st.write("No vectors found.")

        vec_col1, vec_col2, vec_col3 = st.columns([0.2, 0.2, 0.6])
        with vec_col1:
            if st.button("Create PDF Vectors"):
                create_vectors()
                st.cache_data.clear()
                st.rerun()
        with vec_col2:
            if st.button("Create JSON Vectors"):
                create_json_vectors()
                st.cache_data.clear()
                st.rerun()
        with vec_col3:
            if st.button("Delete All Vectors", type="primary"):
                delete_all_vectors()
                st.cache_data.clear()
                st.rerun()


def pdf_preview(filename, path):
    file_path = os.path.join(path, filename)
    with open(file_path, "rb") as f:
        binary_data = f.read()
        pdf_viewer(input=binary_data)

def open_json(filename, path):
    file_path = os.path.join(path, filename)
    with open(file_path, "r") as f:
        return json.load(f)