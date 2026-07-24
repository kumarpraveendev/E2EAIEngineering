from api.agents.retrieval_generation import rag_pipeline

from qdrant_client import QdrantClient
from langsmith import Client
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from openai import AsyncOpenAI
from ragas.llms import LangchainLLMWrapper,llm_factory
from ragas.embeddings import OpenAIEmbeddings

from ragas.metrics.collections import Faithfulness,AnswerRelevancy

ls_client=Client()
qdrant_client = QdrantClient(url="http://localhost:6333")
openai_client=AsyncOpenAI()

ragas_llm = llm_factory("gpt-4.1-mini",client=openai_client,max_tokens=4000)

ragas_embeddings = OpenAIEmbeddings(client= openai_client,model="text-embedding-3-small")

def context_precision_id_based(run, example):
    retrieved_context_ids={str(id) for id in run.outputs["retrieved_context_ids"]}
    reference_context_ids={str(id) for id in run.outputs["reference_context_ids"]}

    score = len(retrieved_context_ids & reference_context_ids) / len(retrieved_context_ids) if retrieved_context_ids else 0.0

    return score


def context_recall_id_based(run, example):

    retrieved_context_ids={str(id) for id in run.outputs["retrieved_context_ids"]}
    reference_context_ids={str(id) for id in run.outputs["reference_context_ids"]}

    score = len(retrieved_context_ids & reference_context_ids) / len(reference_context_ids) if reference_context_ids

    return score


def ragas_faithfulness(run, example):

    scorer = Faithfulness(llm=ragas_llm)
    result =scorer.score(
            user_input=run.outputs["question"],
            response=run.outputs["answer"],
            retrieved_contexts=run.outputs["retrieved_context"]
        )
    return result.value


def ragas_relevancy(run, example):
     
    scorer = AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embeddings)

    result = scorer.score(
        user_input=run.outputs["question"],
        response=run.outputs["answer"]
    )

    return result.value

print ("Evaluating Plain Retriever")
results = ls_client.evaluate(
        lambda x: rag_pipeline(x["question"], qdrant_client,top_k=10,hybrid=False,rerank=False),
        data="rag-evaluation-dataset-extended",
        evaluators=[
            context_precision_id_based,
            context_recall_id_based,
            ragas_faithfulness,
            ragas_relevancy,
        ],
        experiment_prefix="plain"
    )
print ("Evaluating Hybrid Retriever")

results = ls_client.evaluate(
        lambda x: rag_pipeline(x["question"], qdrant_client,top_k=10,hybrid=True,rerank=False),
        data="rag-evaluation-dataset-extended",
        evaluators=[
            context_precision_id_based,
            context_recall_id_based,
            ragas_faithfulness,
            ragas_relevancy,
        ],
        experiment_prefix="Hybrid"
    )

print ("Evaluating Hybrid reRetriever  with Reranking")

results = ls_client.evaluate(
        lambda x: rag_pipeline(x["question"], qdrant_client,top_k=10,hybrid=True,rerank=True),
        data="rag-evaluation-dataset-extended",
        evaluators=[
            context_precision_id_based,
            context_recall_id_based,
            ragas_faithfulness,
            ragas_relevancy,
        ],
        experiment_prefix="Hybrid"
    )