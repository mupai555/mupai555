#!/usr/bin/env python3
"""
Test to validate progress photos section integration in streamlit_app.py
"""

import sys
import os

# Read the streamlit_app.py file
script_dir = os.path.dirname(os.path.abspath(__file__))
streamlit_app_path = os.path.join(script_dir, "streamlit_app.py")
with open(streamlit_app_path, "r") as f:
    content = f.read()

print("Testing Progress Photos Section Integration...")
print("=" * 60)

all_checks_passed = True

# Check 1: Verify new imports for email attachments
if 'from email.mime.base import MIMEBase' in content:
    print("✓ MIMEBase import added")
else:
    print("✗ MIMEBase import NOT found")
    all_checks_passed = False

if 'from email.mime.image import MIMEImage' in content:
    print("✓ MIMEImage import added")
else:
    print("✗ MIMEImage import NOT found")
    all_checks_passed = False

if 'from email import encoders' in content:
    print("✓ encoders import added")
else:
    print("✗ encoders import NOT found")
    all_checks_passed = False

# Check 2: Verify validate_progress_photo function exists
if 'def validate_progress_photo(uploaded_file):' in content:
    print("✓ validate_progress_photo function defined")
    
    # Check validation logic
    if 'file_extension not in [\'jpg\', \'jpeg\', \'png\']' in content:
        print("  ✓ File format validation (JPG, JPEG, PNG)")
    else:
        print("  ✗ File format validation NOT found")
        all_checks_passed = False
    
    if '100 * 1024 * 1024' in content and 'max_size' in content:
        print("  ✓ File size validation (100 MB)")
    else:
        print("  ✗ File size validation NOT found")
        all_checks_passed = False
else:
    print("✗ validate_progress_photo function NOT found")
    all_checks_passed = False

# Check 3: Verify render_progress_photos_section function exists
if 'def render_progress_photos_section():' in content:
    print("✓ render_progress_photos_section function defined")
    
    # Check for required elements
    if 'Fotografías de Progreso (PNG o JPG)' in content:
        print("  ✓ Section title correct")
    else:
        print("  ✗ Section title NOT found")
        all_checks_passed = False
    
    if 'Sube tus fotos de progreso siguiendo el protocolo' in content:
        print("  ✓ Description text present")
    else:
        print("  ✗ Description text NOT found")
        all_checks_passed = False
    
    if 'front_relaxed' in content and 'side_relaxed_right' in content and 'back_relaxed' in content:
        print("  ✓ All three photo types (front, side, back)")
    else:
        print("  ✗ Not all photo types found")
        all_checks_passed = False
    
    if 'st.file_uploader' in content:
        print("  ✓ File uploader widgets present")
    else:
        print("  ✗ File uploader widgets NOT found")
        all_checks_passed = False
else:
    print("✗ render_progress_photos_section function NOT found")
    all_checks_passed = False

# Check 4: Verify attach_progress_photos_to_email function exists
if 'def attach_progress_photos_to_email(msg, progress_photos):' in content:
    print("✓ attach_progress_photos_to_email function defined")
    
    # Check attachment logic
    if 'PHOTO1_front_relaxed' in content:
        print("  ✓ Photo1 filename format")
    else:
        print("  ✗ Photo1 filename NOT found")
        all_checks_passed = False
    
    if 'PHOTO2_side_relaxed_right' in content:
        print("  ✓ Photo2 filename format")
    else:
        print("  ✗ Photo2 filename NOT found")
        all_checks_passed = False
    
    if 'PHOTO3_back_relaxed' in content:
        print("  ✓ Photo3 filename format")
    else:
        print("  ✗ Photo3 filename NOT found")
        all_checks_passed = False
    
    if 'MIMEImage' in content:
        print("  ✓ Uses MIMEImage for attachments")
    else:
        print("  ✗ MIMEImage NOT used")
        all_checks_passed = False
else:
    print("✗ attach_progress_photos_to_email function NOT found")
    all_checks_passed = False

# Check 5: Verify datos_completos_para_email includes photo validation
if 'Foto 1 - Frontal relajado' in content:
    print("✓ Photo validation in datos_completos_para_email")
    
    if 'Foto 2 - Perfil lateral relajado (derecho)' in content and 'Foto 3 - Posterior relajado' in content:
        print("  ✓ All three photos validated")
    else:
        print("  ✗ Not all photos validated")
        all_checks_passed = False
else:
    print("✗ Photo validation NOT found in datos_completos_para_email")
    all_checks_passed = False

# Check 6: Verify enviar_email_resumen updated
if 'progress_photos=None' in content[content.find('def enviar_email_resumen'):content.find('def enviar_email_resumen')+2000]:
    print("✓ enviar_email_resumen accepts progress_photos parameter")
    
    if 'attach_progress_photos_to_email(msg, progress_photos)' in content:
        print("  ✓ Calls attach_progress_photos_to_email")
    else:
        print("  ✗ Does NOT call attach_progress_photos_to_email")
        all_checks_passed = False
else:
    print("✗ enviar_email_resumen NOT updated")
    all_checks_passed = False

# Check 7: Verify enviar_email_parte2 updated
parte2_start = content.find('def enviar_email_parte2')
if parte2_start != -1:
    parte2_section = content[parte2_start:parte2_start+3000]
    if 'progress_photos=None' in parte2_section:
        print("✓ enviar_email_parte2 accepts progress_photos parameter")
        
        if 'FOTOGRAFÍAS DE PROGRESO' in content:
            print("  ✓ Email body mentions photos")
        else:
            print("  ✗ Email body does NOT mention photos")
            all_checks_passed = False
    else:
        print("✗ enviar_email_parte2 NOT updated")
        all_checks_passed = False
else:
    print("✗ enviar_email_parte2 function NOT found")
    all_checks_passed = False

# Check 8: Verify render_progress_photos_section is called before submission
if 'render_progress_photos_section()' in content:
    print("✓ render_progress_photos_section() is called")
    
    # Verify it's called before the submission button
    render_pos = content.find('render_progress_photos_section()')
    button_pos = content.find('Botón para enviar email')
    if render_pos < button_pos:
        print("  ✓ Called before submission button")
    else:
        print("  ✗ NOT called before submission button")
        all_checks_passed = False
else:
    print("✗ render_progress_photos_section() NOT called")
    all_checks_passed = False

# Check 9: Verify email functions are called with progress_photos
if 'progress_photos = st.session_state.get("progress_photos", {})' in content:
    print("✓ Progress photos retrieved from session_state before email")
else:
    print("✗ Progress photos NOT retrieved from session_state")
    all_checks_passed = False

# Check 10: Verify size warning
if '15' in content and 'MB' in content and 'almacenamiento externo' in content:
    print("✓ 15 MB size limit warning present")
else:
    print("  ℹ 15 MB size limit warning might be present (soft check)")

print()
print("=" * 60)
if all_checks_passed:
    print("✅ ALL CHECKS PASSED - Progress Photos Section properly integrated")
    sys.exit(0)
else:
    print("❌ SOME CHECKS FAILED - Review implementation")
    sys.exit(1)
