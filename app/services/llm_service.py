from transformers import pipeline
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        logger.info("Loading LLM for RAG Generation...")
        # flan-t5-small is lightweight and good for simple QA
        self.generator = pipeline(
            "text2text-generation", 
            model="google/flan-t5-small", 
            max_length=512
        )
        logger.info("LLM loaded.")

    def generate_answer(self, context: str, question: str) -> str:
        """
        Generates an answer based on the provided context.
        """
        if not context:
            return "I don't have enough information to answer that."

        # Prompt Engineering for FLAN-T5
        prompt = f"question: {question} context: {context}"
        
        try:
            output = self.generator(prompt)
            return output[0]['generated_text']
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return "Error generating answer."
