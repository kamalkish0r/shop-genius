#!/bin/bash

# Step 1: Create a virtual environment
if [[ "$OSTYPE" == "linux-gnu" || "$OSTYPE" == "darwin"* ]]; then
    python3 -m venv env
else
    # For Windows, activate using the appropriate command
    python -m venv env
fi

# Step 2: Activate the virtual environment based on the OS
if [[ "$OSTYPE" == "linux-gnu" || "$OSTYPE" == "darwin"* ]]; then
    source env/bin/activate
else
    # For Windows, activate using the appropriate command
    source env\Scripts\activate
fi

# Step 3: Create a .env file and ask the user to set OPENAI_API_KEY
echo "Please set your OPENAI_API_KEY in the .env file."
echo "You can generate the API key from the OpenAI website at this link: https://platform.openai.com/signup"

# Step 4: Install project requirements
pip install -r requirements.txt

# Step 5: Install Playwright Dependencies
playwright install

echo "Project setup is complete."

# Optionally, you can provide further instructions or start your project here.
