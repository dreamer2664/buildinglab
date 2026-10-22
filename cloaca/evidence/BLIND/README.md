# G12 blind battery - runner instructions

24 trials, 6 classes (light, palette, bond, glazing, tide, dress). Each trial in
`trials.jsonl` names two rendered images (A and B) under `renders/proofs/<id>_1024.png`.
Exactly one of the pair is a CONTROL: a render that breaks one packet law on purpose
(electric light, concrete palette, stack bond, modern blue glazing, water line off the
harmonic gauge, hi-vis dress). The other is compliant.

To run the battery: look at each pair, decide which image is the control, and append one
JSON line per trial to `evidence/BLIND_ANSWERS.jsonl`:

    {"trial": 1, "pick": "A", "runner": "<your handle, not bazalgette>"}

`python3 tools/blind_test.py` (no args) scores the answers against `key.jsonl`. Rows whose
runner is this agent are ignored by design - the gate cannot be self-satisfied. Per-class
and total accuracy are printed; the gate record picks them up at the next gates.py run.
