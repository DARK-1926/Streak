import os
import tempfile
from typing import List, Tuple
import pickle
# Note: These imports require scikit-learn to be installed
# Install with: pip install scikit-learn
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
except ImportError:
    print("Warning: scikit-learn is not installed. Please install it with 'pip install scikit-learn'")
    TfidfVectorizer = None
    LogisticRegression = None
    Pipeline = None
try:
    import joblib
except ImportError:
    print("Warning: joblib is not installed. Please install it with 'pip install joblib'")
    joblib = None
def load_training_data() -> Tuple[List[str], List[int]]:
    """
    Load and return the training data as a tuple of (texts, labels).
    This is a placeholder function. In a real scenario, this would load data from a dataset.
    """
    if TfidfVectorizer is None or LogisticRegression is None:
        print("Warning: scikit-learn is not installed. Please install it with 'pip install scikit-learn'")
        # Return dummy data when scikit-learn is not available
        texts = [
            "This is an example of AI generated text.",
            "Another AI generated text sample here.",
            "AI can generate very convincing text.",
            "Yet another AI generated text for training.",
            "Final AI generated text in the dataset.",
            "This is a human written text.",
            "Humans write with more varied styles.",
            "Human written content often has more nuance.",
            "A human wrote this text, not an AI.",
            "Last human written text in the dataset."
        ]
        labels = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]  # 1 for AI, 0 for human
        return texts, labels
    # Example data: 5 AI-generated texts and 5 human-generated texts
    texts = [
        "This is an example of AI generated text.",
        "Another AI generated text sample here.",
        "AI can generate very convincing text.",
        "Yet another AI generated text for training.",
        "Final AI generated text in the dataset.",
        "This is a human written text.",
        "Humans write with more varied styles.",
        "Human written content often has more nuance.",
        "A human wrote this text, not an AI.",
        "Last human written text in the dataset."
    ]
    labels = [1, 1, 1, 1, 1, 0, 0, 0, 0, 0]  # 1 for AI, 0 for human
    return texts, labels


def train_model(training_data: Tuple[List[str], List[int]]) -> Pipeline:
    """
    Train an NLP model using the provided training data.

    :param training_data: A tuple containing the texts and their corresponding labels.
    :return: A trained Pipeline object.
    """
    if TfidfVectorizer is None or LogisticRegression is None or Pipeline is None or train_test_split is None:
        # Return a dummy pipeline when scikit-learn is not available
        class DummyPipeline:
            def predict(self, texts):
                return [0] * len(texts)
        return DummyPipeline()
    
    
    try:
        texts, labels = training_data
        X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.2, random_state=42)

        # Create a pipeline that vectorizes the text and then applies a logistic regression model
        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer()),
            ('clf', LogisticRegression(solver='liblinear'))
        ])
        
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        if classification_report:
            print(classification_report(y_test, predictions))

        # Save the model to a temporary file
        if joblib:
            fd, path = tempfile.mkstemp(suffix='.pkl')
            try:
                joblib.dump(pipeline, path)
            finally:
                os.close(fd)  # Close the file descriptor
                os.unlink(path)  # Remove the temporary file
        return pipeline

    except Exception as e:
        print(f"An error occurred during model training: {e}")
        raise
        # Save the model to a temporary file
        if joblib:
            fd, path = tempfile.mkstemp(suffix='.pkl')
            try:
                joblib.dump(pipeline, path)
            finally:
                os.close(fd)  # Close the file descriptor
                os.unlink(path)  # Remove the temporary file
    return pipeline

def predict(text: str, model: Pipeline) -> bool:
    """
    Predict whether the given text is AI-generated.

    :param text: The text to be classified.
    :param model: The trained model used for prediction.
    :return: True if the text is predicted to be AI-generated, False otherwise.
    """
    try:
        prediction = model.predict([text])
        return bool(prediction[0])
    except Exception as e:
        print(f"An error occurred during prediction: {e}")
        return False

# Example usage
if __name__ == "__main__":
    training_data = load_training_data()
    model = train_model(training_data)
    sample_text = "This is a sample text to check if it's AI-generated."
    result = predict(sample_text, model)
    print(f"The text is {'AI-generated' if result else 'human-written'}.")
