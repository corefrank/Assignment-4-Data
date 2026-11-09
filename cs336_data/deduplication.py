from pathlib import Path
from collections import Counter


def exact_line_deduplication(
    input_files: list,
    output_directory
) -> None:

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    # 第一次遍历：统计所有文件中每行出现的次数
    line_counts = Counter()

    for file_path in input_files:
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            for line in f:
                line_counts[line.rstrip("\r\n")] += 1

    # 第二次遍历：删除所有重复行
    for file_path in input_files:
        file_path = Path(file_path)
        output_path = output_directory / file_path.name

        with open(file_path, "r", encoding="utf-8", newline="") as f_in:
            with open(output_path, "w", encoding="utf-8", newline="") as f_out:

                for line in f_in:
                    if line_counts[line.rstrip("\r\n")] == 1:
                        f_out.write(line)


import re
import shutil
import mmh3

from pathlib import Path
from collections import defaultdict


def minhash_deduplication(
    input_files,
    num_hashes,
    num_bands,
    ngrams,
    jaccard_threshold,
    output_directory,
):
    if num_hashes <= 0 or num_bands <= 0 or ngrams <= 0:
        raise ValueError("Parameters must be positive")

    if num_hashes % num_bands != 0:
        raise ValueError("num_hashes must be divisible by num_bands")

    if not 0 <= jaccard_threshold <= 1:
        raise ValueError("jaccard_threshold must be between 0 and 1")

    rows = num_hashes // num_bands

    input_files = sorted(
        [Path(p) for p in input_files],
        key=str
    )

    output_directory = Path(output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    # 将每篇文档转换成 N-gram 集合
    shingle_sets = []

    for path in input_files:
        text = path.read_text(encoding="utf-8")

        words = re.findall(r"\w+", text.lower())
        # 构造 N-gram
        if not words:
            shingles = set()
        elif len(words) < ngrams:
            shingles = {tuple(words)}
        else: 
            shingles = {tuple(words[i:i + ngrams]) for i in range(len(words) - ngrams + 1)}  #使用 tuple，因为列表不能直接放进 set，而元组在其元素均可哈希时可以。

        shingle_sets.append(shingles)

    # 计算每篇文档的 MinHash Signature
    signatures = []
   
    max_hash = (1 << 64) - 1

    for shingles in shingle_sets:

        if not shingles:
            signatures.append([max_hash] * num_hashes)
            continue
 
        signature = []

        for seed in range(num_hashes):

            min_hash = min(
                mmh3.hash64(
                    "\x1f".join(shingle),
                    seed=seed,
                    signed=False
                )[0]
                for shingle in shingles
            )

            signature.append(min_hash)

        signatures.append(signature)

    # 4. LSH 分桶，生成候选文档对
    buckets = defaultdict(list)
    candidate_pairs = set()

    for doc_id, signature in enumerate(signatures):

        for band in range(num_bands):

            start = band * rows
            end = start + rows

            band_signature = tuple(signature[start:end])

            key = (band, band_signature)

            for other_doc_id in buckets[key]:
                candidate_pairs.add((other_doc_id, doc_id))

            buckets[key].append(doc_id)

    # 5. Union-Find：建立重复文档组
    parent = list(range(len(input_files)))

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a, b):
        root_a = find(a)
        root_b = find(b)

        if root_a == root_b:
            return

        # 始终保留编号较小的文档作为组代表
        if root_a > root_b:
            root_a, root_b = root_b, root_a

        parent[root_b] = root_a

    # 6. 使用真实 Jaccard 验证 LSH 候选对
    for a, b in sorted(candidate_pairs):

        set_a = shingle_sets[a]
        set_b = shingle_sets[b]

        intersection = len(set_a & set_b)
        union_size = len(set_a | set_b)

        if union_size == 0:
            similarity = 1.0
        else:
            similarity = intersection / union_size

        if similarity >= jaccard_threshold:
            union(a, b)

    # 7. 每个重复文档组只保留一个文件
    for doc_id, path in enumerate(input_files):

        if find(doc_id) == doc_id:

            output_path = output_directory / path.name

            shutil.copyfile(path, output_path)