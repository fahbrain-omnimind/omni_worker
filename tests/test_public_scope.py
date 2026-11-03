"""public_scope — domestic→public reclassification with provenance trail."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]
                     / "scripts" / "quality_triage"))
import public_scope  # noqa: E402


def test_domestic_accepted_flips_to_public_risk():
    t = public_scope.reclassify("S8707", "accepted_domestic")
    assert t.flips is True
    assert t.public_verdict == "future_public_risk"
    assert t.practice and t.reason


def test_sink_rules_become_real_vulnerability():
    for rule in ("S8706", "S6096", "S8702", "S6350"):
        t = public_scope.reclassify(rule, "accepted_domestic")
        assert t.public_verdict == "real_vulnerability"
        assert t.flips is True


def test_false_positive_stays_false_positive():
    t = public_scope.reclassify("S6466", "false_positive")
    assert t.public_verdict == "false_positive"
    assert t.flips is False  # mesmo veredito → sem flip


def test_unknown_rule_no_flip():
    t = public_scope.reclassify("S9999", "review_needed")
    assert t.public_verdict == "review_needed"
    assert t.flips is False


def test_apply_to_prior_keeps_trail():
    prior = {"verdict": "accepted_domestic", "confidence": 1.0,
             "suppressible": True, "rationale": "x", "total": 100}
    out = public_scope.apply_to_prior("S2083", prior)
    assert out["public_verdict"] == "future_public_risk"
    assert out["domestic_verdict"] == "accepted_domestic"
    assert out["flips"] is True
    assert out["confidence"] == 1.0  # prior preservado