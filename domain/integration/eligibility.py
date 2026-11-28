"""Adapt graph eligibility to records held in the ordered course index."""


def eligible_course_records(graph, index, passed_codes):
    """Return eligible (code, record) pairs, propagating invalid or missing data.

    This read-only adapter does not validate global index/graph synchronization.
    Returned record objects remain owned by the caller/index.
    """
    return tuple((code, index.get(code)) for code in graph.eligible_courses(passed_codes))
