try:
    import fastapi
    import uvicorn
    import pdfplumber
    import pandas
    import numpy
    import google.generativeai
    import groq
    import scipy
    print("SUCCESS: All core packages imported.")
except ImportError as e:
    print(f"FAILED: {e}")
