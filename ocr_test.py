import ollama_client
import base64

# Encode the image to base64
with open('assets/captcha.png', 'rb') as img_file:
    image_bytes = img_file.read()
    encoded_image = base64.b64encode(image_bytes).decode('utf-8')

# Send the image to the vision model
response = ollama.chat(
    model='llama3.2-vision:11b',
    messages=[
        {
            'role': 'user',
            'content': 'What is the captcha code in this image? Return only the code with no special characters',
            'images': [encoded_image],
        }
    ]
)

# Print the response text
print(response)
print(response['message']['content'])
