"""Tests for ASR Engine"""
import pytest
from app.core.asr_engine import ASREngine
from app.core.text_parser import TextParser

def test_text_parser_sentence_segmentation():
    """Test text parser sentence segmentation"""
    parser = TextParser()
    
    text = "这是第一句。这是第二句！这是第三句？"
    sentences = parser.segment_sentences(text)
    
    assert len(sentences) == 3
    assert sentences[0]["text"] == "这是第一句"
    assert sentences[1]["text"] == "这是第二句"
    assert sentences[2]["text"] == "这是第三句"

def test_text_parser_character_extraction():
    """Test character extraction"""
    parser = TextParser()
    
    text = "你好"
    characters = parser.extract_characters(text)
    
    assert len(characters) == 2
    assert characters[0]["char"] == "你"
    assert characters[1]["char"] == "好"
    assert not characters[0]["is_punctuation"]

def test_text_parser_punctuation_detection():
    """Test punctuation detection"""
    parser = TextParser()
    
    assert parser._is_punctuation("。")
    assert parser._is_punctuation("！")
    assert parser._is_punctuation("？")
    assert not parser._is_punctuation("a")
