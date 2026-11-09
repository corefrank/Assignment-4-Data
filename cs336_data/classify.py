import fasttext
from typing import Any
from cs336_data.quality import gopher_quality_filter

nsfw_model = fasttext.load_model(
    "/home/nan/projects/assignment4-data/local-shared-data/classifiers/dolma_fasttext_nsfw_jigsaw_model.bin"
)

toxic_model = fasttext.load_model(
    "/home/nan/projects/assignment4-data/local-shared-data/classifiers/dolma_fasttext_hatespeech_jigsaw_model.bin"
)

def classify_nsfw(text: str) -> tuple[Any, float]:
    text = text.replace("\n", " ")
   
    label, score = nsfw_model.predict(text)
    return (label[0].removeprefix("__label__"), float(score[0]))



def classify_toxic_speech(text: str) -> tuple[Any, float]:
    
    text = text.replace("\n", " ")
   
    label, score = toxic_model.predict(text)
    return (label[0].removeprefix("__label__"), float(score[0]))

def classify_quality(text: str) -> tuple[str, float]:
    """
    一个简单的规则基线：
    通过文本长度和 Gopher 质量规则估计文档质量。
    """

    words = text.split()

    # 长篇且通过 Gopher 规则的文本，归为 wiki 类
    if len(words) >= 500 and gopher_quality_filter(text):
        return "wiki", 0.80

    # 其他文本暂时归为 cc 类
    return "cc", 0.60