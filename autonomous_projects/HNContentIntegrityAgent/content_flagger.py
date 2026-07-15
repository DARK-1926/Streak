# Ensure scikit-learn is installed before running this script. You can install it using:
# pip install scikit-learn

import os
from typing import List, Dict
try:
    from sklearn.pipeline import Pipeline
except ImportError:
    raise ImportError("scikit-learn is required for flag_ai_generated_content. Install with 'pip install scikit-learn'.")


def flag_ai_generated_content(articles, ai_detection_model):
    """
    Flags AI-generated content in the provided list of articles using the AI detection model.
    The function updates the articles list with a new key `is_ai_generated` set to True or False
    based on the prediction.

    :param articles: A list of dictionaries, each containing the title, URL, and text of an article.

    """
    try:
        from sklearn.pipeline import Pipeline
    except ImportError:
        raise ImportError("scikit-learn is required for flag_ai_generated_content. Install with 'pip install scikit-learn'.")
    try:
        for article in articles:
            # Predict if the article is AI-generated
            text = article.get('text', '')
            if text:
                prediction = ai_detection_model.predict([text])
                article['is_ai_generated'] = bool(prediction[0])
            else:
                article['is_ai_generated'] = False  # No text to analyze, assume not AI-generated
    except Exception as e:
        # Handle any exceptions that occur during the flagging process
        print(f"An error occurred while flagging AI-generated content: {e}")
if __name__ == "__main__":
    from hn_content_fetcher import fetch_hn_articles
    from ai_detection_model import load_training_data, train_model

    # Fetch articles
    articles = fetch_hn_articles()

    # Load and train the AI detection model
    training_data = load_training_data()
    ai_detection_model = train_model(training_data)

    # Flag AI-generated content in the articles
    flag_ai_generated_content(articles, ai_detection_model)

    # Print the results
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Is AI-Generated: {article['is_ai_generated']}")
        print("-" * 50)
    # Save the results to a file for further analysis if needed
    with open("ai_generated_content_report.txt", "w") as report_file:
        for article in articles:
            report_file.write(f"Title: {article['title']}\n")
            report_file.write(f"URL: {article['url']}\n")
            report_file.write(f"Is AI-Generated: {article['is_ai_generated']}\n")
            report_file.write("-" * 50 + "\n")
    from hn_content_fetcher import fetch_hn_articles
    from ai_detection_model import load_training_data, train_model

    # Fetch articles
    articles = fetch_hn_articles()

    # Load and train the AI detection model
    training_data = load_training_data()
    ai_detection_model = train_model(training_data)

    # Flag AI-generated content in the articles
    flag_ai_generated_content(articles, ai_detection_model)

    # Print the results
    for article in articles:
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Is AI-Generated: {article['is_ai_generated']}")
        print("-" * 50)
    # Save the results to a file for further analysis if needed
    with open("ai_generated_content_report.txt", "w") as report_file:
        for article in articles:
            report_file.write(f"Title: {article['title']}\n")
            report_file.write(f"URL: {article['url']}\n")
            report_file.write(f"Is AI-Generated: {article['is_ai_generated']}\n")
            report_file.write("-" * 50 + "\n")
