"""Ports: issue_prediction (metacognition) + discourse_discovery (agency)."""


def test_issue_engine_exhaustion_and_anomaly():
    from omni_coworker.metacognition.issue_prediction import (
        IssuePredictionEngine, MetricType)

    eng = IssuePredictionEngine(window_size=50)
    for v in [0.5, 0.55, 0.6, 0.65, 0.7, 0.75]:
        eng.update_metric(MetricType.MEMORY_USAGE, v)
    preds = eng.predict_issues()
    assert isinstance(preds, list)
    summary = eng.get_metrics_summary()
    assert MetricType.MEMORY_USAGE.value in summary


def test_issue_update_from_bundle():
    from omni_coworker.metacognition.issue_prediction import (
        IssuePredictionEngine, MetricType, update_from_bundle)

    eng = IssuePredictionEngine()
    n = update_from_bundle(eng, {"vram_ratio": 0.87,
                                 "thermal": {"cpu": 0.55}})
    assert n == 2
    summary = eng.get_metrics_summary()
    assert MetricType.MEMORY_USAGE.value in summary
    n = update_from_bundle(eng, {})
    assert n == 0


def test_discourse_analyzer_classification():
    from omni_coworker.agency.discourse_discovery import (
        LacanianDiscourseAnalyzer, LacanianDiscourse)

    an = LacanianDiscourseAnalyzer()
    r = an.analyze_text("Obey my command now. I order you to proceed.")
    assert r is not None
    assert r.dominant_discourse in set(LacanianDiscourse)


def test_discourse_analyst_vs_master():
    from omni_coworker.agency.discourse_discovery import (
        LacanianDiscourseAnalyzer)

    an = LacanianDiscourseAnalyzer()
    master = an.analyze_text(
        "Do it now. That's an order. I command you. Obey.")
    listener = an.analyze_text(
        "Tell me more about what you feel. I'm listening.")
    assert master.dominant_discourse != listener.dominant_discourse or \
        master.scores != listener.scores
