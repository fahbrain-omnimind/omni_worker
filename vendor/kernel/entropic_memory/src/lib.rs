//! Rust port of the hot CPU-bound functions from
//! `src/infrastructure/dream_weaver_entropic_memory.py`.

#![allow(clippy::too_many_arguments)]
#![allow(clippy::useless_conversion)]
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule};

#[inline]
fn clip_inner(value: f64, low: f64, high: f64) -> f64 {
    low.max(high.min(value))
}

#[inline]
fn round6(x: f64) -> f64 {
    (x * 1_000_000.0).round_ties_even() / 1_000_000.0
}

#[pyfunction]
#[pyo3(name = "clip")]
fn py_clip(value: f64, low: f64, high: f64) -> f64 {
    clip_inner(value, low, high)
}

#[pyfunction]
#[pyo3(name = "coerce_float", signature = (value, default=0.0))]
fn py_coerce_float(py: Python<'_>, value: &Bound<'_, PyAny>, default: f64) -> f64 {
    let builtins = match py.import("builtins") {
        Ok(b) => b,
        Err(_) => return default,
    };
    let float_func = match builtins.getattr("float") {
        Ok(f) => f,
        Err(_) => return default,
    };
    let arg: Py<PyAny> = value.clone().unbind();
    match float_func.call1((arg,)) {
        Ok(obj) => obj.extract::<f64>().unwrap_or(default),
        Err(_) => default,
    }
}

#[inline]
fn textual_gate_open(host_pressure: f64) -> bool {
    let threshold = std::env::var("OMNIMIND_ENTROPIC_PRESSURE_MIN")
        .ok()
        .and_then(|v| v.trim().parse::<f64>().ok())
        .unwrap_or(0.5);
    host_pressure >= threshold
}

#[pyfunction]
#[pyo3(
    name = "memory_resonance_weight",
    signature = (cosmic_resonance, subject_id, key_insight, host_pressure=0.0)
)]
fn py_memory_resonance_weight(
    cosmic_resonance: i64,
    subject_id: &str,
    key_insight: &str,
    host_pressure: f64,
) -> f64 {
    let mut weight: f64 = 1.0;
    if cosmic_resonance != 0 {
        weight += 0.35;
    }
    let mut text = String::with_capacity(subject_id.len() + key_insight.len() + 1);
    text.push_str(subject_id);
    text.push(' ');
    text.push_str(key_insight);
    let text = text.to_lowercase();
    if textual_gate_open(host_pressure) {
        if text.contains("xer-afex-angst") || text.contains("phase56") || text.contains("federated") {
            weight += 0.15;
        }
        if text.contains("orbital") || text.contains("quantum") || text.contains("astro") {
            weight += 0.1;
        }
    }
    clip_inner(weight, 0.75, 2.25)
}

#[pyfunction]
#[pyo3(
    name = "lexicum_resonance_weight",
    signature = (lexeme, step_type, payload_json, host_pressure=0.0)
)]
fn py_lexicum_resonance_weight(
    lexeme: &str,
    step_type: &str,
    payload_json: &str,
    host_pressure: f64,
) -> f64 {
    let mut weight: f64 = 1.0;
    let lexeme_l = lexeme.to_lowercase();
    let step_type_l = step_type.to_lowercase();
    let payload_l = payload_json.to_lowercase();
    if !lexeme_l.is_empty() {
        weight += 0.15;
    }
    if textual_gate_open(host_pressure) {
        if lexeme_l.contains("ogum") || lexeme_l.contains("xer") || lexeme_l.contains("sago") {
            weight += 0.15;
        }
        if step_type_l.contains("whisper") || payload_l.contains("federat") {
            weight += 0.1;
        }
    }
    clip_inner(weight, 0.75, 2.25)
}

#[pyfunction]
#[pyo3(
    name = "effective_t2_hours",
    signature = (base_t2_hours, resonance_weight, access_count, bridge_feedback_gain, orbital_pressure)
)]
fn py_effective_t2_hours(
    base_t2_hours: f64,
    resonance_weight: f64,
    access_count: i64,
    bridge_feedback_gain: f64,
    orbital_pressure: f64,
) -> f64 {
    let access_gain = clip_inner(1.0 + (access_count.min(12) as f64) * 0.08, 1.0, 1.96);
    let pressure_drag = clip_inner(1.0 - (orbital_pressure * 0.45), 0.35, 1.0);
    let effective =
        base_t2_hours * resonance_weight * access_gain * bridge_feedback_gain * pressure_drag;
    clip_inner(effective, 6.0, 24.0 * 30.0)
}

#[pyfunction]
#[pyo3(
    name = "state_from_age",
    signature = (age_hours, effective_t2_hours, resonance_weight, access_count, orbital_pressure=0.0, bridge_feedback_gain=1.0, dominant_affect_token="")
)]
fn py_state_from_age(
    py: Python<'_>,
    age_hours: f64,
    effective_t2_hours: f64,
    resonance_weight: f64,
    access_count: i64,
    orbital_pressure: f64,
    bridge_feedback_gain: f64,
    dominant_affect_token: &str,
) -> PyResult<Py<PyDict>> {
    let decoherence = (-(age_hours.max(0.0) / effective_t2_hours.max(1e-6))).exp();
    let repression_score = clip_inner(1.0 - decoherence, 0.0, 1.0);
    let access_factor = clip_inner(1.0 + (access_count.min(8) as f64) * 0.05, 1.0, 1.4);
    let retention_priority = clip_inner(decoherence * resonance_weight * access_factor, 0.0, 5.0);

    let dict = PyDict::new(py);
    dict.set_item("age_hours", round6(age_hours))?;
    dict.set_item("effective_t2_hours", round6(effective_t2_hours))?;
    dict.set_item("decoherence_factor", round6(decoherence))?;
    dict.set_item("repression_score", round6(repression_score))?;
    dict.set_item("retention_priority", round6(retention_priority))?;
    dict.set_item("orbital_pressure", round6(orbital_pressure))?;
    dict.set_item("bridge_feedback_gain", round6(bridge_feedback_gain))?;
    dict.set_item("dominant_affect_token", dominant_affect_token)?;
    Ok(dict.into())
}

#[pymodule]
fn omnimind_entropic_memory(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(py_clip, m)?)?;
    m.add_function(wrap_pyfunction!(py_coerce_float, m)?)?;
    m.add_function(wrap_pyfunction!(py_memory_resonance_weight, m)?)?;
    m.add_function(wrap_pyfunction!(py_lexicum_resonance_weight, m)?)?;
    m.add_function(wrap_pyfunction!(py_effective_t2_hours, m)?)?;
    m.add_function(wrap_pyfunction!(py_state_from_age, m)?)?;
    m.add(
        "__doc__",
        "Rust-accelerated hot functions for dream_weaver_entropic_memory.",
    )?;
    Ok(())
}
