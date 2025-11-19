# assistant/commands.py

from assistant.voice import Voice

assistant_voice = Voice()

def process_command(command):
    """
    Process voice/text commands for the Study Assistant.
    """
    command = command.lower()
    
    if "hello" in command or "hi" in command:
        assistant_voice.speak("Hey there! How can I help you today?")
    
    elif "note" in command:
        assistant_voice.speak("Sure! Let's create a note together.")
    
    elif "quiz" in command:
        assistant_voice.speak("Let's test your knowledge with a fun quiz!")
    
    elif "motivate" in command:
        assistant_voice.speak("Believe in yourself! You’re doing amazing!")
    
    else:
        assistant_voice.speak("Sorry, I didn’t quite get that. Can you repeat?")
