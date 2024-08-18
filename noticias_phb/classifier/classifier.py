from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class NewsClassifier:

    @classmethod
    def news_content_similarity(cls,text1: str, text2: str) -> float:
        vectorizer = CountVectorizer()
        vectors = vectorizer.fit_transform([text1, text2])
        dense_vectors = vectors.toarray()
        similarity = cosine_similarity(dense_vectors[0:1], dense_vectors[1:2])[0][0]
        return similarity
