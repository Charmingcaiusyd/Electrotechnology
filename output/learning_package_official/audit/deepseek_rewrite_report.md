# Official Semantic Rewrite Report

This pass rewrote the V3.1 questions that were flagged for possible PDF source-domain mismatch.

## Summary

- Total questions: 3000
- Flagged before rewrite: 87
- DeepSeek rewritten: 87
- Fallback rewritten: 0
- Unresolved mismatch flags: 0
- Exact duplicate questions: 0
- Duplicate variants resolved: 4
- MC answer key errors: 0

## Rewritten IDs

- `V3-S1-SEC3-Q034`
- `V3-S10-SEC1-Q047`
- `V3-S10-SEC2-Q027`
- `V3-S10-SEC4-Q017`
- `V3-S2-CH-Q042`
- `V3-S2-CH-Q044`
- `V3-S2-CH-Q080`
- `V3-S2-SEC1-Q045`
- `V3-S2-SEC1-Q046`
- `V3-S2-SEC1-Q047`
- `V3-S2-SEC1-Q048`
- `V3-S2-SEC2-Q043`
- `V3-S2-SEC2-Q044`
- `V3-S2-SEC2-Q045`
- `V3-S2-SEC3-Q039`
- `V3-S2-SEC3-Q040`
- `V3-S2-SEC3-Q042`
- `V3-S2-SEC3-Q048`
- `V3-S2-SEC3-Q050`
- `V3-S2-SEC4-Q036`
- `V3-S2-SEC4-Q037`
- `V3-S2-SEC4-Q038`
- `V3-S2-SEC4-Q039`
- `V3-S2-SEC4-Q045`
- `V3-S2-SEC4-Q047`
- `V3-S4-CH-Q050`
- `V3-S4-CH-Q051`
- `V3-S4-CH-Q052`
- `V3-S4-CH-Q057`
- `V3-S4-CH-Q058`
- `V3-S4-CH-Q061`
- `V3-S4-CH-Q067`
- `V3-S4-CH-Q068`
- `V3-S4-CH-Q072`
- `V3-S4-SEC1-Q020`
- `V3-S4-SEC1-Q021`
- `V3-S4-SEC1-Q023`
- `V3-S4-SEC1-Q029`
- `V3-S4-SEC1-Q030`
- `V3-S4-SEC1-Q034`
- `V3-S4-SEC1-Q046`
- `V3-S4-SEC1-Q047`
- `V3-S4-SEC1-Q048`
- `V3-S4-SEC2-Q031`
- `V3-S4-SEC2-Q032`
- `V3-S4-SEC2-Q037`
- `V3-S4-SEC2-Q038`
- `V3-S4-SEC2-Q039`
- `V3-S4-SEC2-Q041`
- `V3-S4-SEC2-Q047`
- `V3-S4-SEC3-Q016`
- `V3-S4-SEC3-Q021`
- `V3-S4-SEC3-Q022`
- `V3-S4-SEC3-Q025`
- `V3-S4-SEC3-Q031`
- `V3-S4-SEC3-Q032`
- `V3-S4-SEC3-Q036`
- `V3-S4-SEC3-Q048`
- `V3-S4-SEC3-Q049`
- `V3-S4-SEC3-Q050`
- `V3-S4-SEC4-Q020`
- `V3-S4-SEC4-Q032`
- `V3-S4-SEC4-Q033`
- `V3-S4-SEC4-Q039`
- `V3-S4-SEC4-Q041`
- `V3-S4-SEC4-Q043`
- `V3-S4-SEC4-Q049`
- `V3-S4-SEC4-Q050`
- `V3-S5-CH-Q074`
- `V3-S5-SEC1-Q042`
- `V3-S5-SEC2-Q050`
- `V3-S6-CH-Q044`
- `V3-S6-CH-Q045`
- `V3-S6-CH-Q075`
- `V3-S6-CH-Q076`
- `V3-S6-SEC1-Q027`
- `V3-S6-SEC1-Q028`
- `V3-S6-SEC2-Q039`
- `V3-S6-SEC2-Q040`
- `V3-S6-SEC3-Q020`
- `V3-S6-SEC3-Q021`
- `V3-S6-SEC4-Q032`
- `V3-S6-SEC4-Q033`
- `V3-S9-CH-Q046`
- `V3-S9-SEC1-Q036`
- `V3-S9-SEC2-Q021`
- `V3-S9-SEC4-Q026`

## Audit JSON

```json
{
  "total": 3000,
  "by_module": {
    "S1": 300,
    "S10": 300,
    "S2": 300,
    "S3": 300,
    "S4": 300,
    "S5": 300,
    "S6": 300,
    "S7": 300,
    "S8": 300,
    "S9": 300
  },
  "by_type": {
    "fault_finding": 431,
    "multiple_choice": 1046,
    "scenario": 963,
    "short_answer": 560
  },
  "flagged_questions_before_rewrite": 87,
  "deepseek_rewritten": 87,
  "fallback_rewritten": 0,
  "resolved_source_flags": 87,
  "unresolved_source_domain_mismatch_flags": 0,
  "mismatch_terms_remaining_in_rewritten_questions": 0,
  "exact_duplicate_questions": 0,
  "duplicate_variants_resolved": 4,
  "multiple_choice": {
    "count": 1046,
    "all_have_six_options": true,
    "answer_key_invalid": 0
  },
  "missing_fields": {},
  "rewrite_model_used": {
    "deepseek-chat": 85,
    "deepseek-v4-pro": 2
  },
  "cache_path": "D:\\Backup\\Documents\\CAD\\deepseek_official_rewrite_cache.json"
}
```
