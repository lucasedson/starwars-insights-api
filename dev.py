# dev.py
import os
from functions_framework._cli import _cli

def run_dev():
    os.environ["FUNCTION_TARGET"] = "hello_star_wars"
    os.environ["FUNCTION_SOURCE"] = "src/interfaces/handlers.py"
    _cli()

if __name__ == "__main__":
    run_dev()