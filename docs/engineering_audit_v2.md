# ELEVATE MEAL ENGINE V2 — INDEPENDENT ENGINEERING AUDIT
**Auditor Role:** Principal Software Engineer (Independent Review)
**Files Audited:**
- `app/deterministic_meal_engine.py` (915 lines)
- `app/meal_engine.py` (303 lines)
- `data/meal_metadata.csv`
- `data/nutrition_production_final_v4.csv`

**Date:** 2026-06-23  
**Method:** Direct source code inspection + live Python analysis

> [!CAUTION]
> This audit does NOT rely on implementation summaries, comments, or previous reports. Every finding is independently verified from the source code and live data queries.

---

## PHASE 1 — WEEKLY VARIETY ENGINE

### Implementation Location
`WeeklyVarietyTracker` class — `deterministic_meal_engine.py` lines 105–175

### How It Works
- Maintains six tracking structures: `{breakfast,lunch,dinner,snack}_history` (Sets), `protein_history`, `carb_history`, `cuisine_history`, `template_history` (Lists)
- `record_meal()` adds each component's `food_name` to the corresponding meal_type set, and appends to `protein_history` / `carb_history` if the component's `swap_group` matches known groups
- `variety_penalty()` computes a raw penalty by checking repetition in all six dimensions; penalty is applied in `score_meal()` as `min(20, raw * 0.3)`
- `record_cuisine()` and `record_template()` log the chosen meal's region and blueprint index

### Verification Against Spec

| Check | Status | Notes |
|-------|--------|-------|
| Breakfast rotation | ✅ PASS | `breakfast_history` Set prevents repeats |
| Lunch rotation | ✅ PASS | `lunch_history` Set enforced |
| Dinner rotation | ✅ PASS | `dinner_history` Set enforced |
| Snack rotation | ✅ PASS | `snack_history` Set enforced |
| Protein rotation | ✅ PASS | `protein_history` tracks swap_group |
| Carb rotation | ✅ PASS | `carb_history` tracks swap_group |
| Cuisine rotation | ✅ PASS | `cuisine_history` tracks region |
| Template rotation | ✅ PASS | `template_history` tracks blueprint index |
| Deterministic behaviour | ✅ PASS | Per-slot seed from SHA256(ue:fp:week:day:mt) |
| History tracking | ✅ PASS | Cross-day accumulation confirmed in `generate_weekly_plan` |
| Duplicate prevention | ⚠️ PARTIAL | Prevents via **scoring penalty only**, not hard exclusion. A duplicate can still be selected if all alternatives score lower. |

### Deviations
1. Duplicate prevention is soft (penalty-based), not hard. If the food pool for a role is very small (e.g., salad in lunch — only 1 item), the same food will repeat every time it is needed regardless of penalty.
2. `record_meal()` is called with `best_meal` (optimized Dict with keys `food_name`, `swap_group`) — this is correct, the keys exist in the optimized output.
3. There is a redundant `if best_meal:` check at line 814 — `best_meal` was already checked at line 810.

**Rating: PARTIAL — 7/10**
Penalty system is well-designed but soft enforcement creates deterministic repetition when pool sizes are critically small (confirmed: only 1 salad exists in the Lunch meal_type pool).

---

## PHASE 2 — PORTION OPTIMIZER

### Implementation Location
`optimize_portions()` function — lines 182–243  
`_format_serving()` helper — lines 246–258

### How It Works
- Scales all components proportionally to reach `target_cal` using `scale = target_cal / base_cals`
- Snaps each quantity to the food's `portion_step`, then clamps to `[portion_min, portion_max]`
- For piece/unit serving units, rounds to integer
- Returns list of component dicts plus achieved total calories

### Verification Against Spec

| Check | Status | Notes |
|-------|--------|-------|
| No fractional eggs | ✅ PASS | Lines 212–213: pieces/units rounded to `max(1, round(qty))` |
| No fractional chapati | ✅ PASS | Same piece/unit logic applies |
| No impossible servings | ✅ PASS | Clamp enforced via `portion_min` / `portion_max` metadata |
| Stepped serving sizes | ✅ PASS | `round(raw_qty / p_step) * p_step` |
| Clamped limits | ✅ PASS | `max(p_min, min(p_max, snapped))` |
| Serving formatting | ❌ FAIL | **BUG CONFIRMED**: `_format_serving` produces double unit for cup/tbsp/tsp/bowl/scoop — e.g., `"1.5 cup cup"` instead of `"1.5 cup"` |
| Realistic serving generation | ✅ PASS | For `g`/`ml` units (99% of dataset), output is correct |

### Critical Bug — Line 257
```python
# BUGGY CODE:
return f"{qty:.1f} {unit}".rstrip('0').rstrip('.') + f" {unit}" if '.' in f"{qty:.1f}" else f"{int(qty)} {unit}"
```
When `qty=1.5` and `unit='cup'`:
- `f"{qty:.1f} {unit}"` → `"1.5 cup"`
- `rstrip('0').rstrip('.')` → `"1.5 cup"` (no change, dots/zeros not at end)
- `+ f" {unit}"` → **`"1.5 cup cup"`**

Since 99% of the dataset uses `g` or `ml` units, this bug is rarely triggered in practice, but it is a confirmed defect.

**Rating: PARTIAL — 7/10**

---

## PHASE 3 — MEAL COMPLETENESS ENGINE

### Implementation Location
`BLUEPRINTS` constant — lines 41–67  
`_generate_candidates()` — lines 613–711  
`_validate_plan()` — lines 717–755

### How It Works
- `BLUEPRINTS` defines 4–5 role templates per meal type
- `_generate_candidates` iterates up to `num_candidates * 3 = 120` times, picking a blueprint and filling each role from the filtered pool
- `score_meal()` awards/deducts points for presence of protein and carb roles
- `_validate_plan()` performs a post-generation check using `meal_role` in the formatted food dicts

### Verification Against Spec

| Check | Status | Notes |
|-------|--------|-------|
| Breakfast blueprint | ✅ PASS | 5 blueprints defined |
| Lunch blueprint | ✅ PASS | 4 blueprints defined |
| Dinner blueprint | ✅ PASS | 4 blueprints defined |
| Snack blueprint | ✅ PASS | 4 blueprints defined |
| Required protein | ✅ PASS | Scored −15 if missing, validator flags it |
| Required carb | ✅ PASS | Scored −10 if missing for lunch/dinner |
| Vegetable validation | ⚠️ PARTIAL | No explicit check for `veg_side` presence — blueprints include it but no validator check |
| Duplicate main prevention | ⚠️ PARTIAL | Prevented via variety penalty (soft), not hard exclusion |

### Critical Pool Size Issue
**Only 1 salad food exists in the Lunch meal_type pool** (`High Protein Sprouted Moong Salad`). Blueprint `['carb_base','protein_main','veg_side','salad']` will select this same salad every day it is chosen, causing guaranteed repetition in weekly lunch plans. The fallback at line 668 only tries `pool[pool['meal_role'] == role]` (all meal_types), which gives 20 salads from the Snack pool — contextually incorrect for lunch.

**Rating: PARTIAL — 6/10**

---

## PHASE 4 — MEAL TEMPLATE ENGINE

### Implementation Location
Blueprint selection logic within `_generate_candidates()` — lines 641–651  
`tracker.record_template()` — line 813

### How It Works
- Collects indices of blueprints not used in the last N slots: `unused_idxs = [i for i in range(len(blueprints)) if i not in tracker.template_history[-len(blueprints):]`
- Picks randomly from unused if any; falls back to least-frequently-used if all used
- Records chosen template index in `tracker.template_history`

### Verification Against Spec

| Check | Status | Notes |
|-------|--------|-------|
| Template library | ✅ PASS | 4–5 blueprints per meal type |
| Template rotation | ✅ PASS | Unused-first selection logic present |
| Template scoring | ✅ PASS | `variety_penalty` deducts 25/50 for repeated templates |
| Template reuse prevention | ⚠️ PARTIAL | Soft (penalty), not hard — same blueprint can repeat if all have been used |
| Blueprint selection | ✅ PASS | Deterministic-compatible via seeded RNG |

### Deviations
- The unused-first selection uses `tracker.template_history[-len(blueprints):]` — this is a sliding window, not full history. A blueprint used 10 days ago would be considered "unused" after 4 new days (for 4-blueprint meal types). This is acceptable design.
- Template rotation only tracks at the weekly level — there is no per-day per-meal-type counter.

**Rating: PASS — 8/10**

---

## PHASE 5 — SMART MEAL SWAP ENGINE

### Implementation Location
`build_swap_options()` — lines 338–397  
`get_swap_options()` public API — lines 893–914

### How It Works
- Filters pool by `meal_role == role` and excludes the current food
- Applies ±30% calorie tolerance (code says ±15% in docstring but uses 0.70–1.30 = ±30%)
- Prioritizes same `swap_group` first
- Sorts by `availability + budget` composite score
- Returns up to `limit` (default 4) options

### Verification Against Spec

| Check | Status | Notes |
|-------|--------|-------|
| Swap generation | ✅ PASS | 4 swaps generated per food item |
| Same meal role | ✅ PASS | `pool['meal_role'] == role` filter |
| Allergy filtering | ✅ PASS | `pool` passed is already allergy-filtered |
| Veg/nonveg/vegan compatibility | ✅ PASS | `pool` is already diet-filtered |
| Nutrition similarity | ⚠️ PARTIAL | **Docstring says ±15%**, code uses ±30% (`0.70–1.30`). Inconsistency, but ±30% is more practical for a diverse Indian food database |
| Macro recalculation | ❌ FAIL | Swap options use **raw dataset serving quantities, not recalculated per optimized portion**. A user swapping 250g Chicken for a swap gets raw 100g serving data, not 250g-equivalent |
| Budget ordering | ✅ PASS | `BUDGET_SCORE` applied in `swap_score()` |
| Availability ordering | ✅ PASS | `AVAILABILITY_SCORE` applied |
| Frontend swap output | ✅ PASS | Keys: food_id, food_name, serving, calories, protein, carbs, fat |

### Bug: Swap Pool Not Filtered by meal_type
`build_swap_options()` receives `filtered_pool` (all meal types). Swap candidates for a Breakfast item can include Dinner foods. Example: swapping a breakfast beverage could suggest a dinner biryani if they share the same `meal_role`.

### Bug: Macro Not Recalculated for Swap
The swap shows the food's default serving nutrition, not adjusted to match the original item's portion. If the original item was scaled to 250g (261 kcal), the swap shows at its raw 100g (120 kcal) value. The user sees a 50% calorie drop that is not real.

**Rating: PARTIAL — 6/10**

---

## PHASE 6 — MEAL SCORING ENGINE

### Implementation Location
`score_meal()` — lines 265–331

### How It Works
7-dimension scoring starting at 100.0:
1. **Macro accuracy (30 pts):** `abs(meal_cal - target_cal) / target_cal * 60`, capped at 30
2. **Weekly variety (20 pts):** `min(20, variety_penalty * 0.3)`
3. **Meal completeness (15 pts):** −15 if no protein, −10 if no carb (non-snack)
4. **Portion realism (10 pts):** −3 per component at boundary, max −10
5. **Budget (10 pts):** `(avg_budget_score / 10) * 10 - 10` — net range: −10 to 0
6. **Availability (10 pts):** `(avg_avail_score / 10) * 10 - 10` — net range: −10 to 0
7. **Cuisine rotation (5 pts):** −2 per prior use of same cuisine, max −5

### Verification Against Spec

| Check | Status | Notes |
|-------|--------|-------|
| 40 candidates generated | ✅ PASS | `num_candidates=40` in main loop |
| Macro scoring | ✅ PASS | 30-point dimension |
| Variety scoring | ✅ PASS | 20-point dimension via penalty |
| Completeness scoring | ✅ PASS | 15-point dimension |
| Portion realism scoring | ⚠️ PARTIAL | Logic accesses `c['_raw'].get('portion_min')` — if `_raw` key is absent (defensive), this crashes. In practice it is set by `optimize_portions`, so OK in normal flow |
| Budget scoring | ✅ PASS | 10-point dimension |
| Availability scoring | ✅ PASS | 10-point dimension |
| Cuisine scoring | ✅ PASS | 5-point dimension |
| Final score | ✅ PASS | `max(0.0, score)` — floor at 0 |
| Best candidate selection | ✅ PASS | `best_score` tracking with `>` comparison |

### Scoring Math Bug — Budget & Availability
Both budget and availability scores **only penalize, never reward**:
- `(avg_budget/10)*10 - 10` for all-Low foods = `(10/10)*10-10 = 0` (no bonus)
- For all-High foods = `(2/10)*10-10 = -8` (penalty)

The spec says they contribute `10%` to the score. In reality, low-budget/common foods contribute **0 points** while expensive/rare foods contribute **negative** points. This means a perfect meal of common Indian foods scores 100−30% macro drift only, while expensive foods are penalized. The net effect is correct (incentivizes budget foods) but the framing of the spec is slightly misrepresented.

**Rating: PASS — 8/10**

---

## PHASE 7 — BUDGET & AVAILABILITY ENGINE

### Implementation Location
`AVAILABILITY_SCORE` and `BUDGET_SCORE` constants — lines 70–81  
`_apply_nutrition_rules()` blocklist — lines 600–605  
Weighted sampling in `_generate_candidates()` — lines 680–700

### Verification Against Spec

| Check | Status | Notes |
|-------|--------|-------|
| Availability metadata | ✅ PASS | Column present in `meal_metadata.csv`, no nulls |
| Budget metadata | ✅ PASS | Column present, no nulls |
| Weighted sampling | ✅ PASS | `rng.choices()` with availability weights {very_common:4, common:2, limited:1, rare:0.25} |
| Common foods preferred | ✅ PASS | very_common has 4x weight of limited |
| Rare foods deprioritized | ✅ PASS | rare has 0.25 weight |
| Expensive foods deprioritized | ✅ PASS | Scoring penalty for High budget |
| Indian food prioritization | ✅ PASS | Blocklist removes Western specialty foods; regional scoring applied |

### Distribution of Available Foods
- `very_common`: 862 foods (68%) — correctly dominant in sampling
- `common`: 263 foods (21%)
- `limited`: 161 foods (13%)
- `rare`: 0 foods in current dataset

**Rating: PASS — 8/10**

---

## PHASE 8 — WEEKLY VALIDATOR

### Implementation Location
`_validate_plan()` — lines 717–755

### How It Works
Runs after `generate_weekly_plan()` completes. Checks:
- **CHECK 1&2:** Food name repetition across days within same meal type
- **CHECK 5:** Protein and carb role presence per meal (non-snack)
- CHECKs 3, 4, 6, 7, 8 are noted but not actively implemented

### Verification Against Spec

| Check | Status | Notes |
|-------|--------|-------|
| Duplicate meals | ✅ PASS | CHECK1&2 implemented |
| Duplicate proteins | ❌ FAIL | CHECK3&4 are commented stubs only |
| Duplicate carbs | ❌ FAIL | Same as above |
| Duplicate templates | ❌ FAIL | Not checked in validator (only in scoring) |
| Portion validation | ❌ FAIL | CHECK6 is a comment referencing `optimize_portions`, no active check |
| Macro validation | ❌ FAIL | No overall macro drift check |
| Budget validation | ❌ FAIL | CHECK7&8 are comments only |
| Availability validation | ❌ FAIL | Not validated post-generation |
| Swap validation | ❌ FAIL | Not validated |
| Retry logic | ❌ FAIL | Validator generates warnings but does **not retry** meal generation. The spec requires a failed meal to be regenerated. |

### Critical Missing Feature
The spec requires that if validation fails, the engine **retries** that specific day/meal. Currently the engine prints warnings and returns the plan unchanged. Failed meals are served to the user as-is.

**Rating: PARTIAL — 4/10**

---

## METADATA USAGE AUDIT

| Column | Source | Used by Engine | Notes |
|--------|--------|----------------|-------|
| `food_id` | Both | ✅ Yes | Join key |
| `serving_unit` | Metadata | ✅ Yes | `optimize_portions`, `_format_serving` |
| `serving_quantity` | Metadata | ✅ Yes | Base quantity for scaling |
| `serving_weight_g` | Metadata | ❌ Loaded but never read | Loaded in merge, not referenced in any calculation |
| `meal_role` | Metadata | ✅ Yes | Blueprint matching, scoring, validator |
| `meal_blueprint_type` | Metadata | ❌ Never used | Column loaded but never referenced in engine code |
| `swap_group` | Metadata | ✅ Yes | Protein/carb tracking, swap priority |
| `meal_pair_group` | Metadata | ✅ Yes | Cohesion matching in `_generate_candidates` line 662 |
| `portion_min` | Metadata | ✅ Yes | Clamping in `optimize_portions` |
| `portion_max` | Metadata | ✅ Yes | Clamping in `optimize_portions` |
| `portion_step` | Metadata | ✅ Yes | Snap logic |
| `frequency` | Metadata | ❌ Never used | Loaded but not referenced |
| `meal_complexity` | Metadata | ❌ Never used | Loaded but not referenced |
| `prep_time_minutes` | Metadata | ❌ Never used | Loaded but not referenced |
| `equipment` | Metadata | ❌ Never used | Loaded but not referenced (83 nulls) |
| `budget_level` | Metadata | ✅ Yes | Scoring, swap sorting, output |
| `availability` | Metadata | ✅ Yes | Weighted sampling, scoring, swap sorting, output |
| `season` | Nutrition CSV | ❌ Never used | Present in nutrition CSV but not referenced |
| `recommended_frequency` | Nutrition CSV | ❌ Never used | Present but not referenced |
| `is_suitable_for_weight_loss` | Nutrition CSV | ❌ Never used | Present but not referenced |
| `is_suitable_for_muscle_gain` | Nutrition CSV | ❌ Never used | Present but not referenced |
| `contains_gluten` / `contains_dairy` etc. | Nutrition CSV | ❌ Never used | Engine uses `allergens` string column instead |

**Confirmed Unused Metadata (5 metadata columns, 6 nutrition columns):**
`meal_blueprint_type`, `frequency`, `meal_complexity`, `prep_time_minutes`, `equipment`, `season`, `recommended_frequency`, `is_suitable_for_weight_loss`, `is_suitable_for_muscle_gain`, `serving_weight_g`, `contains_*` boolean columns

---

## JSON OUTPUT VERIFICATION

Every item in `weekly_plan[day][meal_type]` (from line 820–835):

| Field | Present | Notes |
|-------|---------|-------|
| `food_id` | ✅ Yes | |
| `food_name` | ✅ Yes | |
| `meal_type` | ✅ Yes | |
| `meal_role` | ✅ Yes | Added in latest fix |
| `serving` | ✅ Yes | May have double-unit bug for cup/tbsp |
| `serving_weight` | ✅ Yes | `round(c['serving_qty'], 1)` |
| `calories` | ✅ Yes | `round(c['calories'])` — integer |
| `protein` | ✅ Yes | 1 decimal |
| `carbs` | ✅ Yes | 1 decimal |
| `fat` | ✅ Yes | 1 decimal |
| `budget_level` | ✅ Yes | |
| `availability` | ✅ Yes | |
| `swap_group` | ✅ Yes | |
| `swap_options` | ✅ Yes | List of up to 4 options |

**All 14 required fields are present. ✅**

Note: The `_raw` key (internal use for scoring) is correctly NOT included in `food_out`. However, the `swap_options` sub-objects lack `meal_role` — acceptable since they are used for display, not further planning.

---

## FRONTEND SUPPORT VERIFICATION

### Wrapper (`meal_engine.py`)
- `generate_meal_plan()` correctly reads V2's `plan` key with fallback to `weekly_plan` (line 143 area)
- `_scale_meal_item()` correctly scales calories/protein/carbs/fat by intensity multiplier
- `suggest_daily_meals()` correctly reads `food_name` with fallback to `name`
- `get_swap_options()` correctly delegates to underlying engine

### API Backward Compatibility
- Old key `name` is still populated via `item.get('food_name', item.get('name', ''))`
- New key `food_name` is now also present
- `swap_options`, `meal_role`, `budget_level`, `availability`, `serving` are new additions — no existing frontend code would break since they are additive

**Frontend Support: PASS**

---

## ENGINEERING RULEBOOK VERIFICATION

| Rule | Status | Reason |
|------|--------|--------|
| Rule 1: No meals nobody eats | ✅ PASS | Blocklist removes stocks/icings/gateaux; blueprints enforce complete meals |
| Rule 2: No fractional servings | ✅ PASS | piece/unit rounded to integer; g/ml to integer |
| Rule 3: Every meal looks like a real Indian meal | ⚠️ PARTIAL | Blueprints enforce multi-component meals, but single-component `['combo_meal']` blueprints can produce "Rice only" situations |
| Rule 4: Nutrition AND practicality | ✅ PASS | Both scored simultaneously |
| Rule 5: Week-level thinking | ✅ PASS | `WeeklyVarietyTracker` accumulates across all 7 days |
| Rule 6: Week-level optimization | ✅ PASS | Tracker state persists across the weekly loop |
| Rule 7: Not day-by-day | ✅ PASS | Variety penalties apply cross-day |
| Rule 8: Swap preserves nutrition | ⚠️ PARTIAL | Swap searches ±30% calories, but macros at raw serving — not recalculated |
| Rule 9: Swap recalculates totals | ❌ FAIL | No per-swap macro recalculation for the optimized serving size |
| Rule 10: Budget engine reduces expensive frequency | ✅ PASS | Weighted sampling + scoring penalty |
| Rule 11: All meals from approved blueprints | ✅ PASS | All candidates generated through `BLUEPRINTS` |
| Rule 12: No non-blueprint combinations | ✅ PASS | Only blueprint roles are filled |
| Rule 13: Validator runs before return | ✅ PASS | `_validate_plan` called before `return` |
| Rule 14: Failing meal regenerated | ❌ FAIL | Validator reports warnings but does NOT retry |
| Rule 15: Every food exposes swap options | ✅ PASS | `build_swap_options()` called for every food item |
| Rule 16: Swap maintains meal role | ✅ PASS | `pool['meal_role'] == role` filter |
| Rule 17: Swap recalculates portion | ❌ FAIL | Shows raw dataset serving, not scaled to match original |
| Rule 18: Culturally realistic | ✅ PASS | Indian food database, regional scoring, common foods preferred |
| Rule 19: No two complete meals in one slot | ✅ PASS | Blueprint roles differentiate components |
| Rule 20: Lunch > Dinner calorie | ✅ PASS | 35% lunch vs 28% dinner |
| Rule 21: Protein never sacrificed | ✅ PASS | −15 score for missing protein, highest deduction |
| Rule 22: Deterministic same profile = same plan | ✅ PASS | SHA256-based seed verified identical across two runs |
| Rule 23: Modular components | ✅ PASS | Separate classes/functions for each phase |

---

## HIDDEN BUGS FOUND

### 🔴 Critical (Must Fix Before Production)

**BUG-1: Salad Pool Starvation in Lunch**
- Only 1 food has `meal_role=salad` AND `meal_type=Lunch` in the database
- Blueprint `['carb_base','protein_main','veg_side','salad']` will always select "High Protein Sprouted Moong Salad" for lunch
- Creates guaranteed repetition across all 7 days
- **Location:** Data — `meal_metadata.csv` needs more salad entries tagged as Lunch, or the blueprint should be relaxed

**BUG-2: `_format_serving` Double Unit**
- Line 257: `f"{qty:.1f} {unit}".rstrip('0').rstrip('.') + f" {unit}"` produces `"1.5 cup cup"` for volumetric units
- Affects `cup`, `tbsp`, `tsp`, `bowl`, `scoop` serving units
- Currently low impact (most foods use g/ml) but incorrect and visible to user
- **Location:** `deterministic_meal_engine.py` line 257

**BUG-3: Swap Macro Not Recalculated**
- `build_swap_options()` shows raw dataset nutrition (e.g., 100g chicken = 165 kcal)
- The original item may have been optimized to 250g (412 kcal)
- User performing a swap sees completely different calorie values with no explanation
- This violates Rule 17 of the Engineering Rulebook
- **Location:** `build_swap_options()` lines 383–395

**BUG-4: Validator Has No Retry Logic**
- `_validate_plan()` detects issues and returns warning strings
- `generate_weekly_plan()` logs them but returns the invalid plan unchanged
- The spec requires: "if a meal fails validation, regenerate it"
- **Location:** `generate_weekly_plan()` lines 840–845

### 🟡 Major (Fix Before Wide Release)

**BUG-5: Swap Candidates Not Filtered by meal_type**
- `build_swap_options()` uses the full `filtered_pool` (all meal types)
- A breakfast food could swap to a dinner biryani if they share a `meal_role`
- **Location:** `build_swap_options()` line 352

**BUG-6: veg Filter Double Condition**
- Lines 569–570 apply two separate conditions for veg filtering:
  ```python
  df = df[df['is_vegetarian']...isin(['true','1','yes'])]
  df = df[~df['is_vegetarian']...isin(['false','0','no'])]
  ```
  The second filter is redundant since the first already selects only truthy rows. If any row has an unexpected value (e.g., empty string), it passes both conditions.
- More correct would be: filter once to include only `['true','1','yes']`

**BUG-7: Duplicate Candidate Records**
- `_generate_candidates()` runs 120 iterations to produce 40 candidates
- There is no deduplication — the same combination of foods can appear as multiple candidates
- The best-scoring candidate wins, but duplicate candidates waste scoring cycles

**BUG-8: Blueprint Selection Bias After Full Rotation**
- When all blueprints have been used (tracker full), code falls back to `min(range(len(blueprints)), key=lambda i: counts.get(i, 0))`
- This is a `min` on counts — but it selects blueprint 0 when all counts are equal (tie-breaking is index order, not random)
- Creates a bias toward the first blueprint after a full rotation cycle

### 🟢 Minor (Low Impact)

**BUG-9: Redundant Guard at Line 814**
```python
if best_meal:           # line 810
    ...
    if best_meal:       # line 814 — redundant inner check
        tracker.record_cuisine(...)
```

**BUG-10: `week_offset` Ignored by Frontend**
- `week_offset` is read from `profile.get('week_offset', 0)` — the frontend never sends this field
- All users always get `week_offset=0` → same weekly plan forever for same profile
- Users who don't interact (same profile for 4 weeks) never see variety across weeks

**BUG-11: Availability `'rare'` Has Weight 0.25, Not 0**
- `AVAILABILITY_SCORE` dict assigns `rare: 0` (line 74) for scoring
- But `weights_map` in `_generate_candidates` assigns `rare: 0.25` (line 682)
- Inconsistency: scoring discourages rare foods but sampling still picks them occasionally

**BUG-12: Blocklist Substring Match Too Broad**
- `re.escape(t)` without word boundaries will match substrings
- e.g., `'mousse'` in blocklist would block any food with "mousse" anywhere, including hypothetical "Mousseline Dal"
- No word boundary (`\b`) anchoring in the pattern

---

## STRESS TEST MENTAL VERIFICATION

| Profile | Expected Behaviour | Assessment |
|---------|-------------------|------------|
| Weight Loss | 0.85 × TDEE, high protein (1.6g/kg), lower carb (50%) | ✅ Correct: goal multiplier + carb split applied |
| Maintenance | 1.0 × TDEE, moderate protein (1.0g/kg) | ✅ Correct |
| Muscle Gain | 1.10 × TDEE, high protein (1.8g/kg), high carb (65%) | ✅ Correct (validated in test run: 2854 kcal) |
| Male | Standard BMR formula used | ✅ Correct |
| Female | BMR −161, additional 0.90 multiplier on kcal and protein | ✅ Correct |
| Veg | `is_vegetarian == true` filter | ✅ Correct; 1136 foods available |
| NonVeg | No diet filter | ✅ Correct |
| Vegan | `is_vegan == true` filter | ✅ Correct; 942 foods, verified no dairy allergens |
| Egg allergy | Searches `allergens` string for `\begg\b` | ✅ Correct (46 foods match) |
| Milk allergy | Expands to milk/dairy/lactose/cheese/paneer/butter/ghee/cream | ✅ Correct |
| Nut allergy | Expands to nuts/almond/cashew/walnut/peanut/pistachio | ✅ Correct |
| Soy allergy | Falls through to `expanded.append(al)` → searches for `\bsoy\b` | ✅ Correct |
| Gluten allergy | Expands to wheat/gluten/barley/rye/maida/suji/semolina/atta | ✅ Correct |
| High calorie target | Clamped to max 5000 kcal | ✅ Correct |
| Low calorie target | Floored at 1200 kcal | ✅ Correct |
| Very small food pool (e.g., restrictive vegan + nut allergy) | Fallback drops meal_type filter — selects from full remaining pool | ⚠️ Pool may be too small for some blueprints; no minimum pool size guard |
| Very restrictive user (multiple allergies + vegan + gluten-free) | May produce empty candidate list | ⚠️ Empty candidate returns empty `[]` for that meal slot — frontend receives no meals for that slot, no error raised to user |

---

## FINAL REPORT

### Scores

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| **Overall Architecture** | **7/10** | Clean separation of phases, correct data flow, good use of constants and classes. Weak: validator has no retry, phases 3&4 partially merged |
| **Meal Quality** | **6/10** | Blueprints produce realistic meals. Salad starvation creates repetition. Single-component breakfasts (`['combo_meal']`) can produce "Oats only" meals. Swap macros not recalculated |
| **Code Quality** | **7/10** | Readable, well-commented, type-hinted. Format_serving bug, redundant guard, inconsistent availability scoring are defects |
| **Performance** | **7/10** | O(40 × 7 × 4) = 1120 candidate generations per request. No async, no caching of the weekly plan. Re-generates on every API call |
| **Maintainability** | **7/10** | Module-level constants are good. Unused metadata columns create confusion. Phase 3&4 conflated in one function |
| **Production Readiness** | **5/10** | Missing retry logic, swap macro recalculation, validator stubs, and the salad pool bug make this unsuitable for high-volume deployment without fixes |

---

### Critical Issues
1. **Validator has no retry logic** — failed meals served to user unchanged
2. **Salad pool starvation** — only 1 salad in Lunch pool, causing weekly repetition
3. **Swap macro not recalculated** — misleads users on calorie impact of swaps

### Major Issues
4. **`_format_serving` double unit bug** — `"1.5 cup cup"` for non-g/ml units
5. **Swap candidates not filtered by meal_type** — breakfast food can suggest dinner food
6. **5 metadata columns completely unused** (`meal_blueprint_type`, `frequency`, `meal_complexity`, `prep_time_minutes`, `equipment`) — wasted schema
7. **`week_offset` never sent by frontend** — users get identical plan every week
8. **Empty candidate pool returns silent empty meal** — no error propagation to user

### Minor Issues
9. Redundant `if best_meal` guard (line 814)
10. Blocklist uses substring match without word boundaries
11. `rare` food weight inconsistency (0 in scoring, 0.25 in sampling)
12. veg filter has redundant second condition
13. Blueprint tie-breaking biased toward index 0
14. Duplicate candidates generated without deduplication

### Recommendations
1. **Immediate:** Fix `_format_serving` double-unit bug (1 line change)
2. **Immediate:** Add word boundaries to blocklist pattern
3. **Short-term:** Add retry loop to `generate_weekly_plan` (max 2 retries for failed validator checks)
4. **Short-term:** Add `meal_type` filter to `build_swap_options()`
5. **Short-term:** Scale swap option nutrition to match original item's portion
6. **Short-term:** Add 10+ salad foods tagged as `meal_type=Lunch` in `meal_metadata.csv`
7. **Medium-term:** Implement `week_offset` rotation via frontend (send current ISO week number)
8. **Medium-term:** Remove or utilize unused metadata columns (`frequency`, `meal_complexity`, `prep_time_minutes`, `equipment`)
9. **Medium-term:** Add minimum pool size guard with graceful degradation messaging

---

## FINAL VERDICT

> **PASS WITH MAJOR ISSUES**

The engine is architecturally sound, produces realistic Indian meals, is deterministic, and passes the core spec requirements for all 8 phases at a functional level. The weekly plan quality is demonstrably better than a naive macro calculator.

However, three production-blocking issues exist:
- The validator does not retry failed meals
- Swap options show incorrect nutrition (raw vs scaled)
- The salad pool guarantees weekly repetition

These must be resolved before the nutrition feature can be considered complete for production release.
