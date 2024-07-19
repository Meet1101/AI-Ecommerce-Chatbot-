# importing libraries
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain

import pandas as pd

class QA():
    def load_dataset(file_path):
        dataset = pd.read_csv(file_path)
        return dataset

    def convert_csv_to_document(dataset):
        document = ''
        for index, row in dataset.iterrows():
            row_values = row.values.tolist()
            row_text = ' '.join(str(value) for value in row_values)
            document += row_text + '\n'
        return document

    file_path = './adidas_usa.csv' 
    dataset = load_dataset(file_path)

    document = convert_csv_to_document(dataset)

    def split_docs(documents, chunk_size=200, chunk_overlap=20):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_text(documents)
        return docs

    docs = split_docs(document)

    embeddings = OpenAIEmbeddings(openai_api_key="ENTER_YOUR_API_KEY")

    from langchain.vectorstores import Chroma
    db = Chroma.from_texts(docs, embeddings)
    retriever = db.as_retriever(search_type="similarity", search_kwargs={"k":2})


    import os
    os.environ["OPENAI_API_KEY"] = "ENTER_YOUR_API_KEY"

    from langchain.chat_models import ChatOpenAI
    model_name = "gpt-3.5-turbo"
    llm = ChatOpenAI()

    from langchain.chains.question_answering import load_qa_chain
    chain = load_qa_chain(llm, chain_type="stuff",verbose=True)

    from langchain.prompts import PromptTemplate # for custom prompt specification
    from langchain.text_splitter import RecursiveCharacterTextSplitter # splitter for chunks
    from langchain.chains import RetrievalQA # qa and retriever chain
    from langchain.memory import ConversationBufferMemory # for model's memory on past conversations

    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)