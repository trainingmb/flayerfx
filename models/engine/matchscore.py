#!/usr/bin/python3
"""
Contains the Match Score function
"""

# Threshold score for filtering search results
SCORETHRESHOLD = 70

def match_score(search_string, product_name):
    # Normalize the strings to lower case
    search_string = search_string.lower()
    product_name = product_name.lower()
    # Split the strings into words
    search_words = set(search_string.split())
    product_words = set(product_name.split())
    # Count the common words
    common_words = search_words.intersection(product_words)
    common_count = len(common_words)
    # Calculate the score based on common words and the lengths of the strings
    score = (common_count / max(len(search_words), 1)) * 100  # Score out of 100
    # Bonus: check for substring match
    if search_string in product_name:
        score += 10  # Add bonus points for exact substring match
    return score