# LearnWise - AI Powered Learning Companion

## Overview

LearnWise is an AI-powered educational platform that transforms learning materials into interactive study resources. Users can upload PDF documents and generate summaries, quizzes, and audio content to enhance learning and revision.

The project combines document processing, Optical Character Recognition (OCR), Generative AI, and Text-to-Speech technologies to create a personalized learning experience.

---

## Features

* PDF Upload and Processing
* Text Extraction from PDF Documents
* OCR Support for Scanned Documents
* AI-Based Content Summarization
* Automatic Quiz Generation
* Text-to-Speech Audio Generation
* Interactive Streamlit User Interface

---

## Project Structure

```text
LearnWise/
│
├── tutorapp/
│   └── app.py                 # Main Streamlit application
│
├── models/                    # Contains AI/ML models used in the project
│
├── audio_files/               # Stores generated audio files
│
├── requirements.txt           # Project dependencies
│
└── README.md                  # Project documentation
```

---

## Workflow

1. User uploads a PDF document through the Streamlit interface.
2. The system extracts text from the PDF.
3. OCR is applied when scanned images or non-selectable text are detected.
4. Extracted content is processed using AI models.
5. The application generates:

   * Summaries
   * Quiz Questions
   * Audio Learning Content
6. Results are displayed to the user through the web interface.

---

## Technologies Used

### Programming Language

* Python

### Framework

* Streamlit

### Document Processing

* PyMuPDF

### OCR

* PaddleOCR / OCR Engine

### Artificial Intelligence

* Generative AI
* Natural Language Processing

### Audio Processing

* Text-to-Speech (TTS)

---

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd LearnWise
```

### Create a Virtual Environment

```bash
python -m venv venv
```

### Activate the Virtual Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

Navigate to the project directory and run:

```bash
streamlit run tutorapp/app.py
```

The application will open automatically in your web browser.

---

## Future Enhancements

* Multi-language support
* AI-powered chatbot for document interaction
* Learning progress tracking
* Flashcard generation
* Diagram and image understanding
* Cloud deployment support

---

## Author

Amal Benny
Data Science Enthusiast | Machine Learning | Artificial Intelligence | Python
