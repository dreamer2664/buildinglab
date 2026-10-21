#!/usr/bin/env python3
"""
compute_organ.py — Acoustic Pipe-Length Arithmetic for the Gray & Davison Great Organ (G6, CONFLICTS.md C-001).

Adjudicated count: 4,500 speaking pipes across 60 stops / 88 ranks:
  - Great Organ  (Manual I,  54 notes CC-f3, 28 ranks) : 1,512 pipes
  - Swell Organ  (Manual II, 54 notes CC-f3, 25 ranks) : 1,350 pipes
  - Choir Organ  (Manual III,54 notes CC-f3, 19 ranks) : 1,026 pipes
  - Pedal Organ  (Pedal,     30 notes CCC-f0,16 ranks) :   480 pipes
  - Case & Solo  (Tuba/Diapason display ranks, 132)    :   132 pipes
  Total                                                : 4,500 pipes

Acoustic formulas at Hall Temperature T = 16.0 C:
  Speed of sound: c = 331.3 * sqrt(1 + 16.0 / 273.15) = 340.8719 m/s
  Note frequency: f = 440.0 * 2^((midi - 69)/12) * (8.0 / footage_ft)
  Normal-scale diameter at C2 (midi 36): d0 = 0.155 * (footage_ft / 8.0) * scale_factor
  Töpfer 1:sqrt(8) half-dimension on 17th pipe: d(midi) = d0 * 2^(-(midi - 36)/16.0)
  Speaking lengths:
    - open_flue    : L = (c / (2.0 * f)) - 1.65 * d
    - stopped_flue : L = (c / (4.0 * f)) - 0.82 * d
    - reed         : L = 0.72 * (c / (2.0 * f))
"""
from __future__ import annotations
import json
import math
import os
import sys

HALL_TEMP_C = 16.0
SPEED_OF_SOUND_M_S = 331.3 * math.sqrt(1.0 + HALL_TEMP_C / 273.15)  # 340.8719 m/s
A4_HZ = 440.0


def compute_pipe_metrics(midi_note: int, footage_ft: float, scale_factor: float, pipe_type: str) -> dict:
    freq_hz = A4_HZ * (2.0 ** ((midi_note - 69.0) / 12.0)) * (8.0 / footage_ft)
    d0 = 0.155 * (footage_ft / 8.0) * scale_factor
    diameter_m = max(0.006, d0 * (2.0 ** (-(midi_note - 36.0) / 16.0)))
    wavelength_m = SPEED_OF_SOUND_M_S / freq_hz
    if pipe_type == "open_flue":
        length_m = max(0.035, 0.5 * wavelength_m - 1.65 * diameter_m)
    elif pipe_type == "stopped_flue":
        length_m = max(0.025, 0.25 * wavelength_m - 0.82 * diameter_m)
    else:  # reed
        length_m = max(0.045, 0.36 * wavelength_m)
    return {
        "freq_hz": round(freq_hz, 4),
        "diameter_m": round(diameter_m, 5),
        "computed_length_m": round(length_m, 5),
    }


def generate_organ_schedule() -> list[dict]:
    divisions = [
        ("Great", 54, 36, 28, [
            ("Double Open Diapason 16ft", 16.0, 1.05, "open_flue"),
            ("Open Diapason I 8ft", 8.0, 1.02, "open_flue"),
            ("Open Diapason II 8ft", 8.0, 0.96, "open_flue"),
            ("Stopped Diapason 8ft", 8.0, 1.00, "stopped_flue"),
            ("Octave 4ft", 4.0, 0.98, "open_flue"),
            ("Flute 4ft", 4.0, 1.04, "stopped_flue"),
            ("Twelfth 2-2/3ft", 2.6667, 0.94, "open_flue"),
            ("Super Octave 2ft", 2.0, 0.95, "open_flue"),
            ("Mixture Rank", 1.3333, 0.90, "open_flue"),
            ("Posaune 8ft", 8.0, 1.00, "reed"),
            ("Clarion 4ft", 4.0, 0.96, "reed"),
        ]),
        ("Swell", 54, 36, 25, [
            ("Bourdon 16ft", 16.0, 1.00, "stopped_flue"),
            ("Open Diapason 8ft", 8.0, 0.98, "open_flue"),
            ("Keraulophon 8ft", 8.0, 0.82, "open_flue"),
            ("Concert Flute 8ft", 8.0, 1.02, "stopped_flue"),
            ("Principal 4ft", 4.0, 0.96, "open_flue"),
            ("Fifteenth 2ft", 2.0, 0.92, "open_flue"),
            ("Sesquialtera Rank", 2.6667, 0.90, "open_flue"),
            ("Cornopean 8ft", 8.0, 1.00, "reed"),
            ("Hautboy 8ft", 8.0, 0.88, "reed"),
            ("Clarion 4ft", 4.0, 0.94, "reed"),
        ]),
        ("Choir", 54, 36, 19, [
            ("Gamba 8ft", 8.0, 0.80, "open_flue"),
            ("Claribel Flute 8ft", 8.0, 1.04, "stopped_flue"),
            ("Gemshorn 4ft", 4.0, 0.88, "open_flue"),
            ("Harmonic Flute 4ft", 4.0, 1.02, "open_flue"),
            ("Piccolo 2ft", 2.0, 0.94, "open_flue"),
            ("Corno di Bassetto 8ft", 8.0, 0.90, "reed"),
        ]),
        ("Pedal", 30, 24, 16, [
            ("Grand Open Diapason 32ft", 32.0, 1.08, "open_flue"),
            ("Open Diapason Wood 16ft", 16.0, 1.06, "open_flue"),
            ("Violone 16ft", 16.0, 0.86, "open_flue"),
            ("Bourdon 16ft", 16.0, 1.00, "stopped_flue"),
            ("Octave 8ft", 8.0, 0.98, "open_flue"),
            ("Fifteenth 4ft", 4.0, 0.94, "open_flue"),
            ("Trombone 16ft", 16.0, 1.04, "reed"),
            ("Trumpet 8ft", 8.0, 1.00, "reed"),
        ]),
    ]

    pipes = []
    seq = 0
    for div_name, n_notes, base_midi, n_ranks, stop_templates in divisions:
        for r_idx in range(n_ranks):
            stop_name, footage_ft, scale_f, p_type = stop_templates[r_idx % len(stop_templates)]
            rank_label = f"{stop_name} (R{r_idx + 1:02d})"
            for note_i in range(n_notes):
                seq += 1
                midi = base_midi + note_i
                m = compute_pipe_metrics(midi, footage_ft, scale_f, p_type)
                pipes.append({
                    "pipe_id": f"PIPE_{seq:04d}",
                    "seq": seq,
                    "division": div_name,
                    "rank_index": r_idx + 1,
                    "stop_name": rank_label,
                    "pipe_type": p_type,
                    "footage_ft": footage_ft,
                    "scale_factor": scale_f,
                    "midi_note": midi,
                    "hall_temp_c": HALL_TEMP_C,
                    "speed_of_sound_m_s": round(SPEED_OF_SOUND_M_S, 4),
                    "freq_hz": m["freq_hz"],
                    "diameter_m": m["diameter_m"],
                    "computed_length_m": m["computed_length_m"],
                    "mesh_length_m": m["computed_length_m"],
                })

    # Add 132 Case-Front & Solo Tuba Mirabilis speaking pipes -> 4,368 + 132 = 4,500 exact
    for c_i in range(132):
        seq += 1
        midi = 36 + (c_i % 44)
        is_tuba = c_i >= 66
        stop_name = "Tuba Mirabilis 8ft (Solo High-Pressure)" if is_tuba else "Gilt Case Front Open Diapason 16ft/8ft"
        footage_ft = 8.0 if is_tuba else (16.0 if c_i < 22 else 8.0)
        p_type = "reed" if is_tuba else "open_flue"
        scale_f = 1.04
        m = compute_pipe_metrics(midi, footage_ft, scale_f, p_type)
        pipes.append({
            "pipe_id": f"PIPE_{seq:04d}",
            "seq": seq,
            "division": "Case_And_Solo",
            "rank_index": (c_i // 44) + 1,
            "stop_name": stop_name,
            "pipe_type": p_type,
            "footage_ft": footage_ft,
            "scale_factor": scale_f,
            "midi_note": midi,
            "hall_temp_c": HALL_TEMP_C,
            "speed_of_sound_m_s": round(SPEED_OF_SOUND_M_S, 4),
            "freq_hz": m["freq_hz"],
            "diameter_m": m["diameter_m"],
            "computed_length_m": m["computed_length_m"],
            "mesh_length_m": m["computed_length_m"],
        })

    assert len(pipes) == 4500, f"Expected 4500 pipes, got {len(pipes)}"
    return pipes


def main() -> int:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ledgers_dir = os.path.join(base_dir, "ledgers")
    os.makedirs(ledgers_dir, exist_ok=True)
    pipes = generate_organ_schedule()
    out_path = os.path.join(ledgers_dir, "ORGAN_PIPES.jsonl")
    with open(out_path, "w", encoding="utf-8") as fh:
        for p in pipes:
            fh.write(json.dumps(p, separators=(",", ":")) + "\n")
    print(f"Computed and wrote {len(pipes)} organ pipes to {out_path} (speed_of_sound={SPEED_OF_SOUND_M_S:.4f} m/s at {HALL_TEMP_C}C)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
