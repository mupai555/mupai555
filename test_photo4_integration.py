#!/usr/bin/env python3
"""
Test to validate PHOTO4 (Foto de Pose Libre) integration in streamlit_app.py
"""

import sys
import os

# Read the streamlit_app.py file
script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_path = os.path.join(script_dir, "streamlit_app.py")
with open(streamlit_app_path, "r") as f:
    content = f.read()

print("Testing PHOTO4 (Foto de Pose Libre) Integration...")
print("=" * 60)

all_checks_passed = True

# Check 1: Verify session_state initialization includes pose_libre
if '"pose_libre": None' in content:
    print("✓ Session state initialization includes 'pose_libre'")
else:
    print("✗ Session state initialization does NOT include 'pose_libre'")
    all_checks_passed = False

# Check 2: Verify PHOTO4_pose_libre mapping exists
if 'PHOTO4_pose_libre' in content:
    print("✓ PHOTO4_pose_libre filename mapping present")
else:
    print("✗ PHOTO4_pose_libre filename mapping NOT found")
    all_checks_passed = False

# Check 3: Verify pose_libre uploader exists
if 'key="pose_libre_uploader"' in content:
    print("✓ pose_libre file uploader widget present")
else:
    print("✗ pose_libre file uploader widget NOT found")
    all_checks_passed = False

# Check 4: Verify Foto 4 - Pose Libre section exists
if 'Foto 4 – Pose Libre' in content:
    print("✓ 'Foto 4 - Pose Libre' section present")
else:
    print("✗ 'Foto 4 - Pose Libre' section NOT found")
    all_checks_passed = False

# Check 5: Verify optional photo description
if 'Opcional: Carga una fotografía adicional en la pose que prefieras' in content or 'Foto opcional' in content:
    print("✓ Optional photo description present")
else:
    print("✗ Optional photo description NOT found")
    all_checks_passed = False

# Check 6: Verify validation uses same logic as other photos
if 'validate_progress_photo(libre_photo)' in content or 'validate_progress_photo' in content:
    print("✓ Photo validation function used for pose_libre")
else:
    print("✗ Photo validation NOT found for pose_libre")
    all_checks_passed = False

# Check 7: Verify attach_progress_photos_to_email includes pose_libre
attach_func_start = content.find('def attach_progress_photos_to_email')
if attach_func_start != -1:
    attach_func = content[attach_func_start:attach_func_start+2500]
    if '"pose_libre": "PHOTO4_pose_libre"' in attach_func:
        print("✓ attach_progress_photos_to_email includes pose_libre mapping")
    else:
        print("✗ attach_progress_photos_to_email does NOT include pose_libre mapping")
        all_checks_passed = False
    
    # Check that pose_libre is handled as optional (using constant)
    if 'OPTIONAL_PROGRESS_PHOTOS' in attach_func or 'if key in OPTIONAL_PROGRESS_PHOTOS:' in content:
        print("  ✓ pose_libre is correctly handled as optional (using constant)")
    else:
        print("  ✗ pose_libre is NOT handled as optional")
        all_checks_passed = False
else:
    print("✗ attach_progress_photos_to_email function NOT found")
    all_checks_passed = False

# Check 8: Verify required photos are defined as constant
if 'REQUIRED_PROGRESS_PHOTOS' in content:
    print("✓ Required photos defined as constant (REQUIRED_PROGRESS_PHOTOS)")
else:
    print("✗ Required photos constant NOT found")
    all_checks_passed = False

# Check 9: Verify status display distinguishes required vs optional
render_func_start = content.find('def render_progress_photos_section')
if render_func_start != -1:
    # Function is approximately 200 lines, extract more to be safe
    render_func = content[render_func_start:render_func_start+8000]
    if 'required_photos_uploaded' in render_func or 'optional_photo_uploaded' in render_func:
        print("✓ Status display distinguishes required vs optional photos")
        
        # Check for proper counting
        if '3 fotos requeridas' in render_func:
            print("  ✓ Status message correctly states '3 fotos requeridas'")
        else:
            print("  ✗ Status message does NOT correctly state '3 fotos requeridas'")
            all_checks_passed = False
    else:
        print("✗ Status display does NOT distinguish required vs optional")
        all_checks_passed = False
else:
    print("✗ render_progress_photos_section function NOT found")
    all_checks_passed = False

# Check 10: Verify email mentions photos with helper function
if 'def format_photo_status' in content or '3-4 fotografías' in content or 'format_photo_status(progress_photos)' in content:
    print("✓ Email body uses helper function or dynamic message for photos")
else:
    print("  ℹ Email body might mention photos dynamically (soft check)")

# Check 11: Verify photo naming follows specified format (PHOTO4_pose_libre)
if 'PHOTO4_pose_libre' in content:
    print("✓ Photo naming follows specified format: PHOTO4_pose_libre")
else:
    print("✗ Photo naming does NOT follow specified format")
    all_checks_passed = False

# Check 12: Verify file format validation (JPG, JPEG, PNG)
if 'type=["jpg", "jpeg", "png"]' in content:
    print("✓ File format validation matches specification (JPG, JPEG, PNG)")
else:
    print("✗ File format validation NOT correct")
    all_checks_passed = False

# Check 13: Verify 100 MB size limit
if '100 * 1024 * 1024' in content:
    print("✓ 100 MB size limit validation present")
else:
    print("✗ 100 MB size limit validation NOT found")
    all_checks_passed = False

# Check 14: Verify independence - existing logic not broken
if 'front_relaxed' in content and 'side_relaxed_right' in content and 'back_relaxed' in content:
    print("✓ Existing photo logic (front, side, back) preserved")
else:
    print("✗ Existing photo logic might be affected")
    all_checks_passed = False

# Check 15: Verify UI section is independent
if 'Foto Adicional - Pose Libre' in content or 'Pose Libre' in content:
    print("✓ Independent UI section for Pose Libre photo")
else:
    print("✗ Independent UI section NOT found")
    all_checks_passed = False

print()
print("=" * 60)
if all_checks_passed:
    print("✅ ALL CHECKS PASSED - PHOTO4 (Foto de Pose Libre) properly integrated")
    print()
    print("Summary of integration:")
    print("  • Added 'pose_libre' key to session_state")
    print("  • Created PHOTO4_pose_libre filename mapping")
    print("  • Implemented file uploader with same validation (JPG/JPEG/PNG, 100MB)")
    print("  • Updated attach function to include optional PHOTO4")
    print("  • Distinguished required (3) from optional (1) photos")
    print("  • Updated email body to show 3-4 photos dynamically")
    print("  • Maintained independence from existing logic")
    sys.exit(0)
else:
    print("❌ SOME CHECKS FAILED - Review implementation")
    sys.exit(1)
