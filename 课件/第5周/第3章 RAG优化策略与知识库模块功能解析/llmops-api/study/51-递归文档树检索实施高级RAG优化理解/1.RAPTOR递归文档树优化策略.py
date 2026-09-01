#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/8/7 11:18
@Author  : thezehui@gmail.com
@File    : 16.RAPTOR递归文档树优化策略.py
"""
from typing import Optional

import dotenv
import numpy as np
import pandas
import pandas as pd
import umap
import weaviate
from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_weaviate import WeaviateVectorStore
from sklearn.mixture import GaussianMixture
from weaviate.auth import AuthApiKey

dotenv.load_dotenv()

# 1.定义随机数种子、文本嵌入模型、大语言模型、向量数据库
RANDOM_SEED = 224
embd = HuggingFaceEmbeddings(
    model_name="thenlper/gte-small",
    cache_folder="./embeddings/",
    encode_kwargs={"normalize_embeddings": True},
)
model = ChatOpenAI(model="gpt-3.5-turbo-16k", temperature=0)
db = WeaviateVectorStore(
    client=weaviate.connect_to_wcs(
        cluster_url="https://mbakeruerziae6psyex7ng.c0.us-west3.gcp.weaviate.cloud",
        auth_credentials=AuthApiKey("ZltPVa9ZSOxUcfafelsggGyyH6tnTYQYJvBx"),
    ),
    index_name="RaptorRAG",
    text_key="text",
    embedding=embd,
)


def global_cluster_embeddings(
        embeddings: np.ndarray, dim: int, n_neighbors: Optional[int] = None, metric: str = "cosine",
) -> np.ndarray:
    """
    使用UMAP对传递嵌入向量进行全局降维

    :param embeddings: 需要降维的嵌入向量
    :param dim: 降低后的维度
    :param n_neighbors: 每个向量需要考虑的邻居数量，如果没有提供默认为嵌入数量的开方
    :param metric: 用于UMAP的距离度量，默认为余弦相似性
    :return: 一个降维到指定维度的numpy嵌入数组
    """
    if n_neighbors is None:
        n_neighbors = int((len(embeddings) - 1) ** 0.5)
    return umap.UMAP(n_neighbors=n_neighbors, n_components=dim, metric=metric).fit_transform(embeddings)


def local_cluster_embeddings(
        embeddings: np.ndarray, dim: int, n_neighbors: int = 10, metric: str = "cosine",
) -> np.ndarray:
    """
    使用UMAP对嵌入进行局部降维处理，通常在全局聚类之后进行。

    :param embeddings: 需要降维的嵌入向量
    :param dim: 降低后的维度
    :param n_neighbors: 每个向量需要考虑的邻居数量
    :param metric: 用于UMAP的距离度量，默认为余弦相似性
    :return: 一个降维到指定维度的numpy嵌入数组
    """
    return umap.UMAP(
        n_neighbors=n_neighbors, n_components=dim, metric=metric,
    ).fit_transform(embeddings)


def get_optimal_clusters(
        embeddings: np.ndarray, max_clusters: int = 50, random_state: int = RANDOM_SEED,
) -> int:
    """
    使用高斯混合模型结合贝叶斯信息准则（BIC）确定最佳的聚类数目。

    :param embeddings: 需要聚类的嵌入向量
    :param max_clusters: 最大聚类数
    :param random_state: 随机数
    :return: 返回最优聚类数
    """
    # 1.获取最大聚类树，最大聚类数不能超过嵌入向量的数量
    max_clusters = min(max_clusters, len(embeddings))
    n_clusters = np.arange(1, max_clusters)

    # 2.逐个设置聚类树并找出最优聚类数
    bics = []
    for n in n_clusters:
        # 3.创建高斯混合模型，并计算聚类结果
        gm = GaussianMixture(n_components=n, random_state=random_state)
        gm.fit(embeddings)
        bics.append(gm.bic(embeddings))

    return n_clusters[np.argmin(bics)]


def gmm_cluster(embeddings: np.ndarray, threshold: float, random_state: int = 0) -> tuple[list, int]:
    """
    使用基于概率阈值的高斯混合模型（GMM）对嵌入进行聚类。

    :param embeddings: 需要聚类的嵌入向量（降维）
    :param threshold: 概率阈值
    :param random_state: 用于可重现的随机性种子
    :return: 包含聚类标签和确定聚类数目的元组
    """
    # 1.获取最优聚类数
    n_clusters = get_optimal_clusters(embeddings)

    # 2.创建高斯混合模型对象并嵌入数据
    gm = GaussianMixture(n_components=n_clusters, random_state=random_state)
    gm.fit(embeddings)

    # 3.预测每个样本属于各个聚类的概率
    probs = gm.predict_proba(embeddings)

    # 4.根据概率阈值确定每个嵌入的聚类标签
    labels = [np.where(prob > threshold)[0] for prob in probs]

    # 5.返回聚类标签和聚类数目
    return labels, n_clusters


def perform_clustering(embeddings: np.ndarray, dim: int, threshold: float) -> list[np.ndarray]:
    """
    对嵌入进行聚类，首先全局降维，然后使用高斯混合模型进行聚类，最后在每个全局聚类中进行局部聚类。

    :param embeddings: 需要执行操作的嵌入向量列表
    :param dim: 指定的降维维度
    :param threshold: 概率阈值
    :return: 包含每个嵌入的聚类ID的列表，每个数组代表一个嵌入的聚类标签。
    """
    # 1.检测传入的嵌入向量，当数据量不足时不进行聚类
    if len(embeddings) <= dim + 1:
        return [np.array([0]) for _ in range(len(embeddings))]

    # 2.调用函数进行全局降维
    reduced_embeddings_global = global_cluster_embeddings(embeddings, dim)

    # 3.对降维后的数据进行全局聚类
    global_clusters, n_global_clusters = gmm_cluster(reduced_embeddings_global, threshold)

    # 4.初始化一个空列表，用于存储所有嵌入的局部聚类标签
    all_local_clusters = [np.array([]) for _ in range(len(embeddings))]
    total_clusters = 0

    # 5.遍历每个全局聚类以执行局部聚类
    for i in range(n_global_clusters):
        # 6.提取属于当前全局聚类的嵌入向量
        global_cluster_embeddings_ = embeddings[
            np.array([i in gc for gc in global_clusters])
        ]

        # 7.如果当前全局聚类中没有嵌入向量则跳过循环
        if len(global_cluster_embeddings_) == 0:
            continue

        # 8.如果当前全局聚类中的嵌入量很少，直接将它们分配到一个聚类中
        if len(global_cluster_embeddings_) <= dim + 1:
            local_clusters = [np.array([0]) for _ in global_cluster_embeddings_]
            n_local_clusters = 1
        else:
            # 9.执行局部降维和聚类
            reduced_embeddings_local = local_cluster_embeddings(global_cluster_embeddings_, dim)
            local_clusters, n_local_clusters = gmm_cluster(reduced_embeddings_local, threshold)

        # 10.分配局部聚类ID，调整已处理的总聚类数目
        for j in range(n_local_clusters):
            local_cluster_embeddings_ = global_cluster_embeddings_[
                np.array([j in lc for lc in local_clusters])
            ]
            indices = np.where(
                (embeddings == local_cluster_embeddings_[:, None]).all(-1)
            )[1]
            for idx in indices:
                all_local_clusters[idx] = np.append(all_local_clusters[idx], j + total_clusters)

        total_clusters += n_local_clusters

    return all_local_clusters


def embed(texts: list[str]) -> np.ndarray:
    """
    将传递的的文本列表转换成嵌入向量列表

    :param texts: 需要转换的文本列表
    :return: 生成的嵌入向量列表并转换成numpy数组
    """
    text_embeddings = embd.embed_documents(texts)
    return np.array(text_embeddings)


def embed_cluster_texts(texts: list[str]) -> pandas.DataFrame:
    """
    对文本列表进行嵌入和聚类,并返回一个包含文本、嵌入和聚类标签的数据框。
    该函数将嵌入生成和聚类结合成一个步骤。

    :param texts: 需要处理的文本列表
    :return: 返回包含文本、嵌入和聚类标签的数据框
    """
    text_embeddings_np = embed(texts)
    cluster_labels = perform_clustering(text_embeddings_np, 10, 0.1)
    df = pd.DataFrame()
    df["text"] = texts
    df["embd"] = list(text_embeddings_np)
    df["cluster"] = cluster_labels
    return df


def fmt_txt(df: pd.DataFrame) -> str:
    """
    将数据框中的文本格式化成单个字符串

    :param df: 需要处理的数据框，内部涵盖text、embd、cluster三个字段
    :return: 返回合并格式化后的字符串
    """
    unique_txt = df["text"].tolist()
    return "--- --- \n --- ---".join(unique_txt)


def embed_cluster_summarize_texts(texts: list[str], level: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    对传入的文本列表进行嵌入、聚类和总结。
    该函数首先问文本生成嵌入，基于相似性对他们进行聚类，扩展聚类分配以便处理，然后总结每个聚类中的内容。

    :param texts: 需要处理的文本列表
    :param level: 一个整数，可以定义处理的深度
    :return: 包含两个数据框的元组
    - 第一个 DataFrame (df_clusters) 包括原始文本、它们的嵌入以及聚类分配。
    - 第二个 DataFrame (df_summary) 包含每个聚类的摘要信息、指定的处理级别以及聚类标识符。
    """
    # 1.嵌入和聚类文本，生成包含text、embd、cluster的数据框
    df_clusters = embed_cluster_texts(texts)

    # 2.定义变量，用于扩展数据框，以便更方便地操作聚类
    expanded_list = []

    # 3.扩展数据框条目，将文档和聚类配对，便于处理
    for index, row in df_clusters.iterrows():
        for cluster in row["cluster"]:
            expanded_list.append(
                {"text": row["text"], "embd": row["embd"], "cluster": cluster}
            )

    # 4.从扩展列表创建一个新的数据框
    expanded_df = pd.DataFrame(expanded_list)

    # 5.获取唯一的聚类标识符以进行处理
    all_clusters = expanded_df["cluster"].unique()

    # 6.创建汇总Prompt、汇总链
    template = """Here is a sub-set of LangChain Expression Language doc. 

    LangChain Expression Language provides a way to compose chain in LangChain.

    Give a detailed summary of the documentation provided.

    Documentation:
    {context}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model | StrOutputParser()

    # 7.格式化每个聚类中的文本以进行总结
    summaries = []
    for i in all_clusters:
        df_cluster = expanded_df[expanded_df["cluster"] == i]
        formatted_txt = fmt_txt(df_cluster)
        summaries.append(chain.invoke({"context": formatted_txt}))

    # 8.创建一个DataFrame来存储总结及其对应的聚类和级别
    df_summary = pd.DataFrame(
        {
            "summaries": summaries,
            "level": [level] * len(summaries),
            "cluster": list(all_clusters),
        }
    )

    return df_clusters, df_summary


def recursive_embed_cluster_summarize(
        texts: list[str], level: int = 1, n_levels: int = 3,
) -> dict[int, tuple[pd.DataFrame, pd.DataFrame]]:
    """
    递归地嵌入、聚类和总结文本，直到达到指定的级别或唯一聚类数变为1，将结果存储在每个级别处。

    :param texts: 要处理的文本列表
    :param level: 当前递归级别（从1开始）
    :param n_levels: 递归地最大深度（默认为3）
    :return: 一个字典，其中键是递归级别，值是包含该级别处聚类DataFrame和总结DataFrame的元组。
    """
    # 1.定义字典用于存储每个级别处的结果
    results = {}

    # 2.对当前级别执行嵌入、聚类和总结
    df_clusters, df_summary = embed_cluster_summarize_texts(texts, level)

    # 3.存储当前级别的结果
    results[level] = (df_clusters, df_summary)

    # 4.确定是否可以继续递归并且有意义
    unique_clusters = df_summary["cluster"].nunique()
    if level < n_levels and unique_clusters > 1:
        # 5.使用总结作为下一级递归的输入文本
        new_texts = df_summary["summaries"].tolist()
        next_level_results = recursive_embed_cluster_summarize(
            new_texts, level + 1, n_levels
        )

        # 6.将下一级的结果合并到当前结果字典中
        results.update(next_level_results)

    return results


# 2.定义文档加载器、文本分割器(中英文场景)
loaders = [
    UnstructuredFileLoader("./流浪地球.txt"),
    UnstructuredFileLoader("./电商产品数据.txt"),
    UnstructuredFileLoader("./项目API文档.md"),
]
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=0,
    separators=["\n\n", "\n", "。|！|？", "\.\s|\!\s|\?\s", "；|;\s", "，|,\s", " ", ""],
    is_separator_regex=True,
)

# 3.循环分割并加载文本
docs = []
for loader in loaders:
    docs.extend(loader.load_and_split(text_splitter))

# 4.构建文档树，最多3层
leaf_texts = [doc.page_content for doc in docs]
results = recursive_embed_cluster_summarize(leaf_texts, level=1, n_levels=3)

# 5.遍历文档树结果，从每个级别提取总结并将它们添加到all_texts中
all_texts = leaf_texts.copy()
for level in sorted(results.keys()):
    summaries = results[level][1]["summaries"].tolist()
    all_texts.extend(summaries)

# 6.将all_texts添加到向量数据库
db.add_texts(all_texts)

# 7.执行相似性检索（折叠树）
retriever = db.as_retriever(search_type="mmr")
search_docs = retriever.invoke("流浪地球中的人类花了多长时间才流浪到新的恒星系？")

print(search_docs)
print(len(search_docs))
