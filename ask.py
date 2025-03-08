import random

def init_questions():
    with open("questions-master.txt", "r") as file:
        lines = file.readlines()

    max_line = len(lines)-1
    lines_cache = lines
    return lines, max_line

def get_question(lines, max_line):
    line_number = random.randint(0, max_line)
    return lines[line_number].strip()
