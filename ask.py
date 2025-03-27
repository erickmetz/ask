import random
import os
from typing import Dict, List, Tuple

class QuestionDeck:
    def __init__(self, filename: str):
        self.filename = filename
        self.lines: List[str] = []
        self.max_line: int = 0
        self.empty_deck: bool = False
        self.load_questions()
        self.empty_deck = self.max_line == -1
    def load_questions(self) -> None:
        if os.path.exists(self.filename):
            with open(self.filename, "r") as file:
                self.lines = file.readlines()
                self.max_line = len(self.lines) - 1
        else:
            print(f"Warning: Question file {self.filename} not found")
            self.lines = []
            self.max_line = -1

    def get_question(self) -> str:
        if not self.lines:
            return ""
        line_number = random.randint(0, self.max_line)
        return self.lines[line_number].strip()
    
    def is_empty(self) -> bool:
        return self.empty_deck

# Global question decks
question_decks: Dict[str, QuestionDeck] = {
    "master": QuestionDeck("questions-master.txt"),
    "channel1": QuestionDeck("questions-channel1.txt"),
    "channel2": QuestionDeck("questions-channel2.txt")
}

def init_questions() -> Tuple[List[str], int]:
    """Initialize the master question deck for backward compatibility"""
    master_deck = question_decks["master"]
    return master_deck.lines, master_deck.max_line

def get_question(lines: List[str], max_line: int, channel: str = None) -> str:
    """
    Get a random question, optionally from a specific channel.
    If channel is specified and exists, there's a 50% chance to get a question from that channel.
    Otherwise, returns a question from the master deck.
    """
    if channel and channel in question_decks:
        channel_deck = question_decks[channel]
        if channel_deck.lines and random.random() < 0.5:
            return channel_deck.get_question()
    
    # Fall back to master deck
    return question_decks["master"].get_question()
