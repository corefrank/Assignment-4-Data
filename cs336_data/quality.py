def gopher_quality_filter(text: str) -> bool:

    words = [
        word for word in text.split()
        if any(char.isalnum() for char in word)
    ] #.isalnum()	检查是否为字母或数字

    num_words = len(words)
    if not 50 <= num_words <= 100000:
        return False

    # 检查平均词长：3 ~ 10
    avg_word_length = sum(len(word) for word in words) / num_words

    if not 3 <= avg_word_length <= 10:
        return False

    # 检查以省略号结尾的行占比：不能超过 30%
    lines = text.splitlines()
#text.splitlines()	按行分割文本
#line.rstrip()	删除行尾空白
#line.endswith("...")	判断行是否以省略号结尾
    if lines:
        ellipsis_count = sum(
            line.rstrip().endswith("...")
            for line in lines
        )

        ellipsis_ratio = ellipsis_count / len(lines)

        if ellipsis_ratio > 0.3:
            return False

    #  检查包含字母的词占比：至少 80%
    alphabetic_count = sum(any(char.isalpha() for char in word) for word in words ) #Python 中的 bool 可以参与整数运算。

    alphabetic_ratio = alphabetic_count / num_words

    if alphabetic_ratio < 0.8:
        return False
    # 所有规则通过
    return True