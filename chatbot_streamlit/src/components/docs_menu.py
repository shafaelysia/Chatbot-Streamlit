import os
import streamlit as st
import pandas as pd
from streamlit_pdf_viewer import pdf_viewer
from tools.rag import get_all_vectors, delete_all_vectors, create_vectors, upload_pdf, delete_pdf

def docs_menu():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "../../assets/pdfs")

    if os.path.exists(path):
        dir_list = os.listdir(path)
        docs_col1, docs_col2 = st.columns([0.3, 0.7])

        if dir_list:
            dir_data_list = []
            for i, dir in enumerate(dir_list, start=1):
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
                    selection_mode="single-row"
                )

                uploaded_pdf = st.file_uploader("Upload PDF", ["pdf"])
                if st.button("Submit PDF", type="primary"):
                    upload_pdf(uploaded_pdf)
                    st.cache_data.clear()
                    st.rerun()

            with docs_col2:
                st.subheader("PDF Preview")
                if docs_event.selection and len(docs_event.selection['rows']):
                    selected_row = docs_event.selection['rows'][0]
                    filename = docs_df.iloc[selected_row]['File Name']
                    if st.button("Delete PDF", type="primary"):
                        delete_pdf(filename)
                        st.cache_data.clear()
                        st.rerun()
                    with st.container(border=True):
                        pdf_preview(filename, path)

        else:
            st.write("No documents found.")
    else:
        st.write(f"Directory does not exist: {path}")

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

            vec_col1, vec_col2 = st.columns([0.15, 0.85])
            with vec_col1:
                if st.button("Create Vectors",):
                    create_vectors()
                    st.cache_data.clear()
                    st.rerun()
            with vec_col2:
                if st.button("Delete All Vectors", type="primary"):
                    delete_all_vectors()
                    st.cache_data.clear()
                    st.rerun()
        else:
            st.write("No vectors found.")


def pdf_preview(filename, path):
    file_path = os.path.join(path, filename)
    with open(file_path, "rb") as f:
        binary_data = f.read()
        pdf_viewer(input=binary_data)