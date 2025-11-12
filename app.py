from flask import Flask, render_template, request
from utils import preprocess_and_save
import pandas as pd
from groq import Groq
import re
import traceback

app = Flask(__name__)

def strip_code_fences(code: str) -> str:
    """Remove markdown code fences and surrounding backticks safely."""
    if not code:
        return code
    # Remove ```python ... ``` or ``` ... ```
    code = re.sub(r"^```(?:python)?\s*", "", code.strip(), flags=re.IGNORECASE)
    code = re.sub(r"\s*```$", "", code.strip(), flags=re.IGNORECASE)
    # Remove single backticks
    code = code.strip("` \n")
    return code

def sanitize_numeric_like_columns(df: pd.DataFrame, min_numeric_ratio: float = 0.5):
    """
    Inspect each column and, if it's mostly numeric-like after cleaning,
    convert it to numeric (coerce errors -> NaN). Return cleaned df and a dict
    of columns that had conversion problems (samples).
    """
    df = df.copy()
    problem_samples = {}
    for col in df.columns:
        # only attempt on object / string columns (avoid touching actual datetimes etc.)
        if pd.api.types.is_numeric_dtype(df[col]) or pd.api.types.is_datetime64_any_dtype(df[col]):
            continue

        # Convert to string, strip, remove common thousands separators and currency symbols
        cleaned = df[col].astype(str).str.strip().str.replace(r"[,\s\$₹€]", "", regex=True)
        # If column contains values like "1.23" or "-45" etc, try numeric conversion
        as_numeric = pd.to_numeric(cleaned.replace(["", "nan", "None", "NoneType"], pd.NA), errors="coerce")

        numeric_ratio = as_numeric.notna().mean()  # fraction of values that converted
        if numeric_ratio >= min_numeric_ratio:
            # Replace column with numeric version (NaN where conversion failed)
            df[col] = as_numeric
            # Save small sample of problematic entries for diagnostics
            bad_idx = df[col].isna()
            if bad_idx.any():
                problem_samples[col] = df.loc[bad_idx, col].head(10).astype(str).tolist()
        # else: leave column as-is (likely categorical or text)
    return df, problem_samples

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    df = None
    df_html = ""
    df_preview_html = ""
    result_html = ""
    code_generated = ""
    conversion_problems = {}

    if request.method == "POST":
        file = request.files.get("file")
        query = request.form.get("query")
        groq_key = request.form.get("api_key")

        if not groq_key:
            message = "Please enter your Groq API key."
        elif file:
            df, cols, df_html, err = preprocess_and_save(file)
            if err:
                message = err
            else:
                # Show first 5 rows preview
                df_preview_html = df.head().to_html(classes="table-auto w-full") if df is not None else ""

                # sanitize numeric-like columns BEFORE executing any model-generated code
                df, conversion_problems = sanitize_numeric_like_columns(df, min_numeric_ratio=0.5)

                if query:
                    try:
                        prompt = f"""
You are a Python data analyst. Given a pandas DataFrame named `df`, write Python code using pandas to answer this question:

Question: {query}

Only return the Python code (no explanation). Use 'result' as the final output variable.
"""

                        client = Groq(api_key=groq_key)
                        chat_completion = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile"
                        )

                        # Extract code and strip fences/backticks
                        raw_content = chat_completion.choices[0].message.content
                        code_generated = strip_code_fences(raw_content)

                        # Prepare safe exec environment (provide pandas and df)
                        exec_globals = {"pd": pd}
                        local_vars = {"df": df}

                        # Execute generated code
                        exec(code_generated, exec_globals, local_vars)

                        result = local_vars.get("result", "No result generated.")
                        if isinstance(result, pd.DataFrame):
                            result_html = result.to_html(classes="table-auto w-full")
                        else:
                            result_html = str(result)

                    except Exception as e:
                        # Capture traceback and give helpful diagnostics
                        tb = traceback.format_exc()
                        # If it's a conversion error, include sample problematic values
                        err_msg = str(e)
                        diagnostics = ""
                        if conversion_problems:
                            diagnostics += "<br><strong>Possible problematic columns and sample bad values (converted to NaN):</strong><br>"
                            for c, samples in conversion_problems.items():
                                diagnostics += f"{c}: {samples}<br>"

                        message = f"Error running Groq code: {err_msg}.<br><pre>{tb}</pre>{diagnostics}"

        else:
            message = "Please upload a file."

    return render_template(
        "index.html",
        message=message,
        df_html=df_html,
        df_preview_html=df_preview_html,
        code_generated=code_generated,
        result_html=result_html,
    )

if __name__ == "__main__":
    app.run(debug=True)
