import csv
import os
import google.generativeai as genai

class KidsInteractiveChatbot:
    def __init__(self):
        # Initialize Google API
        self.GOOGLE_API_KEY = ''  # Replace with your actual API key
        
        # Initialize Gemini
        genai.configure(api_key=self.GOOGLE_API_KEY)
        self.gmodel = genai.GenerativeModel('gemini-1.5-flash')
        
        # CSV configuration
        self.csv_file = "student_responses.csv"
        self.required_fields = [
            "Student ID", "Favorite Movie", "Favorite Color", 
            "Hobby", "Pet Type", "Sport", "Personality Trait"
        ]
        
        # Initialize CSV if it doesn't exist
        self.initialize_csv()
        
        # Conversation history
        self.conversation_history = []

        # Predefined question list
        self.question_list = [
            "What is your student ID?",
            "What is your favorite movie?",
            "What is your favorite color?",
            "What is your favorite hobby?",
            "Do you have any pets? If so, what type?",
            "What is your favorite sport?",
            "How would you describe your personality in one word?"
        ]
        self.current_question_index = 0

    def initialize_csv(self):
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.required_fields)

    def have_natural_conversation(self):
        initial_prompt = f"""
        You are speaking with a young student (grades 1-2) for a quick chat.
        The goal is to gather the following information in the given order:
        1. Student ID
        2. Favorite movie
        3. Favorite color
        4. Favorite hobby
        5. Pets (if any)
        6. Favorite sport
        7. Personality trait
        
        **You must only ask these questions in the specified order, one at a time. Do not ask for any additional information.**
        
        Always acknowledge the student's answer positively before asking the next question.
        Start by greeting the student and ask for their Student ID first. Wait for their answer before asking the next question.
        """

        # Get initial response from Gemini
        response = self.gmodel.generate_content(initial_prompt)
        print(f"Bot: {response.text}")
        
        # Main conversation loop
        while self.current_question_index < len(self.question_list):
            # Get student input
            user_input = input("Student: ")
            
            # Add to conversation history
            self.conversation_history.append(user_input)
            
            # Update prompt with conversation context
            conversation_prompt = f"""
            You are currently chatting with a student. Here is the conversation so far:
            {self._format_conversation_history()}
            
            Acknowledge the student's last answer positively and then ask the next question from the predefined list:
            {self.question_list}

            Only ask the questions in the given order. The current question should be:
            "{self.question_list[self.current_question_index]}"
            """

            try:
                # Get response from Gemini
                response = self.gmodel.generate_content(conversation_prompt)
                bot_response = response.text.strip()
                
                # Add to conversation history
                self.conversation_history.append(bot_response)
                
                print(f"Bot: {bot_response}")
                
                # Move to the next question
                self.current_question_index += 1
                
                # Check if we should end the conversation
                if self.current_question_index >= len(self.question_list):
                    print("Bot: Thank you for chatting! Goodbye!")
                    break
            except Exception as e:
                print(f"Error in generating response: {e}")
                break

        return self.conversation_history

    def extract_information(self):
        """Extract required information from the conversation history"""
        extraction_prompt = f"""
        Review this conversation and extract the following information in a structured format.
        If any information is missing or unclear, use "Unknown".
        
        Conversation:
        {self._format_conversation_history()}
        
        Extract and format these details:
        - Student ID: (number only)
        - Favorite Movie: (movie title only)
        - Favorite Color: (single color only)
        - Hobby: (single main hobby only)
        - Pet Type: (type of pet or "None")
        - Sport: (single sport or "None")
        - Personality Trait: (single trait based on conversation)
        
        Return the information in this exact format (including the brackets):
        [Student ID],[Movie],[Color],[Hobby],[Pet],[Sport],[Trait]
        """
        
        try:
            # Get structured response from Gemini
            response = self.gmodel.generate_content(extraction_prompt)
            # Split the response into fields
            fields = response.text.strip().split(',')
            return fields
        except Exception as e:
            print(f"Error extracting information: {e}")
            return ["Unknown"] * len(self.required_fields)

    def save_to_csv(self, extracted_info):
        """Save the extracted information to CSV file"""
        try:
            with open(self.csv_file, 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(extracted_info)
            print("Information successfully saved to CSV!")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    def _format_conversation_history(self):
        """Format conversation history for Gemini prompt"""
        return "\n".join([
            f"Student: {response}" if idx % 2 == 0 else f"Bot: {response}"
            for idx, response in enumerate(self.conversation_history)
        ])

    def run_session(self):
        """Run a complete session with the student"""
        print("Starting conversation...")
        
        # Have the natural conversation
        self.have_natural_conversation()
        
        # Extract information
        extracted_info = self.extract_information()
        
        # Save to CSV
        self.save_to_csv(extracted_info)
        
        print("Session completed!")

if __name__ == "__main__":
    chatbot = KidsInteractiveChatbot()
    chatbot.run_session()
