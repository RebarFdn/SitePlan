#import ollama

class AiAssistant:
    role:str
    content:str


    def message(self):
        return {
        "role": self.role,
        "content": self.content
    }

    def send_message(self, role:str=None, content:str=None):
        if role and content:
            self.role = role
            self.content = content
            response = ollama.chat(model='llama2', messages=[ self.message() ])

            return response['message']['content']
