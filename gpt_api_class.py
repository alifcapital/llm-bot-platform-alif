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

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain import hub


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
    def __init__(self, model="gpt-4o-mini", temperature=0.0):
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local("RAG/front", embeddings, allow_dangerous_deserialization=True)

        prompt = hub.pull("rlm/rag-prompt")
        prompt.messages[0].prompt.template = """You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
        If you don't know the answer, just say that you don't know. 
        The answer should be in the sources, do not abbreviate the answers and it is important that the context is conveyed in clear words. 
        If the answer is in both sources, give priority to the source ‘Javob’If the answer in the source ‘Javob’ contains a link to the image, please display the link in your answer. \nQuestion: {question} \nContext: {context} \nAnswer"""

        llm = ChatOpenAI(temperature=temperature, model_name="gpt-4o-mini")
        self.rag_chain = (
            {"context": vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10}) | self.__format_docs, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )


    def __format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)


    def execute_query(self, query):
        with get_openai_callback() as cb:
            answer = self.rag_chain.invoke(query)
        logger.info(f"Query cost {cb.total_cost}")
        return answer