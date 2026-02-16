"""
classifier.py — Uses Groq API to classify comments as hate/toxic/sarcasm/safe.
"""

import os
from dotenv import load_dotenv
from groq import Groq
from linkedin_scraper.utils import logger

load_dotenv()


class CommentClassifier:
    """Wrapper for Groq API classification."""

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            logger.warning("GROQ_API_KEY missing. Classification will be disabled.")
            self.client = None
        else:
            try:
                self.client = Groq(api_key=self.api_key)
                logger.info("✅ Groq client initialized.")
            except Exception as e:
                logger.error(f"Failed to initialize Groq client: {e}")
                self.client = None

    def classify(self, text: str) -> str:
        """
        Classifies the given text into one of: 'hate', 'toxic', 'sarcasm', 'safe'.
        Returns 'unknown' if client is not available or error occurs.
        """
        if not self.client or not text:
            return "unknown"

        try:
            # Using specific model requested by user
            completion = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a content moderation AI. "
                            "Classify the following text into exactly one of these labels: "
                            "'hate', 'sarcasm', 'safe'. "
                            "Return ONLY the label, nothing else."
                        )
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.1,
                max_completion_tokens=1024,
                top_p=1,
                stream=False
            )
            label = completion.choices[0].message.content.strip().lower()
            
            # Simple validation to ensure valid label
            valid_labels = {"hate", "sarcasm", "safe"}
            # Clean punctuation just in case
            cleaned_label = label.strip('."').lower()
            
            if cleaned_label in valid_labels:
                return cleaned_label
            
            # If model returned something else, log it but return raw output
            return label
            
        except Exception as e:
            logger.error(f"Classification error for text '{text[:30]}...': {e}")
            return "error"
