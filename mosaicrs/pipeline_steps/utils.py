import string
from nltk.tokenize import word_tokenize
import unicodedata
import contractions

def translate_language_code(language_code:str):
    language_dict = {
        "eng":"english",
        "deu":"german",
        "fra":"french",
        "ita":"italian",
        #TODO: Extend dict (https://stackoverflow.com/questions/54573853/nltk-available-languages-for-stopwords , https://www.nltk.org/api/nltk.stem.SnowballStemmer.html?highlight=stopwords)
    }
    if language_code in language_dict:
        return language_dict[language_code]
    
    return ""


def get_blacklist_for_filtering():
    return [
    "Home", "About", "Services", "Products", "Features", "Pricing", "Contact", "Blog",
    "FAQ", "Help", "Support", "Careers", "Testimonials", "Portfolio", "Gallery",
    "Login", "Register", "Sign Up", "Profile", "Dashboard", "Settings", "Logout",
    "News", "Events", "Shop", "Store", "Resources", "Community", "Forum",
    "Documentation", "Tutorials", "Guides", "Case Studies", "Partners", "Team",
    "Press", "Investors", "API", "Developers", "Downloads", "Legal",
    "Privacy Policy", "Terms of Service", "Sitemap", "Search", "Subscribe"
    ]


def process_data_punctuation_removal(data):
    if data is None:
        return ''

    expanded_data = contractions.fix(data)
    normalized_data = unicodedata.normalize("NFKD", expanded_data)
    normalized_data = "".join(c for c in normalized_data if unicodedata.category(c) != 'Mn')
    tokenized_words = word_tokenize(normalized_data) 
    tokenized_words = [word.translate(str.maketrans('','',string.punctuation)) for word in tokenized_words]

    cleaned_text = " ".join([word.strip() for word in tokenized_words if word != ''])
    return cleaned_text 

def process_data_stopword_removal(input, selected_stopwords):
    withouth_stopwords = [word.strip() for word in word_tokenize(input) if word.lower() not in selected_stopwords]
    return " ".join(withouth_stopwords)  

def process_data_stemming(input, stemmer):
    stemmed_words = [stemmer.stem(word).strip() for word in word_tokenize(input)]
    return " ".join(stemmed_words)

def get_lemmatization_code(language_name:str):
    lemmatization_codes = {
        "german": "de_core_news_sm",
        "french": "fr_core_news_sm",
        "italian": "it_core_news_sm"
    }
    if language_name in lemmatization_codes:
        return lemmatization_codes[language_name]
    
    return ""
              


