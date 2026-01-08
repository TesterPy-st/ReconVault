# ReconVault - Post-Fix Testing Guide

## Quick Test Checklist

Use this guide to verify all fixes are working correctly.

---

## Test Environment Setup

### Option A: Full Docker (Recommended)
```bash
# From project root
docker-compose up -d

# Wait 30 seconds for all services to start
# Check: docker-compose ps
```

### Option B: Local Development (Backend + Frontend)

#### Backend
```bash
cd backend

# Recreate venv (if needed)
bash setup_venv.sh

# Activate
source venv/bin/activate

# Start backend
python -m app.main
```

#### Frontend
```bash
cd frontend

# Start development server
npm run dev

# Opens: http://localhost:5173
```

---

## Fix #1: Performance (Infinite Render Loop)

### What Was Fixed
- Throttled `setPerfMetrics` to update every 500ms instead of every animation frame
- Eliminated React "maximum update depth exceeded" warning

### How to Test

1. Open frontend at http://localhost:5173
2. Open browser DevTools (F12)
3. Check Console tab

**Expected Result**:
- ✅ NO warning: "Maximum update depth exceeded"
- ✅ NO warning: "Too many re-renders"
- ✅ Graph renders smoothly
- ✅ Performance metrics update periodically (not frantically)

**If Failed**:
- ❌ Still seeing "maximum update depth exceeded"
- Check: Open DevTools Console and look for the warning
- Fix needed: Ensure you're using the latest code

---

## Fix #2: WebSocket Connection Issues

### What Was Fixed
- Added max reconnection attempts (10)
- Stopped reconnection after max attempts reached
- Reduced console spam with development-only logging

### How to Test

#### Test A: WebSocket Without Backend

1. Start frontend ONLY (without backend)
2. Open DevTools Console
3. Watch connection attempts

**Expected Result**:
- ✅ WebSocket attempts to connect 10 times
- ✅ After 10 attempts, STOPS and shows error
- ✅ Console shows: "Max reconnection attempts reached. Stopping reconnection."
- ✅ Clean console (minimal logs in production)

#### Test B: WebSocket With Backend

1. Start backend (wait for it to be ready)
2. Start frontend
3. Watch DevTools Console

**Expected Result**:
- ✅ WebSocket connects on first attempt
- ✅ Console shows: "WebSocket connected successfully"
- ✅ NO "Connection attempt already in progress" warnings
- ✅ NO duplicate connection attempts

---

## Fix #3: API Error Handling

### What Was Fixed
- Reduced API timeout from 30s to 10s
- Added user-friendly error messages
- Prevented login redirect loops
- Development-only error logging

### How to Test

#### Test A: Backend Unavailable

1. Start frontend WITHOUT backend
2. Click "Refresh Graph" button (if available)
3. Watch error behavior

**Expected Result**:
- ✅ Error appears within 10 seconds (not 30)
- ✅ User-friendly message: "Backend unavailable. Please check if server is running."
- ✅ No login redirect loops
- ✅ Clean production console (errors logged only in dev mode)

#### Test B: Backend Available

1. Start backend
2. Start frontend
3. Use application normally

**Expected Result**:
- ✅ API calls succeed
- ✅ No timeout errors
- ✅ Data loads from backend
- ✅ Clean console in production

---

## Fix #4: Demo Data Removal

### What Was Fixed
- Removed 200+ lines of hardcoded sample data from App.jsx
- All data now fetched from backend
- Removed mock data from BottomStats.jsx

### How to Test

#### Test A: Empty State

1. Start frontend WITHOUT backend
2. Check graph visualization

**Expected Result**:
- ✅ Graph shows empty state (no fake nodes)
- ✅ Collection history is empty (not mock data)
- ✅ Active tasks list is empty
- ✅ Stats show: 0 nodes, 0 edges

#### Test B: Real Data

1. Start backend with some entities
2. Start frontend
3. Check graph

**Expected Result**:
- ✅ Graph shows REAL entities from database
- ✅ Data comes from backend API
- ✅ No hardcoded sample data visible

**How to Create Test Data**:
```bash
# Using backend API
curl -X POST http://localhost:8000/api/v1/entities \
  -H "Content-Type: application/json" \
  -d '{
    "value": "test-domain.com",
    "type": "DOMAIN",
    "source": "MANUAL",
    "confidence": 0.9
  }'
```

---

## Fix #5: Real API Integration

### What Was Fixed
- `handleStartCollection` now calls `collectionAPI.startCollection()`
- `handleEntityAction` now calls `entityAPI.deleteEntity()`
- `handleRelationshipAction` now calls `relationshipAPI.deleteRelationship()`
- Removed all `setTimeout` simulations

### How to Test

#### Test A: Start Collection

1. Start backend
2. Start frontend
3. Use search form to start collection

**Expected Result**:
- ✅ Collection starts via API
- ✅ Success toast appears
- ✅ Active tasks list updates
- ✅ No `setTimeout` delays (real async API call)

#### Test B: Delete Entity

1. Have some entities in the graph
2. Click on an entity to select it
3. In Right Sidebar, click "Delete"

**Expected Result**:
- ✅ Entity deleted via API
- ✅ Success toast appears
- ✅ Graph refreshes automatically
- ✅ Entity disappears from graph

#### Test C: Delete Relationship

1. Have some edges in the graph
2. Click on an edge to select it
3. In Right Sidebar, click "Delete"

**Expected Result**:
- ✅ Relationship deleted via API
- ✅ Success toast appears
- ✅ Graph refreshes automatically
- ✅ Edge disappears from graph

---

## Fix #6: Backend venv Setup

### What Was Fixed
- Created `setup_venv.sh` script
- Recreates virtual environment for current platform
- Fixes Windows venv issues in WSL/Linux

### How to Test

#### Test A: Fresh venv

```bash
cd backend

# Run setup script
bash setup_venv.sh

# Check venv was created
ls -la venv/bin/python  # Should exist
```

**Expected Result**:
- ✅ Old venv removed
- ✅ New venv created
- ✅ pip is executable: `venv/bin/pip --version`
- ✅ All dependencies installed

#### Test B: Start Backend

```bash
cd backend
source venv/bin/activate
python -m app.main
```

**Expected Result**:
- ✅ Backend starts without errors
- ✅ No import errors
- ✅ Health endpoint responds: `curl http://localhost:8000/health`

---

## Comprehensive Integration Test

### Full Workflow Test

Test the complete application flow:

1. **Start Backend**
   ```bash
   cd backend
   source venv/bin/activate
   python -m app.main
   ```
   Verify: Health check at http://localhost:8000/health

2. **Start Frontend**
   ```bash
   cd frontend
   npm run dev
   ```
   Verify: Opens at http://localhost:5173

3. **Check Initial State**
   - WebSocket connected? ✅
   - Graph loads? ✅
   - No console errors? ✅
   - Performance metrics updating? ✅

4. **Create Test Entity**
   - Click "Add Entity" in sidebar
   - Fill form and submit
   - Verify: Entity appears in graph ✅

5. **Start Collection**
   - Use search form
   - Enter target: "example.com"
   - Click "Start Collection"
   - Verify: Toast appears ✅
   - Verify: Active tasks updates ✅

6. **Delete Entity**
   - Click on entity
   - Click "Delete" in sidebar
   - Verify: Entity disappears ✅
   - Verify: Success toast ✅

7. **Test Error Handling**
   - Stop backend (Ctrl+C)
   - Try to refresh graph
   - Verify: Error message appears in 10 seconds ✅
   - Verify: User-friendly message ✅
   - Start backend again
   - Verify: Error disappears automatically ✅

8. **Test Performance**
   - Add many entities (via API)
   - Watch graph rendering
   - Verify: FPS stays near 60 ✅
   - Verify: No render loop warnings ✅

---

## Expected Metrics After Fixes

### Performance
- **FPS**: Should stay at or near 60
- **Render Time**: Should be < 16ms (60 FPS target)
- **Memory**: Should be stable, no constant increases

### Console
- **Production Build**: Nearly empty (only critical errors)
- **Development Build**: Structured logs, easy to debug
- **No Spam**: No repeated connection attempts

### User Experience
- **Fast Errors**: Failures detected within 10 seconds
- **Clear Messages**: User-friendly error text
- **Graceful Degradation**: App works without backend
- **Real Data**: All data from backend

---

## Troubleshooting Common Issues

### Issue: "venv/bin/pip: cannot execute"

**Cause**: Windows venv corrupted or platform mismatch

**Fix**:
```bash
cd backend
bash setup_venv.sh
source venv/bin/activate
```

### Issue: "Backend unavailable" message

**Cause**: Backend not running

**Fix**:
```bash
# Test backend
curl http://localhost:8000/health

# If fails, start backend
cd backend
source venv/bin/activate
python -m app.main
```

### Issue: Still seeing "maximum update depth exceeded"

**Cause**: Using cached/old code

**Fix**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R)
3. Ensure you're running latest code from `fix-reconvault-repo-audit-and-fix` branch

### Issue: Console full of errors

**Cause**: Running in development mode

**Fix**: Build and run in production mode:
```bash
cd frontend
npm run build
npm run preview
```

Or check if errors are expected in development.

### Issue: WebSocket keeps reconnecting forever

**Cause**: Backend WebSocket endpoint not available

**Fix**:
- Check backend logs for WebSocket errors
- Ensure firewall allows ws:// protocol
- Frontend will stop after 10 attempts

---

## Sign-Off Checklist

After testing all fixes, you should be able to say:

- [x] No "maximum update depth exceeded" warnings
- [x] WebSocket stops after 10 attempts when backend unavailable
- [x] Console is clean (no spam) in production
- [x] API errors are detected within 10 seconds
- [x] Error messages are user-friendly
- [x] No hardcoded demo data in frontend
- [x] All data comes from backend APIs
- [x] CRUD operations call real backend endpoints
- [x] Backend venv works correctly
- [x] Application works end-to-end with backend running
- [x] Application degrades gracefully without backend

---

## Next Steps After Testing

### If All Tests Pass ✅
1. Deploy to staging environment
2. Run full integration test suite
3. Document any edge cases found
4. Plan production deployment

### If Some Tests Fail ❌
1. Document which tests fail
2. Check if backend is running correctly
3. Verify you're on the correct branch
4. Check browser console for additional errors
5. Review fix logs in COMPREHENSIVE_FIXES.md

---

## Contact & Support

For questions or issues:
1. Review this testing guide
2. Check COMPREHENSIVE_FIXES.md for technical details
3. Check FRONTEND_FIXES.md for user-facing documentation
4. Review backend logs: `backend/logs/` (if configured)
5. Check browser DevTools Console

---

**Last Updated**: January 8, 2025
**Status**: Ready for Testing
**Branch**: fix-reconvault-repo-audit-and-fix
