import fasttext

model = fasttext.load_model("/home/nan/projects/assignment4-data/models/lid.176.bin")
    
def identify_language(text: str) -> tuple[str, float]:
    text = text.replace("\n", " ")
   
    label,score = model.predict(text)

    return (label[0].removeprefix("__label__"), float(score[0]))
#help(model.predict)