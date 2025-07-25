#!/usr/bin/env python3
"""
Real-time formant detection test
"""
import formant_detector
import time

from sklearn.model_selection import train_test_split

from enum import Enum

deviceInput = 7

class Vowel(Enum):
    A = 1
    E = 2
    I = 3
    O = 4
    U = 5

feature_cols = ['formant1', 'formant2']

def test_realtime_formants():
    print("Starting real-time formant detection...")
    
    detector = formant_detector.FormantDetector()
    
    try:
        # Start audio capture
        detector.start_stream(deviceInput)  # Use device 7 (pulse) for input
        print("Listening for formants... Speak into your microphone!")
        print("Press Ctrl+C to stop")
        
        # Monitor for formants
        for i in range(100):  # Run for about 10 seconds
            formants = detector.get_formants()
            if formants[0] > 0 and formants[1] > 0:  # Valid formants detected
                print(f"F1: {formants[0]:.0f} Hz, F2: {formants[1]:.0f} Hz")
            time.sleep(0.1)  # Check every 100ms
            
    except KeyboardInterrupt:
        print("\nStopping detection...")
    finally:
        detector.stop_stream()
        print("Detection stopped.")

def print_audio_devices():
    """Display available audio input devices"""
    print("\n" + "="*50)
    print("AVAILABLE AUDIO DEVICES")
    print("="*50)
    
    detector = formant_detector.FormantDetector()
    try:
        detector.print_devices()
        print("\nNote: Look for devices with maxInputChannels > 0 for microphone input")
        print(f"Current selected device: {deviceInput}")
        print("Use option 10 to change the audio device")
    except Exception as e:
        print(f"Error getting device list: {e}")

def select_audio_device():
    """Allow user to select their preferred audio input device"""
    global deviceInput
    
    print("\n" + "="*50)
    print("SELECT AUDIO INPUT DEVICE")
    print("="*50)
    
    # First show available devices
    detector = formant_detector.FormantDetector()
    try:
        print("Available devices:")
        detector.print_devices()
        print(f"\nCurrent device: {deviceInput}")
        print("Note: Choose a device with maxInputChannels > 0")
        
        while True:
            try:
                new_device = int(input("\nEnter device number (or -1 to cancel): "))
                
                if new_device == -1:
                    print("Device selection cancelled.")
                    return
                
                if new_device < 0:
                    print("Please enter a valid device number (0 or higher)")
                    continue
                
                # Test if the device works by trying to initialize it
                print(f"Testing device {new_device}...")
                test_detector = formant_detector.FormantDetector()
                test_detector.start_stream(new_device)
                test_detector.stop_stream()
                
                # If we get here, the device works
                deviceInput = new_device
                print(f"✓ Audio input device changed to: {deviceInput}")
                print("This will be used for all future training and recognition.")
                break
                
            except ValueError:
                print("Please enter a valid number!")
            except Exception as e:
                print(f"Error testing device {new_device}: {e}")
                print("Please try a different device number.")
                
    except Exception as e:
        print(f"Error getting device list: {e}")

vowel_a_training_examples = []
vowel_e_training_examples = []
vowel_i_training_examples = []
vowel_o_training_examples = []
vowel_u_training_examples = []


def get_vowel_fornants_training_examples():
    detector = formant_detector.FormantDetector()

    vowel_training_examples = []

    for i in range(50):
        formants = detector.get_formants()
        if formants[0] > 0 and formants[1] > 0:
            vowel_training_examples.append(formants)

    return vowel_training_examples

def train_vowel(vowel_index):
    """Collect training examples for a specific vowel"""
    vowel_names = {1: 'A', 2: 'E', 3: 'I', 4: 'O', 5: 'U'}
    vowel_name = vowel_names.get(vowel_index, 'Unknown')
    
    print(f"Training for vowel: {vowel_name}")
    print("Say the vowel sound repeatedly. Press Ctrl+C when done.")
    
    detector = formant_detector.FormantDetector()
    training_examples = []
    
    try:
        detector.start_stream(deviceInput)
        
        # Collect training data
        while True:
            formants = detector.get_formants()
            if formants[0] > 0 and formants[1] > 0:  # Valid formants
                training_examples.append([formants[0], formants[1]])
                print(f"Collected: F1={formants[0]:.0f} Hz, F2={formants[1]:.0f} Hz (Total: {len(training_examples)})")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print(f"\nFinished training for vowel {vowel_name}. Collected {len(training_examples)} examples.")
    finally:
        detector.stop_stream()
    
    # Store in appropriate global array
    if vowel_index == 1:
        vowel_a_training_examples.extend(training_examples)
    elif vowel_index == 2:
        vowel_e_training_examples.extend(training_examples)
    elif vowel_index == 3:
        vowel_i_training_examples.extend(training_examples)
    elif vowel_index == 4:
        vowel_o_training_examples.extend(training_examples)
    elif vowel_index == 5:
        vowel_u_training_examples.extend(training_examples)
    
    return training_examples

def likelyhood_vowel(formants):
    """Predict the most likely vowel based on formant frequencies"""
    from sklearn.neighbors import KNeighborsClassifier
    import numpy as np
    
    # Collect all training data
    all_training_data = []
    all_labels = []
    
    # Add training examples with labels
    for example in vowel_a_training_examples:
        all_training_data.append(example)
        all_labels.append('A')
    
    for example in vowel_e_training_examples:
        all_training_data.append(example)
        all_labels.append('E')
        
    for example in vowel_i_training_examples:
        all_training_data.append(example)
        all_labels.append('I')
        
    for example in vowel_o_training_examples:
        all_training_data.append(example)
        all_labels.append('O')
        
    for example in vowel_u_training_examples:
        all_training_data.append(example)
        all_labels.append('U')
    
    if len(all_training_data) < 5:
        return "Not enough training data"
    
    # Train classifier
    classifier = KNeighborsClassifier(n_neighbors=3)
    classifier.fit(all_training_data, all_labels)
    
    # Predict
    prediction = classifier.predict([formants])
    probabilities = classifier.predict_proba([formants])
    
    return prediction[0], max(probabilities[0])

def clear_vowel_training_data(vowel_index):
    """Clear training data for a specific vowel"""
    global vowel_a_training_examples, vowel_e_training_examples
    global vowel_i_training_examples, vowel_o_training_examples, vowel_u_training_examples
    
    vowel_names = {1: 'A', 2: 'E', 3: 'I', 4: 'O', 5: 'U', 6: 'ALL'}
    vowel_name = vowel_names.get(vowel_index, 'Unknown')
    
    if vowel_index == 1:
        count = len(vowel_a_training_examples)
        vowel_a_training_examples.clear()
    elif vowel_index == 2:
        count = len(vowel_e_training_examples)
        vowel_e_training_examples.clear()
    elif vowel_index == 3:
        count = len(vowel_i_training_examples)
        vowel_i_training_examples.clear()
    elif vowel_index == 4:
        count = len(vowel_o_training_examples)
        vowel_o_training_examples.clear()
    elif vowel_index == 5:
        count = len(vowel_u_training_examples)
        vowel_u_training_examples.clear()
    elif vowel_index == 6:  # Clear all
        count = (len(vowel_a_training_examples) + len(vowel_e_training_examples) + 
                len(vowel_i_training_examples) + len(vowel_o_training_examples) + 
                len(vowel_u_training_examples))
        vowel_a_training_examples.clear()
        vowel_e_training_examples.clear()
        vowel_i_training_examples.clear()
        vowel_o_training_examples.clear()
        vowel_u_training_examples.clear()
    else:
        print("Invalid vowel index!")
        return
    
    print(f"Cleared {count} training examples for vowel: {vowel_name}")

def save_training_data(filename="vowel_training_data.txt"):
    """Save all training data to a file"""
    import os
    
    # Create app_data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), "app_data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Full path to the file
    filepath = os.path.join(data_dir, filename)
    
    try:
        with open(filepath, 'w') as f:
            f.write("# Vowel Training Data\n")
            f.write("# Format: vowel,f1,f2\n")
            
            for example in vowel_a_training_examples:
                f.write(f"A,{example[0]},{example[1]}\n")
            for example in vowel_e_training_examples:
                f.write(f"E,{example[0]},{example[1]}\n")
            for example in vowel_i_training_examples:
                f.write(f"I,{example[0]},{example[1]}\n")
            for example in vowel_o_training_examples:
                f.write(f"O,{example[0]},{example[1]}\n")
            for example in vowel_u_training_examples:
                f.write(f"U,{example[0]},{example[1]}\n")
        
        total_examples = (len(vowel_a_training_examples) + len(vowel_e_training_examples) + 
                         len(vowel_i_training_examples) + len(vowel_o_training_examples) + 
                         len(vowel_u_training_examples))
        print(f"Saved {total_examples} training examples to {filepath}")
    except Exception as e:
        print(f"Error saving training data: {e}")

def load_training_data(filename="vowel_training_data.txt"):
    """Load training data from a file"""
    import os
    global vowel_a_training_examples, vowel_e_training_examples
    global vowel_i_training_examples, vowel_o_training_examples, vowel_u_training_examples
    
    # Look in app_data directory
    data_dir = os.path.join(os.path.dirname(__file__), "app_data")
    filepath = os.path.join(data_dir, filename)
    
    try:
        # Clear existing data
        clear_vowel_training_data(6)  # Clear all
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    continue
                
                parts = line.split(',')
                if len(parts) == 3:
                    vowel, f1, f2 = parts[0], float(parts[1]), float(parts[2])
                    
                    if vowel == 'A':
                        vowel_a_training_examples.append([f1, f2])
                    elif vowel == 'E':
                        vowel_e_training_examples.append([f1, f2])
                    elif vowel == 'I':
                        vowel_i_training_examples.append([f1, f2])
                    elif vowel == 'O':
                        vowel_o_training_examples.append([f1, f2])
                    elif vowel == 'U':
                        vowel_u_training_examples.append([f1, f2])
        
        total_examples = (len(vowel_a_training_examples) + len(vowel_e_training_examples) + 
                         len(vowel_i_training_examples) + len(vowel_o_training_examples) + 
                         len(vowel_u_training_examples))
        print(f"Loaded {total_examples} training examples from {filepath}")
        
    except FileNotFoundError:
        print(f"Training data file {filepath} not found.")
        print(f"Note: Files are stored in the 'app_data' directory")
    except Exception as e:
        print(f"Error loading training data: {e}")

def list_saved_training_data():
    """List all saved training data files"""
    import os
    
    data_dir = os.path.join(os.path.dirname(__file__), "app_data")
    
    if not os.path.exists(data_dir):
        print("No app_data directory found. No saved training data files.")
        return
    
    try:
        files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
        
        if not files:
            print("No training data files found in app_data directory.")
        else:
            print("\n" + "="*50)
            print("SAVED TRAINING DATA FILES")
            print("="*50)
            
            for i, filename in enumerate(files, 1):
                filepath = os.path.join(data_dir, filename)
                try:
                    # Get file size and modification time
                    stat = os.stat(filepath)
                    size_kb = stat.st_size / 1024
                    import time
                    mod_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(stat.st_mtime))
                    
                    # Try to count lines quickly
                    with open(filepath, 'r') as f:
                        line_count = sum(1 for line in f if line.strip() and not line.startswith('#'))
                    
                    print(f"{i:2d}. {filename}")
                    print(f"     Size: {size_kb:.1f} KB | Examples: ~{line_count} | Modified: {mod_time}")
                    
                except Exception as e:
                    print(f"{i:2d}. {filename} (error reading details: {e})")
            
            print(f"\nFiles are stored in: {data_dir}")
            
    except Exception as e:
        print(f"Error listing files: {e}")

def test_model_accuracy():
    """Test the accuracy of the current model using cross-validation"""
    from sklearn.model_selection import cross_val_score
    from sklearn.neighbors import KNeighborsClassifier
    import numpy as np
    
    # Collect all training data
    all_training_data = []
    all_labels = []
    
    vowel_counts = {}
    
    for example in vowel_a_training_examples:
        all_training_data.append(example)
        all_labels.append('A')
    vowel_counts['A'] = len(vowel_a_training_examples)
    
    for example in vowel_e_training_examples:
        all_training_data.append(example)
        all_labels.append('E')
    vowel_counts['E'] = len(vowel_e_training_examples)
        
    for example in vowel_i_training_examples:
        all_training_data.append(example)
        all_labels.append('I')
    vowel_counts['I'] = len(vowel_i_training_examples)
        
    for example in vowel_o_training_examples:
        all_training_data.append(example)
        all_labels.append('O')
    vowel_counts['O'] = len(vowel_o_training_examples)
        
    for example in vowel_u_training_examples:
        all_training_data.append(example)
        all_labels.append('U')
    vowel_counts['U'] = len(vowel_u_training_examples)
    
    if len(all_training_data) < 15:
        print("Need at least 15 total examples for accuracy testing!")
        return
    
    print("\n" + "="*50)
    print("MODEL ACCURACY ANALYSIS")
    print("="*50)
    
    print("Training Data Summary:")
    for vowel, count in vowel_counts.items():
        if count > 0:
            print(f"  {vowel}: {count} examples")
    print(f"  Total: {len(all_training_data)} examples")
    
    # Test with different K values
    print("\nAccuracy with different K values:")
    for k in [1, 3, 5, 7]:
        if k < len(all_training_data):
            classifier = KNeighborsClassifier(n_neighbors=k)
            try:
                # 5-fold cross validation
                scores = cross_val_score(classifier, all_training_data, all_labels, cv=min(5, len(all_training_data)//2))
                avg_accuracy = scores.mean()
                std_accuracy = scores.std()
                print(f"  K={k}: {avg_accuracy:.1%} (+/- {std_accuracy*2:.1%})")
            except Exception as e:
                print(f"  K={k}: Could not test ({e})")
    
    # Recommendations
    print("\nRecommendations:")
    min_per_vowel = min([count for count in vowel_counts.values() if count > 0])
    max_per_vowel = max([count for count in vowel_counts.values() if count > 0])
    
    if min_per_vowel < 20:
        print(f"  • Collect more examples for vowels with < 20 examples")
        print(f"  • Target: 30-50 examples per vowel for good accuracy")
    elif min_per_vowel < 50:
        print(f"  • You have a good start! Consider collecting 50+ examples per vowel")
        print(f"  • Expected accuracy: 75-85%")
    else:
        print(f"  • Excellent training data! You should see 85-95% accuracy")
        print(f"  • Diminishing returns beyond 100 examples per vowel")
    
    # Balance check
    if max_per_vowel > min_per_vowel * 3:
        print(f"  • Dataset is unbalanced - some vowels have many more examples")
        print(f"  • Consider training more examples for under-represented vowels")



def realtime_vowel_prediction():
    print("Starting realtime vowel prediction")
    
    # Check if we have training data
    total_training = (len(vowel_a_training_examples) + len(vowel_e_training_examples) + 
                     len(vowel_i_training_examples) + len(vowel_o_training_examples) + 
                     len(vowel_u_training_examples))
    
    if total_training < 10:
        print("Not enough training data! Please train some vowels first.")
        return

    detector = formant_detector.FormantDetector()

    try:
        # Start audio capture
        detector.start_stream(deviceInput)
        print("Listening for vowels... Speak into your microphone!")
        print("Press Ctrl+C to stop")
        
        # Monitor for formants and predict vowels
        for i in range(100):
            formants = detector.get_formants()
            if formants[0] > 0 and formants[1] > 0:  # Valid formants detected
                try:
                    predicted_vowel, confidence = likelyhood_vowel(formants)
                    print(f"F1: {formants[0]:.0f} Hz, F2: {formants[1]:.0f} Hz -> Vowel: {predicted_vowel} (confidence: {confidence:.2f})")
                except Exception as e:
                    print(f"F1: {formants[0]:.0f} Hz, F2: {formants[1]:.0f} Hz -> Prediction error: {e}")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nStopping prediction...")
    finally:
        detector.stop_stream()
        print("Prediction stopped.")


def main():
    """Main program loop"""
    exit_var = False

    print("\n" + "="*60)
    print("Welcome to the Vowel Recognition Training Program")
    print("="*60)

    while not exit_var:
        print("\n" + "="*60)
        print("Welcome to the Vowel Recognition Training Program")
        print("="*60)
        print("TRAINING OPTIONS:")
        print("1. Train for vowel: A")
        print("2. Train for vowel: E") 
        print("3. Train for vowel: I")
        print("4. Train for vowel: O")
        print("5. Train for vowel: U")
        print("\nRECOGNITION & TESTING:")
        print("6. Run the vowel Recognition module")
        print("7. Test basic formant detection")
        print("8. Test model accuracy")
        print("9. Show available audio devices")
        print("10. Select audio input device")
        print("\nDATA MANAGEMENT:")
        print("11. Clear training data for specific vowel")
        print("12. Clear ALL training data")
        print("13. Save training data to file")
        print("14. Load training data from file")
        print("15. List saved training data files")
        print("\n16. Exit")
        
        print("\nTraining data collected:")
        print(f"  A: {len(vowel_a_training_examples)} examples")
        print(f"  E: {len(vowel_e_training_examples)} examples")
        print(f"  I: {len(vowel_i_training_examples)} examples")
        print(f"  O: {len(vowel_o_training_examples)} examples")
        print(f"  U: {len(vowel_u_training_examples)} examples")
        total_examples = (len(vowel_a_training_examples) + len(vowel_e_training_examples) + 
                         len(vowel_i_training_examples) + len(vowel_o_training_examples) + 
                         len(vowel_u_training_examples))
        print(f"  Total: {total_examples} examples")
        
        try:
            user_input = int(input("\nEnter your choice: "))
            
            if user_input < 1 or user_input > 16:
                print("Please specify a valid index (1-16)! Try again.")
            elif 1 <= user_input <= 5:
                train_vowel(user_input)
            elif user_input == 6:
                realtime_vowel_prediction()
            elif user_input == 7:
                test_realtime_formants()
            elif user_input == 8:
                test_model_accuracy()
            elif user_input == 9:
                print_audio_devices()
            elif user_input == 10:
                select_audio_device()
            elif user_input == 11:
                print("\nClear training data for:")
                print("1. A  2. E  3. I  4. O  5. U")
                vowel_choice = int(input("Which vowel? "))
                if 1 <= vowel_choice <= 5:
                    clear_vowel_training_data(vowel_choice)
                else:
                    print("Invalid choice!")
            elif user_input == 12:
                confirm = input("Are you sure you want to clear ALL training data? (yes/no): ")
                if confirm.lower() in ['yes', 'y']:
                    clear_vowel_training_data(6)  # Clear all
                else:
                    print("Cancelled.")
            elif user_input == 13:
                filename = input("Enter filename (or press Enter for default): ").strip()
                if not filename:
                    save_training_data()
                else:
                    save_training_data(filename)
            elif user_input == 14:
                filename = input("Enter filename (or press Enter for default): ").strip()
                if not filename:
                    load_training_data()
                else:
                    load_training_data(filename)
            elif user_input == 15:
                list_saved_training_data()
            elif user_input == 16:
                print("Goodbye!")
                exit_var = True
                
        except ValueError:
            print("Please enter a valid number!")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit_var = True

if __name__ == "__main__":
    main()