# Payoff note and export gate

Candidate scores in `candidates.md` come from loudness, loudness jumps, hype words and speech rate. They never look at
the picture, so a loud, quiet-driving or menu moment can score "strong". A score only shortlists.

Rules in this fork:

- **`payoff` note.** Each pick in `picks.json` needs `"payoff": "<what you saw or heard as setup and result>"`
  (at least 20 characters). It is your record that you looked at the contact sheet or clip. If you cannot write one,
  do not export the moment. `clipper check` reports the missing note as a failure.
- **Long dead air fails.** A silent stretch of 5 s or more in the finished clip (no word, no label) is now a failure
  in `clipper check`, not only an edit note. Cut it with `segments`.
- **Failures block `clipper render`.** A failing `check`, or a pick without a `payoff` note, stops a normal render with
  nothing written. `--diagnostic` renders anyway into `exports/<profile>/<date>/diagnostic/` for a pipeline test. A
  diagnostic render is not a clip to post.
- **Hook ranking is wording only.** `clipper simulate` ranks hook wording by fitted features. It does not know whether
  the scene supports the hook. Do not pick a hook the footage does not show, or add a hook to a scene with no payoff.

Tests: `python -m unittest tests.test_payoff_gate`.
