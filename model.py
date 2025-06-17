from transformers import AutoModelForSequenceClassification, AutoTokenizer

best_ckpt = './results\\distilBERT\\checkpoint-3612'
model = AutoModelForSequenceClassification.from_pretrained(best_ckpt)

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")

def tokenize_function(sentence): 
    return tokenizer(sentence, padding='max_length', truncation=True, max_length=256, return_tensors="pt")