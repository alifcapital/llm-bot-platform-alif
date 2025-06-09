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
from models import RAGConfig


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
        """
        Invokes the language model with the provided text using the template.
        
        This method takes the input text, formats it using the predefined template,
        and sends it to the OpenAI LLM. It tracks the cost of the API call and
        returns both the response and the cost information.
        
        Args:
            text (str): The input text to be processed by the language model.
            
        Returns:
            tuple: A tuple containing:
                - gpt_response (str): The text response from the language model.
                - total_cost (float): The cost of the API call in USD.
        """
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
    def __init__(self, bot_id, model="gpt-4o-mini", temperature=0.0):
        # Get RAG configuration from database
        rag_config = RAGConfig.query.filter_by(bot_id=bot_id).first()
        if not rag_config:
            raise ValueError(f"No RAG configuration found for bot_id {bot_id}")
        
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.load_local(
            rag_config.vectorstore_path, 
            embeddings, 
            allow_dangerous_deserialization=True
        )

        prompt = hub.pull("rlm/rag-prompt")
        prompt.messages[0].prompt.template = rag_config.prompt_template

        llm = ChatOpenAI(
            temperature=rag_config.temperature or temperature, 
            model_name=rag_config.model_name or model
        )
        
        self.rag_chain = (
            {
                "context": vectorstore.as_retriever(
                    search_type="similarity", 
                    search_kwargs={"k": 10}
                ) | self.__format_docs, 
                "question": RunnablePassthrough()
            }
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