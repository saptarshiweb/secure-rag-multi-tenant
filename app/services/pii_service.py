from transformers import pipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PIIScrubber:
    def __init__(self):
        logger.info("Loading NER model for PII Scrubbing...")
        # Using a standard BERT-NER model. 
        # aggregation_strategy="simple" groups sub-word tokens into whole words.
        self.nlp = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
        logger.info("NER model loaded.")

    def scrub(self, text: str) -> str:
        """
        Detects PII entities (Person, Organization, Location) and replaces them with placeholders.
        Example: "John works at Google" -> "<PER> works at <ORG>"
        """
        if not text:
            return ""

        results = self.nlp(text)
        
        # Sort results by start index in descending order to replace without messing up indices
        results.sort(key=lambda x: x['start'], reverse=True)
        
        # Convert to list of characters for mutable replacement
        scrubbed_text_list = list(text)
        
        for entity in results:
            # We focus on PER (Person), ORG (Organization), LOC (Location)
            if entity['entity_group'] in ['PER', 'ORG', 'LOC']:
                start = entity['start']
                end = entity['end']
                replacement = f"<{entity['entity_group']}>"
                
                # Replace the slice
                scrubbed_text_list[start:end] = replacement
                
        return "".join(scrubbed_text_list)
