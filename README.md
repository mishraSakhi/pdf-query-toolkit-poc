**PDF Query Toolkit (PoC)**

This project is a proof of concept demonstrating how to query and extract information from PDF files using FastAPI, NLP embeddings, and fuzzy search. It allows you to upload PDFs, process them, and perform intelligent searches over the extracted text.

**Features**

* Extracts and preprocesses text from PDF files
* Uses Sentence Transformers for text embeddings
* Performs similarity-based text search
* Provides a FastAPI backend with REST endpoints
* Optional Ngrok integration for public API access
* Easy to extend with custom tools or APIs

**Project Structure**

pdf-query-toolkit-poc/
│
├── main.py              -> FastAPI entry point
├── preprocess.py        -> PDF text extraction and preprocessing
├── start_ngrok.py       -> Ngrok tunnel setup
├── requirements.txt     -> Dependencies list
├── .gitignore           -> Ignored files and folders
├── README.md            -> Project documentation
└── venv/                -> Virtual environment (excluded from Git)

**Installation**

1. Clone the repository:
   git clone [https://github.com/mishraSakhi/pdf-query-toolkit-poc.git](https://github.com/mishraSakhi/pdf-query-toolkit-poc.git)
   cd pdf-query-toolkit-poc

2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate

3. Install the dependencies:
   pip install -r requirements.txt

**Running the Application**

Start the FastAPI server:
uvicorn main:app --host 0.0.0.0 --port 8000

If using Ngrok for public access:
python3 start_ngrok.py

Then open the API documentation in your browser:
[http://localhost:8000/docs](http://localhost:8000/docs)

or use the Ngrok public URL shown in the terminal.

**Example Usage**

1. Upload or specify a PDF URL.
2. The text is extracted and stored in memory or as embeddings.
3. Send a query such as:
   "What are the payment terms mentioned in the document?"
4. The API returns the closest text match based on semantic similarity.

 **Customization**

You can add your own tools or connect an external API.

* Extend preprocess.py to handle more file types.
* Modify main.py to integrate with OpenAI or LangChain.
* Add custom endpoints to FastAPI.

**Troubleshooting**

* If imports show as unresolved, ensure your virtual environment is activated.
* Large models may require additional memory; use smaller Sentence Transformers models if needed.
* If Ngrok fails, verify your token setup using:
  ngrok config add-authtoken YOUR_TOKEN



