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

# Step 3: Install project requirements
pip install -r requirements.txt

# Step 4: Install Playwright Dependencies
playwright install


# Step 5: Create a .env file and ask the user to set OPENAI_API_KEY
echo -e "\n\n\nNow let's your OPENAI_API_KEY in the .env file."
echo "You can generate the API key from the OpenAI website at this link: https://platform.openai.com/account/api-keys"
touch .env

# Ask the user to enter the OPENAI_API_KEY
read -p "Please enter your OPENAI_API_KEY: " OPENAI_API_KEY

# Write the OPENAI_API_KEY to the .env file
echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> .env

echo "Project setup is complete!!"
echo -e "\nYou can starting shopping buy running the bot.py"
