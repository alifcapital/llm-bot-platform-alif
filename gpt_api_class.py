import os

from tqdm import tqdm
from loguru import logger
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain, RetrievalQA, ConversationalRetrievalChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import TextLoader, UnstructuredExcelLoader, UnstructuredMarkdownLoader
from langchain.vectorstores import DocArrayInMemorySearch, FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferMemory, ConversationBufferMemory
from langchain.indexes import VectorstoreIndexCreator
from langchain.agents.agent_types import AgentType
from langchain_experimental.agents.agent_toolkits.csv.base import create_csv_agent


class GPT_API():

    def __init__(self, model="gpt-4o-mini", temperature=0.3):
        self.openai_llm = ChatOpenAI(model=model, temperature=temperature)

        self.template = """
###Instruction###
Переведи текст на таджикский. В ответе верни только переведенное предложение
###Data###
{text}
"""

    def invoke(self, text):
        # Составляем промт
        valiables = {'text': str(text)}
        prompt = PromptTemplate(template=self.template, input_variables=["text"])

        # Соединяем промт и подключение к LLM
        llm_chain = LLMChain(prompt=prompt, llm=self.openai_llm)

        # Вызваем LLM
        with get_openai_callback() as cb:
            response = llm_chain.invoke(valiables)
            total_cost = cb.total_cost

        gpt_response = response['text']
        return gpt_response, total_cost
    

class RAG():
    def __init__(self, model="gpt-4o-mini", temperature=0.7):
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local("RAG/frontend", embeddings, allow_dangerous_deserialization=True)

        llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini")
        memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
        self.conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            chain_type="stuff",
            retriever=vectorstore.as_retriever(),
            memory=memory
        )

    def execute_query(self, query):
        with get_openai_callback() as cb:
            result = self.conversation_chain({"question": query})
            answer = result["answer"]
        logger.info(f"Query cost {cb.total_cost}")
        return answer