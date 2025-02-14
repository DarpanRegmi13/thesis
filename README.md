# thesis
This is my final year thesis IncidenceResponseAI rag chatbot.

The Incident Response RAG Chatbot is an AI-powered assistant designed to help financial bank staff in Kathmandu Valley handle cybersecurity incidents efficiently. Utilizing a Retrieval-Augmented Generation (RAG) approach, it combines FAISS (Facebook AI Similarity Search) for document retrieval with a Google Gemini-based chatbot to provide accurate, context-aware responses. It guides users through security incidents like DoS, R2L, U2R, and Probe attacks, offering structured recommendations based on indexed incident response PDFs. The chatbot supports session management, allowing users to save and review past conversations, and enables knowledge expansion by uploading PDFs that are automatically processed and indexed. Designed as a Flask-based web service, it features a user-friendly interface for easy access, presenting information in a clear, structured format. Primarily intended for non-technical bank staff, the chatbot acts as an AI-driven security advisor, ensuring quick, informed decision-making during and after cyber threats.

# Notes:

Static folder contains nids.css.
GOOGLE_API_KEY.txt contains gemini-flash-1.5's api key.
In gemini_rag_for_saving_sessions.py, in line 26 i have hardcoded the location of GOOGLE_API_KEY.txt, change it to the location that you have saved GOOGLE_API_KEY.txt so that you can use it efficiently.
NSL-KDD folder contains dataset used for training and testing LR NIDS model.
pandas_profiling.html contains all figures of NIDS during the training.
