import google.generativeai as genai
import matplotlib.pyplot as plt
import json
import re

# Step 1: Configure your Gemini API key
# Make sure to replace "YOUR_GEMINI_API_KEY" with your actual key
# or preferably load it from an environment variable for security.
# import os
# genai.configure(api_key=os.environ['GEMINI_API_KEY'])
genai.configure(api_key="key here")


# Step 2: Load your transcript from a file
try:
    with open("interview_transcript.txt", "r", encoding="utf8") as file:
        transcript_text = file.read()
except FileNotFoundError:
    print("Error: interview_transcript.txt not found. Please create this file.")
    exit() # Exit if the transcript file is missing

# Step 3: Define a prompt with your requirements
prompt = f"""
Here is the transcript of an interview:
-----------------------------------------
{transcript_text}
-----------------------------------------

Please perform the following analysis and provide the output clearly separated:
1.  **Detailed Summary:** A comprehensive summary of the key points discussed during the interview.
2.  **Performance Analysis:** An evaluation of the interviewee's performance based on metrics like engagement (interaction, listening), clarity (articulation, conciseness), and enthusiasm (passion, interest). Score each metric on a scale of 1-10.
3.  **Chart Data (JSON):** Provide *only* the performance scores in a valid JSON object format like this: {{"engagement": <score>, "clarity": <score>, "enthusiasm": <score>}}. Do not include any text before or after the JSON object itself for this specific part.
4.  **Insights Report:** A brief report highlighting key insights, strengths, and potential areas for improvement observed from the transcript.
"""

# Step 4: Send the prompt to Gemini using the correct method
model_name = "gemini-1.5-flash" # Or "gemini-pro" or other compatible models
model = genai.GenerativeModel(model_name)

# Configure generation parameters (optional but recommended)
generation_config = genai.types.GenerationConfig(
    temperature=0.7,
    max_output_tokens=1500
)

# --- THIS IS THE CORRECTED PART ---
try:
    response = model.generate_content(
        prompt,
        generation_config=generation_config # Pass config here
    )
    # --- Access the result correctly ---
    response_text = response.text
except Exception as e:
    print(f"An error occurred during API call: {e}")
    # Consider inspecting 'response.prompt_feedback' if available
    if hasattr(response, 'prompt_feedback'):
         print(f"Prompt Feedback: {response.prompt_feedback}")
    exit() # Exit if API call fails

# Step 5: Display the model's full response (for debugging initially)
print("--- Full Model Response ---")
print(response_text)
print("---------------------------\n")


# Step 6: Extract JSON chart data from the response using a regular expression
#    Improved regex to find JSON object more reliably, even with surrounding text
json_data = None
# Looks for a structure like: {"key": value, ...} potentially spanning multiple lines
json_match = re.search(r"```json\s*(\{.*?\})\s*```|(\{[\s\S]*?\})", response_text, re.DOTALL | re.MULTILINE)

if json_match:
    # Prioritize the content within ```json ... ``` if found
    json_string = json_match.group(1) or json_match.group(2)
    try:
        # Clean potential artifacts if necessary (though the prompt requests clean JSON)
        cleaned_json_string = json_string.strip()
        json_data = json.loads(cleaned_json_string)
        print("Extracted JSON Data:", json_data) # Print extracted data for verification
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON data: {e}")
        print(f"Attempted to parse: >>>{json_string}<<<") # Show what was attempted
    except Exception as e: # Catch other potential errors
         print(f"An unexpected error occurred during JSON processing: {e}")

else:
     print("Could not find JSON data matching the expected format in the response.")

# Step 7: Generate chart (if valid data is found)
if isinstance(json_data, dict) and all(isinstance(v, (int, float)) for v in json_data.values()):
    metrics = list(json_data.keys())
    scores = list(json_data.values())

    if not metrics or not scores:
        print("JSON data found, but it's empty or invalid for plotting.")
    else:
        plt.figure(figsize=(8, 6))
        plt.bar(metrics, scores, color='skyblue')
        plt.xlabel("Metrics")
        plt.ylabel("Scores (1-10)")
        plt.title("Interview Performance Metrics")
        # Adjust Y limit based on expected score range (1-10)
        plt.ylim(0, 11) # Set Y limit slightly above max expected score (10)

        for i, score in enumerate(scores):
             # Adjust text position slightly for better visibility
            plt.text(i, score + 0.2, str(score), ha='center', va='bottom')

        plt.tight_layout() # Adjust layout to prevent labels overlapping
        plt.show()
else:
    if json_data is not None: # It was parsed but not the expected format
        print("Parsed data is not a valid dictionary for plotting.")
    # The "Could not find JSON data" message is handled above
