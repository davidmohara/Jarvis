<!-- system:start -->
# Comp 2 — Extraction Examples (comp-tracker)

Used by step-04 tasks 3-4 when reading the One Texas PowerBI page.

## Row format (task 3)

The One Texas page shows tabular data (when "Show visuals as tables" is active) with rows like:
```
Year, Month    Austin        Dallas        Houston
2026, January  $1,456,127   $2,748,530   $1,235,959
2026, February $1,366,394   $2,911,328   $1,167,126
2026, March    $1,521,899   $3,074,539   $1,268,871
```

## Worked per-month calculation (task 4)

```
<YYYY, Month>:  Austin $<a> + Dallas $<d> + Houston $<h> = $<revenue>
                Austin GP $<agp> + Dallas GP $<dgp> + Houston GP $<hgp> = $<gp>
                Cost = $<revenue> − $<gp> = $<cost>
```
<!-- system:end -->
