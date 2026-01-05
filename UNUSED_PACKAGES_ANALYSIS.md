# Unused Packages Analysis

## Overview

The following packages are listed in `backend/requirements.txt` but are **NOT imported anywhere in the backend codebase**.

**Total Unused Packages:** 4

---

## Unused Packages Details

### 1. aiohttp==3.9.1
```
Category: HTTP Client / Asynchronous
Purpose: Asynchronous HTTP client/server library
Status: NOT IMPORTED
Search Results: No matches found for "import aiohttp|from aiohttp"
```

**Recommendation:**
- **REMOVE** if not planning to use in the near future
- **KEEP** if planned for future async HTTP operations
- If keeping, document the intended use case

**Similar Package Already Used:**
- `httpx==0.26.0` - Already imported in code
- `requests==2.31.0` - Already imported in code

---

### 2. imageio==2.33.1
```
Category: Image Processing / I/O
Purpose: Library for reading and writing image files
Status: NOT IMPORTED
Search Results: No matches found for "import imageio|from imageio"
```

**Recommendation:**
- **REMOVE** if not needed
- **KEEP** if planned for additional image format support

**Similar Packages Already Used:**
- `Pillow==10.1.0` - Image processing (used in media_collector.py)
- `opencv-python==4.8.1.78` - Computer vision (used in media_collector.py)

**Note:** The media_collector.py uses Pillow and OpenCV for image operations, which cover most use cases.

---

### 3. dask==2023.12.0
```
Category: Distributed Computing
Purpose: Parallel computing with task scheduling
Status: NOT IMPORTED
Search Results: No matches found for "import dask|from dask"
```

**Recommendation:**
- **REMOVE** if not using distributed computing
- **KEEP** if planning large-scale data processing

**Similar Packages Used:**
- `pandas==2.1.3` - Data processing (used in multiple files)
- `numpy==1.26.3` - Numerical computing (used in 8 files)

**Note:** Current codebase uses pandas for data processing. Dask would only be needed for:
- Out-of-memory computation
- Distributed computing across clusters
- Parallel processing of very large datasets

---

### 4. pydub==0.25.1
```
Category: Audio Processing
Purpose: Audio file manipulation and processing
Status: NOT IMPORTED
Search Results: No matches found for "import pydub|from pydub"
```

**Recommendation:**
- **REMOVE** if not needed
- **KEEP** if planning advanced audio processing

**Similar Packages Used:**
- `librosa==0.10.0` - Audio analysis (listed but not imported either)

**Note:** The media_collector.py attempts to import `mutagen` for audio metadata but has a try/except block. It doesn't currently do audio manipulation.

---

## Also Listed But Not Imported (May Be Future Use)

### 5. librosa==0.10.0
```
Category: Audio Analysis
Purpose: Music and audio analysis
Status: NOT IMPORTED
Search Results: No matches found for "import librosa|from librosa"
```

**Recommendation:**
- **REVIEW** - Listed but not imported
- May be intended for future audio analysis features
- Currently only used as fallback in media_collector.py (not imported)

---

## Verification Method

To verify these findings, run:

```bash
cd backend

# Search for aiohttp imports
grep -r "import aiohttp\|from aiohttp" app/

# Search for imageio imports
grep -r "import imageio\|from imageio" app/

# Search for dask imports
grep -r "import dask\|from dask" app/

# Search for pydub imports
grep -r "import pydub\|from pydub" app/

# Search for librosa imports
grep -r "import librosa\|from librosa" app/
```

All searches return **NO RESULTS**.

---

## Impact Analysis

### If Removed:
- **No breaking changes** (not used in code)
- **Reduced dependency bloat**
- **Faster pip install** (fewer packages to download)
- **Smaller Docker image**
- **Reduced attack surface** (fewer dependencies)

### If Kept:
- **Potential future use** (must be documented)
- **No immediate impact** (not imported)
- **Maintenance burden** (need to track updates)

---

## Recommendations

### Immediate Action (HIGH PRIORITY)

**REMOVE these packages:**
1. **pydub==0.25.1** - No audio manipulation in code
2. **dask==2023.12.0** - No distributed computing in code

### Review and Decide (MEDIUM PRIORITY)

**REVIEW and document or remove:**
3. **imageio==2.33.1** - Pillow and OpenCV already cover image I/O
4. **aiohttp==3.9.1** - httpx and requests already cover HTTP needs

### Future Planning (LOW PRIORITY)

**KEEP if planned for future features:**
- If keeping, add TODO comments in code where they will be used
- Add to future task tracker
- Document in DEVELOPMENT.md

---

## Proposed Action Plan

### Option 1: Conservative (Keep All)
- Keep all packages for potential future use
- Add documentation to each package's purpose
- Create a FUTURE_DEPENDENCIES.md file
- **Pros:** Ready for future features
- **Cons:** Dependency bloat, maintenance burden

### Option 2: Moderate (Remove Unused) - RECOMMENDED
- Remove definitely unused: pydub, dask
- Review imageio, aiohttp for 1 sprint, then remove if unused
- **Pros:** Clean dependencies, faster installs
- **Cons:** May need to reinstall later

### Option 3: Aggressive (Remove All)
- Remove all 4-5 unused packages
- Reinstall when needed
- **Pros:** Cleanest, smallest Docker image
- **Cons:** May delay future features

---

## Conclusion

**Recommendation: Option 2 - Moderate Cleanup**

Remove immediately:
- pydub==0.25.1
- dask==2023.12.0

Review for 1 sprint:
- imageio==2.33.1
- aiohttp==3.9.1

This balances clean dependencies with flexibility for future development.

---

**Analysis Date:** 2026-01-05
**Analyzer:** cto-new[bot]
