"""
Task 4: Analysis text
Version: 1.0
Author: Butakova Kristina
Date: 16.04.2025
"""
def analyze_text():
    text = """
    So she was considering in her own mind, as well as she could, for the hot day made her feel very sleepy and stupid, 
    whether the pleasure of making a daisy-chain would be worth the trouble of getting up and picking the daisies, 
    when suddenly a White Rabbit with pink eyes ran close by her.
    """
    
    text = text.lower().replace(',', ' ').replace('.', ' ').replace('-', ' ')
    
    words = text.split()
    
    vowels = "aeiouy"
    count_vowel_ending = sum(1 for word in words if word[-1] in vowels)
    
    word_lengths = [len(word) for word in words]
    average_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
    average_length = round(average_length) 
    
    words_of_avg_length = [word for word in words if len(word) == average_length]
    

    words_every_fifth = [words[i] for i in range(4, len(words), 5)] 
    
    return count_vowel_ending, average_length, words_of_avg_length, words_every_fifth