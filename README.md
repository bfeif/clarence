# clarence
Herein lies the code that powers [checkmymate.co](http://checkmymate.co/), a website that enables you to see how to beat your friends at chess.

## Getting Started
So you want to work on checkmymate? Great! To develop and test locally, all you need to do is clone the project, create a virtual environment, and launch the flask app:

### Clone the project
Run the following command in your terminal:
`git clone https://github.com/bfeif/clarence.git`

### Create a virtual environment
This project encourages the built-in python `venv` tool for managing virtual environments. To create a virtual environment for this project, run the following commands in terminal:
1. `cd path/to/clarence` - Go to the root of the project directory.
2. `python3 -m venv .venv` - Create a virtual environment.
3. `source .venv/bin/activate` - Activate the virtual environment.
4. `pip install -r requirements.txt` - Install all necessary packages to the virtual environment.

### Launch the flask app
With the virtual environment activated, launch the flask app with `flask run`.  
A bunch of text will pop up in your terminal, one of which will say something like `Running on http://127.0.0.1:5000/`. Copy and paste this url to your web-browser.  
Great! Now you have the application running locally, and you should be able to see the changes you make in the code automatically update in your browser!
