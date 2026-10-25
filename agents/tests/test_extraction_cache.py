from agents.services.extraction_cache import ExtractionCache


def test_cache_returns_none_for_missing_entry(tmp_path):
    cache = ExtractionCache(
        cache_dir=str(tmp_path),
    )

    result = cache.get(
        namespace="cv_test",
        content="Python, SQL",
    )

    assert result is None


def test_cache_stores_and_retrieves_result(tmp_path):
    cache = ExtractionCache(
        cache_dir=str(tmp_path),
    )

    expected = {
        "skills": [
            {
                "skill": "Python",
                "source": "cv",
            }
        ]
    }

    cache.set(
        namespace="cv_test",
        content="Python, SQL",
        result=expected,
    )

    actual = cache.get(
        namespace="cv_test",
        content="Python, SQL",
    )

    assert actual == expected


def test_cache_separates_namespaces(tmp_path):
    cache = ExtractionCache(
        cache_dir=str(tmp_path),
    )

    cache.set(
        namespace="cv_test",
        content="Python",
        result={"source": "cv"},
    )

    cache.set(
        namespace="job_test",
        content="Python",
        result={"source": "job"},
    )

    cv_result = cache.get(
        namespace="cv_test",
        content="Python",
    )

    job_result = cache.get(
        namespace="job_test",
        content="Python",
    )

    assert cv_result == {"source": "cv"}
    assert job_result == {"source": "job"}


def test_cache_separates_different_inputs(tmp_path):
    cache = ExtractionCache(
        cache_dir=str(tmp_path),
    )

    cache.set(
        namespace="cv_test",
        content="Python",
        result={"skill": "Python"},
    )

    cache.set(
        namespace="cv_test",
        content="SQL",
        result={"skill": "SQL"},
    )

    assert cache.get(
        namespace="cv_test",
        content="Python",
    ) == {"skill": "Python"}

    assert cache.get(
        namespace="cv_test",
        content="SQL",
    ) == {"skill": "SQL"}


def test_cache_persists_between_instances(tmp_path):
    first_cache = ExtractionCache(
        cache_dir=str(tmp_path),
    )

    first_cache.set(
        namespace="cv_test",
        content="Python",
        result={"skill": "Python"},
    )

    second_cache = ExtractionCache(
        cache_dir=str(tmp_path),
    )

    result = second_cache.get(
        namespace="cv_test",
        content="Python",
    )

    assert result == {"skill": "Python"}
