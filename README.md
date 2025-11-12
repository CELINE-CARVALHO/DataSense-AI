# 🧠 AI-Powered Data Analyst (Flask + Groq LLaMA Model)

An intelligent **Flask web application** that allows users to upload CSV files and ask **data analysis questions in natural language**.  
The app automatically cleans the dataset, detects numeric-like columns, and uses **Groq’s LLaMA 3.3 70B model** to generate **Python (pandas) code** that answers the user's query.

---

## 🚀 Features

- 📊 Upload your dataset (CSV or Excel)
- 🤖 Ask natural language questions about your data
- 🧹 Automatic data cleaning and numeric conversion
- 🔍 Auto-detection of numeric-like columns
- 🧠 AI-generated pandas code execution using **Groq API**
- 🪄 Safe code execution with detailed error diagnostics
- 🧾 Preview of uploaded data and final results

---

## 🏗️ Project Structure

├── app.py # Main Flask application
├── utils.py # File preprocessing and saving logic
├── templates/
│ └── index.html # Web interface
├── static/ # (Optional) CSS, JS, images
├── requirements.txt # Python dependencies
└── README.md # Project documentation



## ⚙️ Installation

### 1️⃣ Clone the repository

git clone https://github.com/your-username/ai-data-analyst.git
cd ai-data-analyst
2️⃣ Create a virtual environment
bash
Copy code
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
Example requirements.txt:

text
Copy code
Flask
pandas
groq
🔑 Configuration
You’ll need a Groq API key to use the LLaMA model.
Get one from https://console.groq.com.

The key will be entered directly into the web form on the app interface.

▶️ Run the App
bash
Copy code
python app.py
Then open your browser and go to:

cpp
Copy code
http://127.0.0.1:5000
💡 How It Works
Upload your dataset (e.g., data.csv).

Enter your Groq API Key and query, for example:

"What is the average age by department?"

The app:

Cleans and preprocesses your data

Sends your question to Groq’s LLaMA 3.3-70B model

Receives AI-generated pandas code

Executes the code securely on your dataset

Displays both the code and the output

🧩 Core Functions
sanitize_numeric_like_columns(df)
Automatically converts string-based numeric columns (like "1,234", "₹500") into numeric dtype
and provides samples of conversion errors.

strip_code_fences(code)
Removes Markdown formatting like python or ``` to safely execute AI-generated code.

⚠️ Error Handling
If an error occurs during code execution:

A detailed Python traceback is displayed.

Problematic columns and their invalid samples are listed.

You can modify your dataset or query accordingly.

🧠 Example Query
Question: "Show the top 5 customers with the highest total purchase value."

AI-Generated Code:

python
Copy code
result = df.groupby("Customer")["PurchaseValue"].sum().nlargest(5)
🛠️ Tech Stack
Frontend: HTML + Jinja2 Templates

Backend: Flask

AI Model: Groq LLaMA 3.3 70B

Data Handling: pandas

📌 Future Enhancements
Support for multiple file formats (JSON, Excel, Parquet)

Visualization support (matplotlib/seaborn output)

Enhanced prompt templating for more accurate queries

User authentication for API key management

🧑‍💻 Author
Celine Carvalho
