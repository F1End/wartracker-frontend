"""Run this file to kick off streamlit frontend locally on your browser"""

import sys
from os import path

from streamlit.web import cli as stcli

def main():
    sys.argv = ["streamlit", "run", path.join("main.py")]
    sys.exit(stcli.main())

if __name__ == '__main__':
    main()