# Performance and Caching Fixes

## Issues Identified

### 1. Workout Plan Generation
- **Issue**: Plans regenerate on every login despite caching logic
- **Root Cause**: Cache exists in memory but not persisted to database per user
- **Impact**: 3-8 second delay on each login

### 2. Muscle Group Diversity
- **Issue**: All days showing "Full Body" instead of varied muscle groups
- **Root Cause**: Split selection logic may be falling back to default
- **Impact**: Poor workout variety, user confusion

### 3. Meal Plan Generation
- **Issue**: Slow generation on login
- **Root Cause**: V6 engine doing full computation even with valid cached plan
- **Impact**: Additional 2-4 second delay

## Solutions Implemented

### Fix 1: Database-backed Workout Plan Persistence
- Store generated plans in `weekly_workout_plans` collection
- Check database before ML generation
- Cache for 7 days with profile hash

### Fix 2: Optimize Workout Engine Initialization
- Lazy load heavy components (WGER index, media cache)
- Precompute feature vectors
- Cache ML model predictions

### Fix 3: Fix Muscle Group Assignment
- Verify V2 split selection is enabled
- Add fallback logic if no valid split found
- Log split selection for debugging

### Fix 4: Meal Plan Performance
- Verify cached plans are returned immediately
- Optimize V6 engine meal selection
- Reduce template iteration overhead
