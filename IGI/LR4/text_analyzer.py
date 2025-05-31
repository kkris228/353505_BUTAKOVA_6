# text_analyzer.py

"""
Lab work #2: Text Analysis
Version 1.0
Author: Your Full Name
Date: 2025-05-14

This module performs analysis of a given text according to specific tasks,
using regular expressions and file operations.
"""

import re
import zipfile
import os


class TextAnalyzer:
    """
    Class to perform text analysis tasks including regex extraction,
    statistics, and archiving results.
    """

    def __init__(self, source_file: str, result_file: str, archive_file: str):
        """
        Initialize with file paths.

        :param source_file: Path to input text file.
        :param result_file: Path to output results file.
        :param archive_file: Path to zip archive file.
        """
        self.source_file = source_file
        self.result_file = result_file
        self.archive_file = archive_file
        self.text = ""

    def read_text(self):
        """Read text from source file."""
        with open(self.source_file, 'r', encoding='utf-8') as f:
            self.text = f.read()

    def count_sentences(self):
        """
        Count total sentences and sentences by type:
        declarative, interrogative, imperative.
        
        Assumes sentences end with '.', '?', or '!' respectively.
        """
        declarative = re.findall(r'[^.!?]+[.]', self.text)
        interrogative = re.findall(r'[^.!?]+[?]', self.text)
        imperative = re.findall(r'[^.!?]+[!]', self.text)
        total = len(declarative) + len(interrogative) + len(imperative)
        return total, len(declarative), len(interrogative), len(imperative)

    def average_sentence_length(self):
        """
        Calculate average sentence length in characters (count only letters and digits).

        :return: average length (float)
        """
        sentences = re.findall(r'[^.!?]+[.!?]', self.text)
        cleaned_sentences = [re.sub(r'[^a-zA-Z0-9\s]', '', s) for s in sentences]
        lengths = [len(s.replace(" ", "")) for s in cleaned_sentences if s.strip()]
        return sum(lengths) / len(lengths) if lengths else 0

    def average_word_length(self):
        """
        Calculate average word length in characters.

        :return: average length (float)
        """
        words = re.findall(r'\b\w+\b', self.text)
        lengths = [len(word) for word in words]
        return sum(lengths) / len(lengths) if lengths else 0

    def count_smileys(self):
        """
        Count smileys defined as:
        - starts with ; or :
        - followed by zero or more -
        - ends with one or more identical brackets from set () []
        """
        pattern = r'[;:]-*[()\[\]]\3*'
        # The above regex won't ensure all brackets identical, so do a more precise check:

        # Alternative approach: find candidates and filter
        candidates = re.findall(r'[;:]-*[()\[\]]+', self.text)
        count = 0
        for c in candidates:
            # Check first char ; or :
            if c[0] not in (';', ':'):
                continue
            # Check if all chars after optional - are identical brackets
            rest = c[1:]
            # remove all '-' in rest
            rest_no_dash = rest.replace('-', '')
            if not rest_no_dash:
                continue
            if all(ch == rest_no_dash[0] for ch in rest_no_dash):
                count += 1
        return count

    def capital_words_with_digits(self):
        """
        Return list of words starting with capital letter and containing digits.
        """
        words = re.findall(r'\b[A-Z][\w]*\d[\w]*\b', self.text)
        return words

    def hex_color_codes(self):
        """
        Return list of valid hex color codes in text (case insensitive).

        Valid examples: #FFFFFF, #00ff00, #FF3421
        Invalid: #fd2 (only 3 hex digits)
        """
        pattern = r'#([0-9a-fA-F]{6})\b'
        codes = re.findall(pattern, self.text)
        return ['#' + code for code in codes]

    def minimal_length_words_count(self):
        """
        Count how many words have minimal length.
        """
        words = re.findall(r'\b\w+\b', self.text)
        if not words:
            return 0
        min_len = min(len(w) for w in words)
        return sum(1 for w in words if len(w) == min_len)

    def words_followed_by_dot(self):
        """
        Return list of words immediately followed by a dot ('.').
        """
        words = re.findall(r'\b(\w+)\.(?!\w)', self.text)
        return words

    def longest_word_ending_r(self):
        """
        Return the longest word that ends with 'r' or 'R'.
        """
        words = re.findall(r'\b\w*r\b', self.text, flags=re.IGNORECASE)
        if not words:
            return ''
        return max(words, key=len)

    def analyze(self):
        """
        Perform all analyses and prepare a results string.
        """
        results = []

        total, dec, ques, imp = self.count_sentences()
        results.append(f"Total sentences: {total}")
        results.append(f"Declarative sentences: {dec}")
        results.append(f"Interrogative sentences: {ques}")
        results.append(f"Imperative sentences: {imp}")

        avg_sent_len = round(self.average_sentence_length())
        results.append(f"Average sentence length (chars, words only): {avg_sent_len:g}")

        avg_word_len = round(self.average_word_length())
        results.append(f"Average word length (chars): {avg_word_len:g}")

        smileys = self.count_smileys()
        results.append(f"Number of smileys: {smileys}")

        cap_words = self.capital_words_with_digits()
        results.append(f"Words starting with capital and containing digits: {', '.join(cap_words) if cap_words else 'None'}")

        hex_codes = self.hex_color_codes()
        results.append(f"Hex color codes found: {', '.join(hex_codes) if hex_codes else 'None'}")

        min_len_words = self.minimal_length_words_count()
        results.append(f"Number of words with minimal length: {min_len_words}")

        words_dot = self.words_followed_by_dot()
        results.append(f"Words followed by a dot: {', '.join(words_dot) if words_dot else 'None'}")

        longest_r = self.longest_word_ending_r()
        results.append(f"Longest word ending with 'r': {longest_r if longest_r else 'None'}")

        return '\n'.join(results)

    def save_results(self, content):
        """Save results string to the results file."""
        with open(self.result_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def archive_results(self):
        """
        Archive the results file into a zip and print info about archive contents.
        """
        with zipfile.ZipFile(self.archive_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(self.result_file, arcname=os.path.basename(self.result_file))

        with zipfile.ZipFile(self.archive_file, 'r') as zipf:
            info = zipf.getinfo(os.path.basename(self.result_file))
            print(f"\nArchive '{self.archive_file}' contents:")
            print(f"File: {info.filename}")
            print(f"Compressed size: {info.compress_size} bytes")
            print(f"Uncompressed size: {info.file_size} bytes")


def create_sample_file(path):
    """
    Create a sample text file to analyze.
    """
    sample_text = """He3llo! This is a sample text to analyze.
How many sentences does it have? Let's check.
Smileys are fun :) ;-----)))) and ;---------[[[[[[[[ too!
Some words like Data123 or Version2 are capitalized and contain digits.
Is #FF3421 a color code? What about #00ff00 or #123abc? No, #fd2 is invalid.
Short words a I be we he it.
Does the word printer or answer appear here? Let's see.
"""
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sample_text)
