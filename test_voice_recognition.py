import speech_recognition as sr

def test_voice_recognition():
    recognizer = sr.Recognizer()
    
    print("Testing voice recognition...")
    print("Please say a chess move when prompted (e.g., 'e2 to e4' or 'Knight to f3')")
    
    with sr.Microphone() as source:
        print("Adjusting for ambient noise... Please wait")
        recognizer.adjust_for_ambient_noise(source, duration=2)
        
        print("Say something now!")
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    
    return None

if __name__ == "__main__":
    test_voice_recognition() 