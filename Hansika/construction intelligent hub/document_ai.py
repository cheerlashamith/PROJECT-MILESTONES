import streamlit as st
import pdfplumber
import docx
import requests


def ask_ai(document_text):

    prompt = f"""
You are a construction document analyst.

Analyze the following document and provide:

1. Document Type
2. Owner Details
3. Land Details
4. Area Details
5. Important Information
6. Risks or Missing Information
7. Construction Suitability

Document:
{document_text}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:0.5b",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


def show():

    st.title("📄 AI Document Analyzer")

    st.write(
        "Upload Patta, Agreement, Contract, Invoice, BOQ or other construction documents for AI analysis."
    )

    uploaded_file = st.file_uploader(
        "Upload Document",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file is not None:

        text = ""

        try:

            if uploaded_file.name.endswith(".pdf"):

                with pdfplumber.open(uploaded_file) as pdf:

                    for page in pdf.pages:

                        extracted = page.extract_text()

                        if extracted:
                            text += extracted + "\n"

            elif uploaded_file.name.endswith(".docx"):

                doc = docx.Document(uploaded_file)

                for para in doc.paragraphs:
                    text += para.text + "\n"

            elif uploaded_file.name.endswith(".txt"):

                text = uploaded_file.read().decode("utf-8")

            st.success("✅ Document uploaded successfully")

            st.subheader("📃 Extracted Content")

            st.text_area(
                "Document Text",
                text,
                height=250
            )

            if st.button(
                "🔍 Analyze Document",
                use_container_width=True
            ):

                with st.spinner(
                    "AI is analyzing the document..."
                ):

                    result = ask_ai(text)

                st.subheader("🤖 AI Analysis")

                st.success(result)

        except Exception as e:

            st.error(
                f"Error while processing document: {e}"
            )