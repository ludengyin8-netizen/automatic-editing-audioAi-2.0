"""Text parsing and sentence segmentation"""
from typing import List, Dict, Any
from loguru import logger
import re

class TextParser:
    """Parse Chinese text and segment into sentences"""
    
    SENTENCE_TERMINATORS = r'[。！？；：\n]'
    
    def __init__(self):
        logger.info("TextParser initialized")
    
    def segment_sentences(self, text: str) -> List[Dict[str, str]]:
        """
        Segment text into sentences
        
        Args:
            text: Input text
        
        Returns:
            List of sentences with indices
        """
        try:
            sentences = re.split(self.SENTENCE_TERMINATORS, text)
            
            result = []
            for idx, sentence in enumerate(sentences):
                sentence = sentence.strip()
                if sentence:
                    result.append({
                        "id": idx,
                        "text": sentence,
                        "length": len(sentence),
                    })
            
            logger.info(f"Text segmented into {len(result)} sentences")
            return result
        
        except Exception as e:
            logger.error(f"Sentence segmentation failed: {str(e)}")
            raise
    
    def align_words_to_sentences(
        self,
        words: List[Dict[str, Any]],
        sentences: List[Dict[str, str]],
    ) -> List[Dict[str, Any]]:
        """
        Align word-level data to sentences
        
        Args:
            words: Word timeline from ASR
            sentences: Segmented sentences
        
        Returns:
            List of sentences with word-level data
        """
        try:
            full_text = "".join([w["word"] for w in words])
            
            result = []
            current_pos = 0
            
            for sentence in sentences:
                sent_text = sentence["text"]
                start_pos = full_text.find(sent_text, current_pos)
                
                if start_pos == -1:
                    logger.warning(f"Could not find sentence: {sent_text}")
                    continue
                
                end_pos = start_pos + len(sent_text)
                
                sentence_words = []
                char_pos = 0
                for word in words:
                    word_start = full_text.find(word["word"], char_pos)
                    if start_pos <= word_start < end_pos:
                        sentence_words.append(word)
                        char_pos = word_start + len(word["word"])
                
                if sentence_words:
                    result.append({
                        "id": sentence["id"],
                        "text": sent_text,
                        "start": sentence_words[0]["start"],
                        "end": sentence_words[-1]["end"],
                        "words": sentence_words,
                        "word_count": len(sentence_words),
                    })
                
                current_pos = end_pos
            
            logger.info(f"Aligned {len(result)} sentences with word data")
            return result
        
        except Exception as e:
            logger.error(f"Word-to-sentence alignment failed: {str(e)}")
            raise
    
    def extract_characters(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract individual characters from text
        
        Args:
            text: Input text
        
        Returns:
            List of characters
        """
        try:
            characters = []
            for idx, char in enumerate(text):
                characters.append({
                    "id": idx,
                    "char": char,
                    "is_punctuation": self._is_punctuation(char),
                    "is_space": char.isspace(),
                })
            
            return characters
        
        except Exception as e:
            logger.error(f"Character extraction failed: {str(e)}")
            raise
    
    @staticmethod
    def _is_punctuation(char: str) -> bool:
        """Check if character is punctuation"""
        punctuation = r'[。，！？；：、「」『』（）《》【】·…—·、，。；：？！]'
        return bool(re.match(punctuation, char))
