import functools
import pytest
import numpy as np

from noticias_phb.classifier.classifier import NewsClassifier


@functools.cache
def text_from_fixtures(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.readlines()


class TestClassifier:

    @pytest.mark.parametrize(
        ("file_path", "allowed_percentage","expected_result"),
        (
            ("./fixtures/duplicated_news.txt",1, True),
            ("./fixtures/not_duplicated_news.txt",1,False),
            ("./fixtures/almost_equal.txt",1, False),
            ("./fixtures/same_subject.txt",0.4, True)
        )
    )
    def test_news_similarity(self,file_path, expected_result,allowed_percentage):
        texts_news = text_from_fixtures(file_path)
        assert expected_result == (allowed_percentage <= NewsClassifier.news_content_similarity(texts_news[0], texts_news[1]))
