# EduGPT: AI-Powered Education Assistant

##  Project Overview
EduGPT is an AI-powered educational assistant built using **LangChain, FAISS, ChromaDB, Sentence-Transformers, and Streamlit**.  
It can answer domain-specific questions (Q/A dataset) with **Retrieval-Augmented Generation (RAG)**.  
This project is designed to help students, teachers, and institutions by providing instant answers from structured educational datasets.

---

##  Features
- Retrieval-Augmented Generation (RAG) for accurate responses  
- Context-aware answers using FAISS/Chroma vector store  
- Easy-to-use **Streamlit web app interface**  
- Pre-loaded Q/A dataset for education domain  
- Modular codebase for extension and scaling  

---

## 🛠️ Tech Stack
- **Python 3.10+**
- **OpenAI**
- **LangChain**
- **FAISS / ChromaDB**
- **Sentence-Transformers**
- **Streamlit**
- **Transformers**
- **Torch**

---

## 📂 Project Structure
EduGPT_Project/
│── datasets/ # CSV dataset (Q/A)
│── embeddings/ # FAISS/Chroma vector store
│── app.py # Streamlit app
│── requirements.txt # Project dependencies
│── README.md # Project documentation


---

## ⚙️ Installation & Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/EduGPT_Project.git
   cd EduGPT_Project

2. Install dependencies:

pip install -r requirements.txt 

3. Run the app:

streamlit run app.py

4. Usage

Open the app in your browser

Ask any educational question from the dataset

The AI will retrieve the most relevant context and generate an answer

📸 Screenshots (Optional)

(Add screenshots of your Streamlit app here after running it locally)

🌟 Future Improvements

Add multiple datasets (Maths, Science, Coding, etc.)

Deploy on Streamlit Cloud / Hugging Face Spaces

Add authentication & user profiles

Improve answer generation with fine-tuning

📊 Dataset

The dataset is stored in datasets/EduGPT_Master_QA.csv.
It contains educational Q&A pairs used to train EduGPT for better accuracy.

🌍 Deployment

You can deploy this project on:

Streamlit Cloud
Hugging Face Spaces
Render
AWS / GCP / Azure

🤝 Contribution

Contributions are welcome! 🎉
If you’d like to improve EduGPT, feel free to fork the repo and submit a PR.

👨‍💻 Author

Chanchal Raikwar
 AI/ML | Data Science | GenAI Enthusiast

📬 Contact

 LinkedIn : linkedin.com/in/chanchal-raikwar-430b91256 
 | GitHub : github.com/Chanchalgithu
