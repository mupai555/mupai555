#!/usr/bin/env python3
"""
Test for flow state management and conditional rendering system.

This test validates:
- Flow state initialization and transitions
- Conditional rendering wrapper functions
- Helper function behavior across different phases
"""

import sys


class MockSessionState:
    """Mock session state for testing without Streamlit."""
    
    def __init__(self):
        self.state = {"flow_phase": "intake"}
    
    def get(self, key, default=None):
        return self.state.get(key, default)
    
    def __setattr__(self, name, value):
        if name == "state":
            object.__setattr__(self, name, value)
        else:
            self.state[name] = value
    
    def __getattr__(self, name):
        return self.state.get(name)


# Mock streamlit module
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()


# Create mock streamlit instance
mock_st = MockStreamlit()


def get_flow_phase():
    """Returns the current flow phase from session state."""
    return mock_st.session_state.get("flow_phase", "intake")


def set_flow_phase(phase):
    """Sets the current flow phase in session state."""
    if phase not in ["intake", "review", "final"]:
        raise ValueError(f"Invalid flow phase: {phase}. Must be 'intake', 'review', or 'final'.")
    mock_st.session_state.flow_phase = phase


def should_render_technical():
    """Returns True only in 'final' phase."""
    return get_flow_phase() == "final"


def should_hide_during_intake():
    """Returns True if NOT in 'intake' phase."""
    return get_flow_phase() != "intake"


def render_user_safe(render_func):
    """Wrapper for components that are always safe to show."""
    def wrapper(*args, **kwargs):
        return render_func(*args, **kwargs)
    return wrapper


def render_if_final(render_func):
    """Wrapper for technical components shown only in 'final' phase."""
    def wrapper(*args, **kwargs):
        if get_flow_phase() == "final":
            return render_func(*args, **kwargs)
        return None
    return wrapper


def hide_during_intake(render_func):
    """Wrapper for components hidden only during 'intake' phase."""
    def wrapper(*args, **kwargs):
        if get_flow_phase() != "intake":
            return render_func(*args, **kwargs)
        return None
    return wrapper


class TestFlowStateManagement:
    """Test flow state initialization and transitions."""
    
    def setup_method(self):
        """Reset session state before each test."""
        mock_st.session_state = MockSessionState()
    
    def test_default_flow_phase_is_intake(self):
        """Test that default flow phase is 'intake'."""
        assert get_flow_phase() == "intake"
    
    def test_set_flow_phase_to_review(self):
        """Test setting flow phase to 'review'."""
        set_flow_phase("review")
        assert get_flow_phase() == "review"
    
    def test_set_flow_phase_to_final(self):
        """Test setting flow phase to 'final'."""
        set_flow_phase("final")
        assert get_flow_phase() == "final"
    
    def test_invalid_flow_phase_raises_error(self):
        """Test that invalid flow phase raises ValueError."""
        try:
            set_flow_phase("invalid")
            raise AssertionError("Expected ValueError but none was raised")
        except ValueError as e:
            assert "Invalid flow phase" in str(e)
    
    def test_flow_phase_transitions(self):
        """Test complete flow phase transition sequence."""
        # Start in intake
        assert get_flow_phase() == "intake"
        
        # Transition to review
        set_flow_phase("review")
        assert get_flow_phase() == "review"
        
        # Transition to final
        set_flow_phase("final")
        assert get_flow_phase() == "final"
        
        # Can go back to intake
        set_flow_phase("intake")
        assert get_flow_phase() == "intake"


class TestHelperFunctions:
    """Test helper functions for conditional rendering."""
    
    def setup_method(self):
        """Reset session state before each test."""
        mock_st.session_state = MockSessionState()
    
    def test_should_render_technical_in_intake_phase(self):
        """Test should_render_technical returns False during intake."""
        set_flow_phase("intake")
        assert should_render_technical() is False
    
    def test_should_render_technical_in_review_phase(self):
        """Test should_render_technical returns False during review."""
        set_flow_phase("review")
        assert should_render_technical() is False
    
    def test_should_render_technical_in_final_phase(self):
        """Test should_render_technical returns True during final."""
        set_flow_phase("final")
        assert should_render_technical() is True
    
    def test_should_hide_during_intake_in_intake_phase(self):
        """Test should_hide_during_intake returns False during intake."""
        set_flow_phase("intake")
        assert should_hide_during_intake() is False
    
    def test_should_hide_during_intake_in_review_phase(self):
        """Test should_hide_during_intake returns True during review."""
        set_flow_phase("review")
        assert should_hide_during_intake() is True
    
    def test_should_hide_during_intake_in_final_phase(self):
        """Test should_hide_during_intake returns True during final."""
        set_flow_phase("final")
        assert should_hide_during_intake() is True


class TestConditionalRenderingWrappers:
    """Test wrapper decorators for conditional rendering."""
    
    def setup_method(self):
        """Reset session state before each test."""
        mock_st.session_state = MockSessionState()
    
    def test_render_user_safe_always_renders(self):
        """Test render_user_safe always executes regardless of phase."""
        @render_user_safe
        def test_func():
            return "rendered"
        
        # Test in all phases
        set_flow_phase("intake")
        assert test_func() == "rendered"
        
        set_flow_phase("review")
        assert test_func() == "rendered"
        
        set_flow_phase("final")
        assert test_func() == "rendered"
    
    def test_render_if_final_only_renders_in_final(self):
        """Test render_if_final only executes in final phase."""
        @render_if_final
        def test_func():
            return "technical output"
        
        # Should not render in intake
        set_flow_phase("intake")
        assert test_func() is None
        
        # Should not render in review
        set_flow_phase("review")
        assert test_func() is None
        
        # Should render in final
        set_flow_phase("final")
        assert test_func() == "technical output"
    
    def test_hide_during_intake_hides_only_in_intake(self):
        """Test hide_during_intake only suppresses in intake phase."""
        @hide_during_intake
        def test_func():
            return "intermediate output"
        
        # Should not render in intake
        set_flow_phase("intake")
        assert test_func() is None
        
        # Should render in review
        set_flow_phase("review")
        assert test_func() == "intermediate output"
        
        # Should render in final
        set_flow_phase("final")
        assert test_func() == "intermediate output"
    
    def test_wrapper_with_arguments(self):
        """Test wrappers work with functions that have arguments."""
        @render_if_final
        def calculate_technical(value, multiplier=2):
            return value * multiplier
        
        set_flow_phase("intake")
        assert calculate_technical(5, 3) is None
        
        set_flow_phase("final")
        assert calculate_technical(5, 3) == 15


class TestFallbackBehavior:
    """Test fallback behavior when flow state is undefined."""
    
    def test_undefined_flow_phase_defaults_to_intake(self):
        """Test that undefined flow phase defaults to 'intake'."""
        # Create a fresh session state without flow_phase
        mock_st.session_state = MockSessionState()
        mock_st.session_state.state = {}  # Empty state
        
        # Should default to intake
        assert get_flow_phase() == "intake"
        
        # Technical outputs should not render
        assert should_render_technical() is False
        
        # Intake hiding should not hide
        assert should_hide_during_intake() is False


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def setup_method(self):
        """Reset session state before each test."""
        mock_st.session_state = MockSessionState()
    
    def test_intake_to_final_workflow(self):
        """Test typical workflow from intake to final phase."""
        # User starts at intake - technical details hidden
        assert get_flow_phase() == "intake"
        assert should_render_technical() is False
        
        # User completes intake, clicks "COMENZAR EVALUACIÓN"
        set_flow_phase("final")
        
        # Now technical details should show
        assert should_render_technical() is True
        
        # Verify calculation happens in both phases
        @render_if_final
        def show_ffmi_details():
            return "FFMI: 22.5 (Advanced)"
        
        # Reset to intake
        set_flow_phase("intake")
        result = show_ffmi_details()
        assert result is None  # Not shown during intake
        
        # Move to final
        set_flow_phase("final")
        result = show_ffmi_details()
        assert result == "FFMI: 22.5 (Advanced)"  # Shown in final
    
    def test_calculations_persist_across_phases(self):
        """Test that calculations persist even when display is suppressed."""
        # Note: In the actual implementation, calculations should happen 
        # outside the display wrapper to ensure they always run.
        # This test demonstrates the pattern where calculation and display are separated.
        
        # Simulate calculations that always run
        calculation_results = {}
        
        def calculate_ffmi(mlg, height):
            """Calculation always runs regardless of phase."""
            result = mlg / (height ** 2)
            calculation_results['ffmi'] = result
            return result
        
        # Calculation happens before display wrapper
        set_flow_phase("intake")
        ffmi_value = calculate_ffmi(60, 1.75)
        assert 'ffmi' in calculation_results
        assert calculation_results['ffmi'] > 0
        
        # Display wrapper only affects whether result is shown
        @render_if_final
        def display_ffmi(value):
            return f"FFMI: {value:.2f}"
        
        # Display suppressed in intake
        result = display_ffmi(ffmi_value)
        assert result is None  # Display suppressed
        assert calculation_results['ffmi'] == ffmi_value  # But calculation persists
        
        # Display shown in final
        set_flow_phase("final")
        result = display_ffmi(ffmi_value)
        assert result == f"FFMI: {ffmi_value:.2f}"
        assert calculation_results['ffmi'] == ffmi_value  # Calculation still available


def run_tests():
    """Run all tests and return results."""
    print("Running flow state management tests...")
    
    test_classes = [
        TestFlowStateManagement,
        TestHelperFunctions,
        TestConditionalRenderingWrappers,
        TestFallbackBehavior,
        TestRealWorldScenarios
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}...")
        instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                # Run setup if exists
                if hasattr(instance, 'setup_method'):
                    instance.setup_method()
                
                # Run test
                method = getattr(instance, test_method)
                method()
                
                passed_tests += 1
                print(f"  ✓ {test_method}")
            except Exception as e:
                failed_tests.append((test_class.__name__, test_method, str(e)))
                print(f"  ✗ {test_method}: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"Test Results: {passed_tests}/{total_tests} passed")
    
    if failed_tests:
        print(f"\nFailed tests:")
        for class_name, test_name, error in failed_tests:
            print(f"  - {class_name}.{test_name}: {error}")
        return False
    else:
        print("\n✅ All tests passed!")
        return True


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
