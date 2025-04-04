from fuzzywuzzy import fuzz

def match_text_with_list(extracted_text, word_list, threshold=70):
    for word in word_list:
        score = fuzz.ratio(extracted_text, word)
        if score >= threshold:
            return True  # Return True as soon as we find a match
    return False  # Return False if no matches meet the threshold


