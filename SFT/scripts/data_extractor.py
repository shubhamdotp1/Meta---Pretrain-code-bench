import nbformat
import json
import os

def extract_notebook_fields_from_path(notebook_path):
    """
    Extracts structured field values from a Jupyter notebook file (.ipynb)
    containing separate Markdown cells with field names and filled-in values.

    Args:
        notebook_path (str): Full path to the notebook file.

    Returns:
        dict: Extracted field-value pairs.
    """
    # ✅ Confirm path exists
    if not os.path.exists(notebook_path):
        print(f"❌ File does not exist:\n{notebook_path}")
        return {}

    print(f"✅ Found notebook file at:\n{notebook_path}")

    # ✅ Read notebook
    with open(notebook_path, "r", encoding="utf-8") as f:
        nb = nbformat.read(f, as_version=4)

    fields = [
        "task_id", "prompt", "canonical_solution", "incorrect_solution",
        "entry_point", "test_setup", "test", "language", "difficulty", "domain", "description"
    ]

    data = {}
    last_field = None

    for cell in nb["cells"]:
        if cell["cell_type"] == "markdown":
            content = cell["source"].strip()
            if content.startswith("### ") and content[4:].strip() in fields:
                last_field = content[4:].strip()
            elif last_field and not content.startswith("# Put"):
                data[last_field] = content.strip()
                last_field = None

    if data:
        print("✅ Extracted JSON:")
        d=json.dumps(data, indent=4)
        print(d)
    else:
        print("⚠️ No filled fields found — did you fill them in yet?")

    return d
