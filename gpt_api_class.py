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
from typing import List
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
import numpy as np
import logging


from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain import hub

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class HR_RAG:
    def __init__(self, model="gpt-4o-mini", temperature=0.0, alpha=0.5):
        self.embeddings = OpenAIEmbeddings()
        self.vectorstore = FAISS.load_local("RAG/HR", self.embeddings, allow_dangerous_deserialization=True)
        self.alpha = alpha  # 0 = только BM25, 1 = только reranker

        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.llm = ChatOpenAI(model=model, temperature=temperature)

        prompt = PromptTemplate(
            template="""
Ты — внутренний эксперт по кадровым и нормативным документам компании.

На основе предоставленного описания инцидента и контекста из документов, выполни следующие действия:

1. Найди в контексте положения, которые прямо или косвенно относятся к описанному инциденту.

2. Для каждого выявленного нарушения укажи:
- Название документа;
- Конкретный пункт или раздел;
- Точный текст нарушенного положения;
- Объяснение;
- Тип нарушения (ИБ, конфиденциальность, этика и т.д.);
- Оценку серьёзности: низкая / средняя / высокая / критическая.

Если ничего не подходит — напиши "Нарушения не найдены".

Контекст:
{context}

Описание инцидента:
{question}

Ответ:
""",
            input_variables=["context", "question"]
        )

        self.rag_chain = (
            {
                "context": self._get_context,
                "question": RunnablePassthrough()
            }
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def _get_context(self, query: str) -> str:
        vector_results = self.vectorstore.similarity_search(query, k=25)

        tokenized = [doc.page_content.lower().split() for doc in vector_results]
        bm25 = BM25Okapi(tokenized)
        bm25_scores = bm25.get_scores(query.lower().split())

        rerank_inputs = [[query, doc.page_content] for doc in vector_results]
        reranker_scores = self.reranker.predict(rerank_inputs)

        hybrid_scores = self.alpha * np.array(reranker_scores) + (1 - self.alpha) * np.array(bm25_scores)
        sorted_docs = [doc for _, doc in sorted(zip(hybrid_scores, vector_results), key=lambda x: x[0], reverse=True)]

        top_docs = sorted_docs[:10]
        logger.info(f"Отобрано {len(top_docs)} документов по гибридному скору")

        return self._format_docs(top_docs)

    def _format_docs(self, docs: List[Document]) -> str:
        chunks = []
        for doc in docs:
            source = doc.metadata.get("source", "Неизвестный документ")
            content = doc.page_content.strip()
            chunks.append(f"Документ: {source}\n{content}")
        return "\n\n".join(chunks)


    def ask(self, query):
        answer = self.rag_chain.invoke(query)
        return answer


if __name__ == "__main__":
    rag = HR_RAG()
    while True:
        q = input("\nОпиши нарушение (или 'выход'): ")
        if q.lower() in ["выход", "exit", "quit"]:
            break
        print("\nНайденные нарушения:\n", rag.ask(q))