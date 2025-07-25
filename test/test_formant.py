#!/usr/bin/env python3
"""
Test script for the formant_detector module
"""

def test_formant_detector():
    try:
        import formant_detector
        print("✓ Successfully imported formant_detector module")
        
        # Create detector instance
        detector = formant_detector.FormantDetector()
        print("✓ Successfully created FormantDetector instance")
        
        # Test print_devices (should not crash)
        print("\nAvailable audio devices:")
        detector.print_devices()
        
        # Test get_formants (should return [0.0, 0.0] initially)
        formants = detector.get_formants()
        print(f"✓ Initial formants: F1={formants[0]} Hz, F2={formants[1]} Hz")
        
        print("\n✓ All basic tests passed!")
        print("\nTo test real-time detection:")
        print("detector.start_stream()  # Start audio capture")
        print("formants = detector.get_formants()  # Get detected formants")
        print("detector.stop_stream()  # Stop audio capture")
        
    except ImportError as e:
        print(f"✗ Failed to import formant_detector: {e}")
        print("Make sure to install the module first:")
        print("pip install -e .")
    except Exception as e:
        print(f"✗ Error during testing: {e}")

if __name__ == "__main__":
    test_formant_detector()
