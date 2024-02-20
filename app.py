import streamlit as st
from langchain_community.llms import OpenAI
from PyPDF2 import PdfReader
from PIL import Image
import openai
import os
from openai import OpenAI
# api_key="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"
client = os.environ.get("OPENAI_API_KEY")
# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )

# print(completion.choices[0].message)
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
# from langchain.llms import OpenAI
# from langchain.callbacks import get_openai_callback
from langchain_community.callbacks import get_openai_callback
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document

st.set_page_config(page_title="Insightify ", page_icon=":robot:")

openai.api_key = st.secrets["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"]

page_bg = f"""
<style>
[data-testid="stSidebar"] {{
background-color:#EFEFE8;

}}

[data-testid="stToolbar"] {{
background-color:#FCFCFC;

}}
</style>
"""
st.markdown(page_bg,unsafe_allow_html=True)

# Sidebar contents
with st.sidebar:

    image = Image.open('Sumquiry.png')
    st.image(image)
    st.markdown("<h3 style='text-align: left'> Intelligent PDF Summarizer and Inquiry Companion </h3>", unsafe_allow_html= True)
    st.markdown("""
            <br><p style='text-align: left;'>With Sumquiry, you can quickly obtain concise and accurate summaries of lengthy documents, saving valuable time. \
            But that's not all - you can ask detailed questions about the content and receive insightful responses, \
            transforming your research experience into an interactive and efficient journey. Say goodbye to information overload \
            and hello to a seamless exploration of knowledge with Sumquiry as your trusted companion.</p> <br><br>
    """, unsafe_allow_html=True)
    
    st.markdown("<p> Made by <a href='https://omaresguerra.github.io'>Omar Esguerra</a> </p>", unsafe_allow_html=True)

# Clear input text
def clear_text():
    st.session_state["input"] = ""

st.header("Sumquiry")
# upload file
pdf = st.file_uploader("Upload your PDF", type="pdf")

# extract the text
if pdf is not None:
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    
    # split into chunks
    text_splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
    )

    chunks = text_splitter.split_text(text)
      
    # create docs
    docs = [Document(page_content=t) for t in chunks[:3]]
    llm = OpenAI(temperature=0, openai_api_key=st.secrets["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"])

    # show summarize doc
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summarized_docs = chain.run(docs)
    st.write("Summary")
    st.write(summarized_docs)

    # create embeddings
    embeddings = OpenAIEmbeddings(openai_api_key=st.secrets["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"])
    knowledge_base = FAISS.from_texts(chunks, embeddings)

    # show user input
    user_question = st.text_input("Ask a question about your PDF", key="input")

    # show button for clear question
    st.button("Clear Text", on_click=clear_text)
    if user_question:
        docs = knowledge_base.similarity_search(user_question)
        chain = load_qa_chain(llm, chain_type="stuff")
        with get_openai_callback() as cb:
            response = chain.run(input_documents=docs, question=user_question)
            print(cb)
            st.write(response)
