# Implementation Plan - Nutrition Engine Fixes

This plan details the changes required to resolve empty meal plans for lunch/dinner, incorrect protein scaling/oscillation, incorrect region/cuisine limits, and the frontend black blank screen on cache load.

## User Review Required
> [!IMPORTANT]
> - These fixes will immediately improve the accuracy of protein targets and enforce a strict Maharashtrian cuisine layout (limiting other region cuisines to $\le 10\%$ of weekly meals).
> - Candidate starvation caused by applying the weekly cuisine limit to individual side dishes is resolved by applying it only at the meal blueprint level.

## Open Questions
No open questions at this stage.

## Proposed Changes

### Nutrition Engine

---

#### [MODIFY] [weekly_optimizer.py](file:///d:/Final%20Year%20Project/githubclone%2022%20mor/githubclone/ELEVATE_GITHUB/Elevate/backend-python/app/nutrition_engine/weekly_optimizer.py)
- Implement `_get_meal_cuisine(self, candidate_plate) -> str` to correctly identify and normalize the cuisine of a meal by scanning all its items (prioritizing non-Pan Indian cuisines if present).
- Update the weekly variety tracking logic to call `self._get_meal_cuisine` instead of using the naive first-item fallback.
- Cap the carried-over protein deficit added to the snack target to a maximum of $\pm 10\text{g}$ to prevent snack protein targets from inflating.

---

#### [MODIFY] [candidate_generator.py](file:///d:/Final%20Year%20Project/githubclone%2022%20mor/githubclone/ELEVATE_GITHUB/Elevate/backend-python/app/nutrition_engine/candidate_generator.py)
- Remove the `other_cuisine_count >= 2` check from `get_valid_ingredients_for_role` and fallback `_is_eligible` logic to ensure side dishes are not starved or blocked by weekly cuisine limits.
- Keep the `is_allowed_other_region_food_in_maharashtra` check for individual items.

---

#### [MODIFY] [portion_optimizer.py](file:///d:/Final%20Year%20Project/githubclone%2022%20mor/githubclone/ELEVATE_GITHUB/Elevate/backend-python/app/nutrition_engine/portion_optimizer.py)
- Track the combination of food portion quantities that minimizes the combined calorie and protein error relative to target macros at each step of fine-tuning.
- Restore the best portion quantities prior to constructing the final result list to prevent overshoot/oscillation.

---

### Backend Integration

---

#### [MODIFY] [meal_engine.py](file:///d:/Final%20Year%20Project/githubclone%2022%20mor/githubclone/ELEVATE_GITHUB/Elevate/backend-python/app/meal_engine.py)
- Handle cached plans defensively in `_apply_intensity_adjustments`. If `weekly_plan` is a cached dictionary directly containing day keys (instead of a wrapper dictionary), map the days correctly.
- Accept `profile` as a parameter and re-generate `daily_targets` on the fly if they are missing or empty in the cached data.

## Verification Plan

### Automated Tests
- Run `python test_meal.py` in the `backend-python` folder to verify that:
  - The plan generates without crash.
  - Meal plans contain non-empty lunch and dinner slots.
  - The protein targets match closely (no extreme overshoot).
  - Maharashtrian region cuisine limits ($\le 10\%$ other cuisines) are correctly respected.
