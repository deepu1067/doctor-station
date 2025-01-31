from groq import Groq
import json
GROQ_API = "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"
import json

def res(heart_rate, temperature, prblm):
    return (
        "I have measured my vitals using sensors: "
        f"Heart rate: {heart_rate} bpm (using MAX30102 sensor). "
        f"Body temperature: {temperature}°F (using MLX90614 sensor). "
        f"Additionally, {prblm}. "
        "Based on this data, provide a response in the following fixed JSON format:\n"
        "{\n"
        '    "Analysis": "Brief analysis of the condition based on the provided vitals.",\n'
        '    "Recommendation": "Recommended actions or advice based on the condition.",\n'
        '    "Medicine": "Name of the medicine and dosage if required. Ensure the medicine is commonly available in Bangladesh."\n'
        "}\n\n"
        "Ensure the response is concise, medically appropriate, and formatted exactly as specified."
    )

client = Groq(
    api_key=GROQ_API,
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": res(95, 94, "I am experiencing mild headache, having itching on my skin which is unbearable"),
        }
    ],
    model="llama-3.3-70b-versatile",
)

response = chat_completion.choices[0].message.content

def get_medicine(response):
    return (
        "From the following response:\n\n"
        f"{response}\n\n"
        "Based on this data, provide a response in the following fixed JSON format:\n"
        "{\n"
        '    "Medicines": [\n'
        '        {\n'
        '            "Name": "Medicine name",\n'
        '            "Dosage": "How to take the medicine"\n'
        '        }\n'
        '    ]\n'
        "}\n\n"
        "Ensure the response is concise and formatted exactly as specified."
    )

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": get_medicine(response),
        }
    ],
    model="llama-3.3-70b-versatile",
)

medicine = chat_completion.choices[0].message.content

# Save the responses to a JSON file
data = {
    "response": response.strip(),
    "medicine": medicine.strip()
}


response_data = json.loads(data["response"])

# Clean the 'medicine' string to parse as JSON
medicine_data = json.loads(data["medicine"])

# Create the cleaned JSON object
cleaned_data = {
    "Analysis": response_data["Analysis"],
    "Recommendation": response_data["Recommendation"],
    "Medicines": [
        {"name": medicine["Name"], "Dosage": medicine["Dosage"]}
        for medicine in medicine_data["Medicines"]
    ]
}

# Save the cleaned data to a new JSON file
with open("cleaned_response_and_medicine.json", "w") as outfile:
    json.dump(cleaned_data, outfile, indent=4)