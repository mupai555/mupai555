#!/usr/bin/env python3
"""
Integration test for photo upload functionality in streamlit_app
"""

import sys
import os

# Test that all required imports are available
def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing Imports")
    print("=" * 50)
    
    try:
        from PIL import Image
        print("✅ PIL (Pillow) imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PIL: {e}")
        return False
    
    try:
        from io import BytesIO
        print("✅ BytesIO imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import BytesIO: {e}")
        return False
    
    try:
        import base64
        print("✅ base64 imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import base64: {e}")
        return False
    
    return True

def test_function_definitions():
    """Test that photo-related functions are defined in streamlit_app"""
    print("\n🧪 Testing Function Definitions")
    print("=" * 50)
    
    # Read the streamlit_app.py file
    with open('/home/runner/work/mupai555/mupai555/streamlit_app.py', 'r') as f:
        content = f.read()
    
    required_functions = [
        'validate_photo_format',
        'validate_photo_count',
        'process_uploaded_photo',
        'initialize_photos_session_state',
        'get_photo_count'
    ]
    
    all_found = True
    for func_name in required_functions:
        if f"def {func_name}(" in content:
            print(f"✅ Function '{func_name}' found")
        else:
            print(f"❌ Function '{func_name}' not found")
            all_found = False
    
    return all_found

def test_photo_section_in_ui():
    """Test that the photo upload section is present in the UI"""
    print("\n🧪 Testing UI Photo Section")
    print("=" * 50)
    
    with open('/home/runner/work/mupai555/mupai555/streamlit_app.py', 'r') as f:
        content = f.read()
    
    ui_elements = [
        'Fotografías de progreso – Composición corporal',
        'fotos_evaluacion',
        'fotos_metadata',
        'st.file_uploader',
        'Vista Frontal',
        'Vista Posterior',
        'Lateral Izquierda',
        'Lateral Derecha',
        'Ángulo Libre'
    ]
    
    all_found = True
    for element in ui_elements:
        if element in content:
            print(f"✅ UI element '{element}' found")
        else:
            print(f"❌ UI element '{element}' not found")
            all_found = False
    
    return all_found

def test_email_integration():
    """Test that photo information is added to email reports"""
    print("\n🧪 Testing Email Integration")
    print("=" * 50)
    
    with open('/home/runner/work/mupai555/mupai555/streamlit_app.py', 'r') as f:
        content = f.read()
    
    email_elements = [
        'FOTOGRAFÍAS DE PROGRESO - COMPOSICIÓN CORPORAL',
        'Total de fotografías subidas',
        'get_photo_count()'
    ]
    
    all_found = True
    for element in email_elements:
        if element in content:
            print(f"✅ Email element '{element}' found")
        else:
            print(f"❌ Email element '{element}' not found")
            all_found = False
    
    return all_found

def test_session_state_structure():
    """Test that session state structure is properly defined"""
    print("\n🧪 Testing Session State Structure")
    print("=" * 50)
    
    with open('/home/runner/work/mupai555/mupai555/streamlit_app.py', 'r') as f:
        content = f.read()
    
    # Check for proper photo categories
    photo_categories = [
        'frontal',
        'posterior',
        'lateral_izquierda',
        'lateral_derecha',
        'libre_1',
        'libre_2'
    ]
    
    all_found = True
    for category in photo_categories:
        if f'"{category}"' in content:
            print(f"✅ Photo category '{category}' found")
        else:
            print(f"❌ Photo category '{category}' not found")
            all_found = False
    
    return all_found

def test_validation_logic():
    """Test validation logic for photos"""
    print("\n🧪 Testing Validation Logic")
    print("=" * 50)
    
    with open('/home/runner/work/mupai555/mupai555/streamlit_app.py', 'r') as f:
        content = f.read()
    
    validation_checks = [
        'max_photos = 6',
        'valid_extensions = [\'png\', \'jpg\', \'jpeg\']',
        'image/png',
        'image/jpeg',
        'current_photo_count >= max_photos'
    ]
    
    all_found = True
    for check in validation_checks:
        if check in content:
            print(f"✅ Validation check '{check}' found")
        else:
            print(f"❌ Validation check '{check}' not found")
            all_found = False
    
    return all_found

def main():
    """Run all integration tests"""
    print("\n" + "=" * 50)
    print("🚀 PHOTO UPLOAD INTEGRATION TESTS")
    print("=" * 50 + "\n")
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Function Definitions", test_function_definitions()))
    results.append(("UI Photo Section", test_photo_section_in_ui()))
    results.append(("Email Integration", test_email_integration()))
    results.append(("Session State Structure", test_session_state_structure()))
    results.append(("Validation Logic", test_validation_logic()))
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n🎉 All integration tests PASSED!")
        return 0
    else:
        print("\n⚠️ Some tests FAILED. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
