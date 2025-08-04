from ragas import SingleTurnSample, evaluate, EvaluationDataset
from ragas.metrics import BleuScore, answer_relevancy, faithfulness, context_recall
import json
from test.retrieve_and_generate_test import build_chatbot  # senin build_chatbot fonksiyonun

def load_testset(path="test/test_data.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def build_samples(test_items):
    retrieve_fn, generate_fn = build_chatbot()
    samples = []

    for item in test_items:
        question = item["soru"]
        reference = item["cevap"]

        state = retrieve_fn({"question": question})
        contexts_docs = state.get("context", [])
        gen_out = generate_fn(state)
        model_answer = gen_out.get("answer", "")

        contexts_texts = []
        for doc in contexts_docs:
            try:
                content = doc.page_content
            except AttributeError:
                content = str(doc)
            contexts_texts.append(content)

        sample = SingleTurnSample(
            user_input=question,
            response=model_answer,
            reference=reference,
            contexts=contexts_texts,
            retrieved_contexts=contexts_texts,
        )
        samples.append(sample)
    return samples

def evaluate_all(samples, show_n=5):
    metrics = [BleuScore(), answer_relevancy, faithfulness, context_recall]

    eval_dataset = EvaluationDataset(samples)
    aggregated = evaluate(dataset=eval_dataset, metrics=metrics)
    print("=== Aggregated evaluation ===")
    print(aggregated)

if __name__ == "__main__":
    test_items = load_testset()
    samples = build_samples(test_items)
    evaluate_all(samples)
