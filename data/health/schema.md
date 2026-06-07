# Health Metrics Log Schema

**File:** `data/health/metrics-log.json`

Galen reads and writes this file. It is the single source of truth for longitudinal health tracking. Every skill that produces real metric values appends an entry here. This enables multi-year trend analysis without relying on session memory.

---

## Entry Types

Each entry in the `entries` array has a `category` field that determines its structure.

### `bloodwork`

Written by `galen-bloodwork` skill after every bloodwork draw.

```json
{
  "entry_id": "bloodwork-2026-06-01",
  "date": "2026-06-01",
  "category": "bloodwork",
  "source": "Function Health / Quest Diagnostics",
  "source_file": "~/Library/CloudStorage/Dropbox/Family/Health/David - Bloodwork/2026/2026-06-01.pdf",
  "physician": "Dr. Julli Randol",
  "metrics": {
    "cardiovascular": {
      "apob_mg_dl": null,
      "ldl_p_nmol_l": null,
      "lp_a_nmol_l": null,
      "total_cholesterol_mg_dl": null,
      "hdl_mg_dl": null,
      "ldl_mg_dl": null,
      "triglycerides_mg_dl": null,
      "hscrp_mg_l": null,
      "homocysteine_umol_l": null
    },
    "metabolic": {
      "fasting_insulin_uiu_ml": null,
      "hba1c_pct": null,
      "fasting_glucose_mg_dl": null
    },
    "hormonal": {
      "total_testosterone_ng_dl": null,
      "free_testosterone_pg_ml": null,
      "estradiol_e2_pg_ml": null,
      "lh_miu_ml": null,
      "fsh_miu_ml": null,
      "dhea_s_ug_dl": null,
      "igf1_ng_ml": null
    },
    "micronutrients": {
      "vitamin_d3_ng_ml": null,
      "b12_pg_ml": null,
      "folate_ng_ml": null,
      "ferritin_ng_ml": null,
      "omega3_index_pct": null
    },
    "blood_health": {
      "mch_pg": null,
      "mcv_fl": null,
      "hemoglobin_g_dl": null,
      "hematocrit_pct": null
    },
    "liver": {
      "alt_u_l": null,
      "ast_u_l": null,
      "alp_u_l": null
    }
  },
  "out_of_range": [],
  "notes": ""
}
```

### `whoop_monthly`

Written by `galen-whoop-analysis` skill after a 30-day analysis.

```json
{
  "entry_id": "whoop-monthly-2026-06",
  "date": "2026-06-07",
  "category": "whoop_monthly",
  "source": "WHOOP API",
  "period_start": "2026-05-08",
  "period_end": "2026-06-07",
  "metrics": {
    "recovery_avg": null,
    "recovery_trend": null,
    "hrv_rmssd_avg": null,
    "hrv_trend": null,
    "rhr_avg": null,
    "rhr_trend": null,
    "sleep_duration_avg_min": null,
    "sleep_efficiency_avg_pct": null,
    "sleep_trend": null,
    "red_days": null,
    "yellow_days": null,
    "green_days": null,
    "workout_count": null,
    "avg_strain": null,
    "key_patterns": []
  },
  "notes": ""
}
```

### `dexa`

Written by `galen-visit-prep` or `galen-monthly-health-review` when DEXA data is read.

```json
{
  "entry_id": "dexa-2026-04",
  "date": "2026-04-01",
  "category": "dexa",
  "source": "BodySpec DEXA",
  "source_file": "~/Library/CloudStorage/Dropbox/Family/Health/David - DEXA/2026-04 bodyspec-results.pdf",
  "metrics": {
    "weight_lbs": null,
    "body_fat_pct": null,
    "lean_mass_lbs": null,
    "fat_mass_lbs": null,
    "bmi": null,
    "vat_lbs": null,
    "ag_ratio": null,
    "bone_density_t_score": null
  },
  "notes": ""
}
```

### `body_comp`

Written when body composition tracking is updated from the health tracking Excel file (between DEXA scans).

```json
{
  "entry_id": "body-comp-2026-06-07",
  "date": "2026-06-07",
  "category": "body_comp",
  "source": "David - Health Tracking.xlsx",
  "metrics": {
    "weight_lbs": null,
    "body_fat_pct": null,
    "bmi": null
  },
  "notes": ""
}
```

### `protocol_change`

Written by `galen-protocols` skill when supplement or peptide status changes.

```json
{
  "entry_id": "protocol-change-2026-06-07",
  "date": "2026-06-07",
  "category": "protocol_change",
  "source": "manual / bloodwork-triggered / physician",
  "changes": [
    {
      "item": "CoQ10",
      "type": "supplement",
      "action": "started",
      "dose": "500mg",
      "frequency": "daily",
      "rationale": "ApoB management per June 1 bloodwork"
    }
  ],
  "notes": ""
}
```

### `monthly_review`

Written by `galen-monthly-health-review` workflow at the end of each monthly review.

```json
{
  "entry_id": "monthly-review-2026-06",
  "date": "2026-06-07",
  "category": "monthly_review",
  "period": "June 2026",
  "summary": {
    "recovery_status": "improving | stable | declining",
    "bloodwork_status": "no concerns | watch items | act items | urgent",
    "body_comp_status": "on track | at risk | off track",
    "horsemen_cv_status": "low | moderate | elevated",
    "horsemen_metabolic_status": "low | moderate | elevated",
    "horsemen_neuro_status": "low | moderate | elevated",
    "horsemen_cancer_status": "low | moderate | elevated",
    "overall_trajectory": "improving | stable | declining"
  },
  "obsidian_note": "Mind/Health/Monthly Review - June 2026.md",
  "notes": ""
}
```

---

## Usage Rules

1. **Append only.** Never edit or delete existing entries.
2. **Real values only.** If a metric is not available from the source file, use `null`. Never estimate or interpolate.
3. **All fields from source.** Extract every available marker from bloodwork, DEXA, etc. Partial entries are fine — use `null` for anything not on the panel.
4. **entry_id format:** `{category}-{date}` using ISO date. For monthly entries, use `{category}-{YYYY-MM}`.
5. **Trend queries:** To trend a metric, filter `entries` by `category`, sort by `date`, and extract the target field across entries.
