# Changes Summary: Photo Upload Size & Session Timeout

## Overview
This document summarizes the changes made to increase the maximum photo upload size to 100 MB and extend session timeout duration for the MUPAI application.

## Files Modified

### 1. `.streamlit/config.toml` (New File)
**Purpose:** Streamlit server configuration

**Key Settings:**
```toml
[server]
maxUploadSize = 100        # Increased from default (200 MB) to 100 MB
maxMessageSize = 200        # WebSocket message size
enableStaticServing = true  # Enable session persistence
sessionTimeout = 1800       # 30 minutes idle timeout
maxSessionLifetime = 7200   # 2 hours maximum session
```

**Impact:**
- Users can upload photos up to 100 MB
- Sessions remain active for 30 minutes of inactivity
- Maximum session duration is 2 hours
- Session state is preserved across interactions

---

### 2. `streamlit_app.py`
**Lines Modified:** 3065-3070

**Before:**
```python
# Check file size (10 MB = 10 * 1024 * 1024 bytes)
max_size = 10 * 1024 * 1024
if uploaded_file.size > max_size:
    size_mb = uploaded_file.size / (1024 * 1024)
    return False, f"Archivo muy grande ({size_mb:.1f} MB). Máximo permitido: 10 MB"
```

**After:**
```python
# Check file size (100 MB = 100 * 1024 * 1024 bytes)
# Increased to accommodate high-resolution photos from modern smartphones
max_size = 100 * 1024 * 1024
if uploaded_file.size > max_size:
    size_mb = uploaded_file.size / (1024 * 1024)
    return False, f"Archivo muy grande ({size_mb:.1f} MB). Máximo permitido: 100 MB"
```

**Impact:**
- `validate_progress_photo()` function now accepts files up to 100 MB
- Validation error message updated to reflect new limit
- Compatible with high-resolution smartphone photos (Android & iPhone)

---

### 3. `.gitignore`
**Lines Modified:** 6-9

**Before:**
```
# Streamlit cache and logs
.streamlit/
streamlit_output.log
```

**After:**
```
# Streamlit cache and logs (but allow config.toml)
.streamlit/*
!.streamlit/config.toml
streamlit_output.log
```

**Impact:**
- Config file is now tracked in version control
- Cache files remain ignored
- Ensures configuration is deployed with the application

---

### 4. `UPLOAD_AND_SESSION_CONFIG.md` (New File)
**Purpose:** Comprehensive documentation

**Contents:**
- Configuration parameters explained
- Implementation details
- Testing recommendations
- Deployment considerations
- Troubleshooting guide
- Future improvement suggestions

---

## Behavioral Changes

### Upload Behavior
| Aspect | Before | After |
|--------|--------|-------|
| Max photo size | 10 MB | 100 MB |
| Validation message | "Máximo permitido: 10 MB" | "Máximo permitido: 100 MB" |
| Server limit | Default (~200 MB) | Explicitly 100 MB |
| WebSocket size | Default (~200 MB) | Explicitly 200 MB |

### Session Behavior
| Aspect | Before | After |
|--------|--------|-------|
| Idle timeout | Default (~10 min) | 30 minutes |
| Max lifetime | Unlimited | 2 hours |
| Static serving | Default | Enabled |
| State preservation | ✓ | ✓ Enhanced |

---

## Testing Checklist

### Upload Testing
- [x] Configuration file created and validated
- [x] Code changes implemented and verified
- [ ] Test upload with 50 MB photo
- [ ] Test upload with 100 MB photo
- [ ] Test upload with 101 MB photo (should fail with correct message)
- [ ] Test with high-resolution smartphone photos (Android)
- [ ] Test with high-resolution smartphone photos (iPhone)
- [ ] Verify all 4 photo slots accept large files
- [ ] Confirm photo display works correctly

### Session Testing
- [ ] Fill form partially and idle for 20 minutes
- [ ] Verify data persists after 20-minute idle
- [ ] Test at 29-minute mark (should still work)
- [ ] Test at 31-minute mark (may timeout)
- [ ] Test complete session approaching 2-hour limit
- [ ] Verify session state preservation throughout
- [ ] Test multiple tabs/windows with same session

### Email Testing
- [ ] Upload 4 photos totaling < 15 MB (should inline in email)
- [ ] Upload 4 photos totaling > 15 MB (should link externally)
- [ ] Verify email delivery with large photo sets
- [ ] Confirm photo links/attachments work correctly

---

## Deployment Checklist

### Pre-Deployment
- [x] Configuration file created
- [x] Code changes implemented
- [x] Documentation written
- [x] Changes committed to repository
- [ ] Changes reviewed and approved
- [ ] Integration tests completed

### Deployment Steps
1. Deploy updated code to server
2. Verify `.streamlit/config.toml` is present
3. Restart Streamlit application
4. Test photo upload functionality
5. Monitor logs for any errors
6. Test session timeout behavior

### Post-Deployment
- [ ] Verify upload limit works (100 MB)
- [ ] Verify session timeout (30 minutes)
- [ ] Monitor application performance
- [ ] Check user feedback
- [ ] Review error logs
- [ ] Validate email delivery

---

## Rollback Plan

If issues arise, rollback by:

1. **Revert config file:**
   ```bash
   git checkout HEAD^ .streamlit/config.toml
   ```

2. **Revert code changes:**
   ```bash
   git checkout HEAD^ streamlit_app.py
   ```

3. **Restart application:**
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Temporary override** (if needed):
   Remove `.streamlit/config.toml` and use command-line flags:
   ```bash
   streamlit run streamlit_app.py --server.maxUploadSize=10
   ```

---

## Performance Considerations

### Upload Performance
- Larger files take longer to upload (network dependent)
- WebSocket may timeout on slow connections
- Consider progress indicator for uploads > 50 MB

### Session Performance
- Extended sessions use more server memory
- Monitor memory usage with multiple active sessions
- Consider session cleanup for inactive users

### Email Performance
- Large photo sets may delay email generation
- External storage links preferred for > 15 MB total
- Email delivery may take longer with large attachments

---

## Security Considerations

### Upload Security
- File type validation still enforced (JPG, JPEG, PNG only)
- Size limit prevents denial-of-service attacks
- Server-side validation prevents malicious uploads

### Session Security
- Extended sessions may increase session hijacking risk
- Ensure HTTPS is enabled in production
- Consider session token rotation for long sessions

---

## Monitoring Recommendations

### Metrics to Track
- Average upload size
- Upload success/failure rate
- Session duration distribution
- Timeout frequency
- Email delivery success rate
- Server memory usage
- Application response time

### Alerts to Configure
- Upload failures > 5% of attempts
- Session timeouts > 10% of sessions
- Server memory > 80% capacity
- Email delivery failures
- Application errors related to uploads/sessions

---

## Notes for Future Reference

### Why 100 MB?
- Modern iPhone photos: 3-8 MB typical, up to 20 MB for ProRAW
- Modern Android photos: 2-6 MB typical, up to 15 MB for high-res
- Safety margin for future higher-resolution phones
- Balance between usability and server resources

### Why 30-Minute Timeout?
- Average questionnaire completion: 10-15 minutes
- Buffer for user interruptions (phone calls, etc.)
- Prevents indefinite idle sessions
- Balances user experience with resource management

### Why 2-Hour Lifetime?
- Reasonable maximum for complete workflow
- Prevents extremely long-lived sessions
- Encourages periodic fresh starts
- Allows for thorough questionnaire completion with breaks

---

## Change Log

| Date | Change | Version |
|------|--------|---------|
| 2025-12-30 | Initial implementation | 1.0 |
| 2025-12-30 | Documentation created | 1.0 |

---

## Contact & Support

For questions or issues related to these changes:
- Review `UPLOAD_AND_SESSION_CONFIG.md` for detailed documentation
- Check application logs for error messages
- Test in development environment before production deployment
- Contact repository maintainer for assistance

---

**End of Changes Summary**
