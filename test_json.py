from crm.pipeline.rules import PIPELINE_RULES, RESULT_LABELS, CHECKLIST_LABELS
import json

current_stage = "CONTA_PARA_CONTATO"
pipeline_rules = PIPELINE_RULES.get(current_stage, {})

# Test results generation
results = []
for k in pipeline_rules.get('results', {}).keys():
    next_stage = pipeline_rules['results'][k]
    results.append({
        "key": k,
        "label": RESULT_LABELS.get(k, k),
        "next_status_label": next_stage,
    })

# Test checklist generation  
checklist = [
    [item, CHECKLIST_LABELS.get(item, item)]
    for item in pipeline_rules.get('checklist', [])
]

print("=== RESULTS JSON ===")
print(json.dumps(results, indent=2, ensure_ascii=False))

print("\n=== CHECKLIST JSON ===")
print(json.dumps(checklist, indent=2, ensure_ascii=False))
