import os
import tiktoken

from tqdm import tqdm
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.callbacks import get_openai_callback

class GPT_API():

    def __init__(self, model="gpt-4o-mini", temperature=0.3):
        self.openai_llm = ChatOpenAI(model=model, temperature=temperature)

        self.tokenizer = tiktoken.get_encoding("cl100k_base") # tokenize для gpt 3.5
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