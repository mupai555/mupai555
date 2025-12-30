# Upload Size and Session Timeout Configuration

This document explains the configuration changes made to support larger photo uploads and extended session timeouts in the MUPAI application.

## Changes Summary

### 1. Photo Upload Size Limit
- **Previous limit:** 10 MB
- **New limit:** 100 MB
- **Reason:** Accommodate high-resolution photos from modern smartphones (Android and iPhone)

### 2. Session Timeout
- **Browser session timeout:** 30 minutes (1800 seconds)
- **Maximum session lifetime:** 2 hours (7200 seconds)
- **Reason:** Ensure users can complete the questionnaire without premature timeouts

## Implementation Details

### Configuration File: `.streamlit/config.toml`
The primary configuration is managed through Streamlit's configuration file:

```toml
[server]
# Maximum file upload size in MB
maxUploadSize = 100

# Maximum WebSocket message size in MB
maxMessageSize = 200

# Session timeout settings
enableStaticServing = true
sessionTimeout = 1800  # 30 minutes
maxSessionLifetime = 7200  # 2 hours
```

### Code Changes in `streamlit_app.py`

#### Photo Validation Function
Updated `validate_progress_photo()` to support 100 MB uploads:

```python
# Line 3065-3070 in streamlit_app.py
# Check file size (100 MB = 100 * 1024 * 1024 bytes)
# Increased to accommodate high-resolution photos from modern smartphones
max_size = 100 * 1024 * 1024
if uploaded_file.size > max_size:
    size_mb = uploaded_file.size / (1024 * 1024)
    return False, f"Archivo muy grande ({size_mb:.1f} MB). Máximo permitido: 100 MB"
```

## Configuration Parameters Explained

### Upload Size Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `maxUploadSize` | 100 MB | Maximum size for file uploads (photos) |
| `maxMessageSize` | 200 MB | Maximum WebSocket message size to handle large uploads |

### Session Timeout Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| `sessionTimeout` | 1800 s (30 min) | Idle timeout - user can remain idle for this duration |
| `maxSessionLifetime` | 7200 s (2 hrs) | Total session duration before forced refresh |
| `enableStaticServing` | true | Enables session persistence |

## Session State Preservation

The application uses Streamlit's `st.session_state` to maintain user data across interactions:

- User inputs are stored in session state variables
- Progress photos are stored in `st.session_state.progress_photos`
- Form data persists within the session lifetime
- State is preserved during idle periods (up to 30 minutes)

## Email Attachment Considerations

**Important:** While uploads can be up to 100 MB, email attachments remain limited to 15 MB due to email server restrictions:

```python
# Line 39 in streamlit_app.py
EMAIL_ATTACHMENT_SIZE_LIMIT_MB = 15
```

When total photo size exceeds 15 MB:
- Photos are uploaded to external storage
- Email includes links to photos instead of inline attachments
- This ensures email delivery reliability

## Testing Recommendations

### Test Upload Functionality
1. Upload photos of various sizes up to 100 MB
2. Verify validation messages display correctly
3. Test with high-resolution smartphone photos
4. Confirm email delivery with large photo sets

### Test Session Behavior
1. Fill form partially and wait 20 minutes idle
2. Verify data is preserved after idle period
3. Test session behavior approaching 2-hour lifetime
4. Confirm smooth user experience without premature logouts

## Deployment Notes

### Production Deployment
- Ensure `.streamlit/config.toml` is deployed with the application
- Verify hosting platform supports 100 MB uploads
- Check hosting platform's session timeout settings
- Monitor application logs for timeout-related issues

### Hosting Platform Considerations
Different hosting platforms may have their own limits:

| Platform | Max Upload | Notes |
|----------|------------|-------|
| Streamlit Cloud | 200 MB | Default, can be configured |
| Heroku | 50 MB | May require config changes |
| AWS/GCP | Configurable | Check load balancer settings |
| Custom Server | As configured | Full control |

## Troubleshooting

### Upload Fails Before 100 MB
- Check hosting platform's upload limits
- Verify reverse proxy/load balancer settings
- Confirm WebSocket message size is adequate

### Session Expires Prematurely
- Check hosting platform's idle timeout settings
- Verify `config.toml` is being loaded
- Review browser console for WebSocket errors

### Photos Not in Email
- Verify total size vs `EMAIL_ATTACHMENT_SIZE_LIMIT_MB`
- Check external storage configuration
- Review email server logs

## Future Improvements

Potential enhancements for consideration:
1. Progressive photo upload with chunk support
2. Image compression before upload (client-side)
3. Cloud storage integration (AWS S3, Google Cloud Storage)
4. Session extension notifications (alert user before timeout)
5. Auto-save functionality for form data

## References

- [Streamlit Configuration Documentation](https://docs.streamlit.io/library/advanced-features/configuration)
- [Streamlit File Uploader Widget](https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
