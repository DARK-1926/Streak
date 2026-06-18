GrantFlow
==========
A lightweight, fully local web application that guides U.S. small businesses through the SBIR Phase‑I grant preparation process. GrantFlow automatically parses eligibility, generates tailored proposal sections, and tracks deadlines—all without any paid APIs or external services.

Purpose
-------
GrantFlow is designed to help small businesses:
* Quickly determine if they qualify for SBIR Phase‑I funding.
* Draft proposal sections (Background, Objectives, Methodology, etc.) using a local language model.
* Review and refine the draft within the browser.
* Export the final proposal as PDF or Word.
* Track key deadlines and milestones.

Prerequisites
-------------
* **Python 3.11+** – The application is tested on Python 3.11 and 3.12.
* **pip** – Python’s package installer.
* (Optional) **Git** – For cloning the repository.

Installation
------------
1. **Clone the repository**  
   ```bash
   git clone https://github.com/your-username/GrantFlow.git
   cd GrantFlow
   ```

2. **Create a virtual environment**  
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**  
   * On macOS/Linux:  
     ```bash
     source venv/bin/activate
     ```  
   * On Windows:  
     ```cmd
     venv\Scripts\activate
     ```

4. **Install dependencies**  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Download the local LLM weights**  
   GrantFlow uses a lightweight local model (e.g., `llama-7b`).  
   ```bash
   python scripts/download_model.py
   ```

Running the App
---------------
```bash
python app.py
```
The application will start a local Flask server on `http://localhost:5000`. Open this URL in your browser.

Basic Usage
-----------
1. **Enter Business Details** – Provide company name, size, industry, and any existing SBIR experience.
2. **Eligibility Check** – GrantFlow automatically parses the input and tells you if you meet the SBIR Phase‑I criteria.
3. **Draft Proposal** – Click “Generate Proposal”. The local LLM will produce draft sections based on your data.
4. **Review & Edit** – Use the built‑in editor to tweak the language, add figures, or adjust the narrative.
5. **Export** – Once satisfied, export the proposal as PDF or Word for submission.

How it Works
------------
```
User Input (Business Details) → Eligibility Parser → Local LLM (llama.cpp) → Draft Sections
          ↓                                 ↓
      Deadline Tracker                 UI Editor
          ↓                                 ↓
   Export (PDF/Word)                Final Proposal
```

* **Eligibility Parser** – A lightweight Python module that checks size, industry, and funding history against SBIR rules.
* **Local LLM** – The application ships with a small, open‑source language model that runs entirely on your machine via `llama.cpp`. No external API calls are made.
* **UI** – A Flask‑based web interface that serves HTML, CSS, and JavaScript. All assets are loaded locally.
* **Deadline Tracker** – A simple SQLite database stores key dates and sends local notifications (via the browser).

FAQ
---
**Q: Does GrantFlow require an internet connection?**  
A: No. All processing, including the language model inference, happens locally. The only external requirement is the initial download of the model weights.

**Q: How does GrantFlow determine SBIR eligibility?**  
A: The eligibility parser checks the following criteria:
1. Company size (≤ 500 employees).
2. U.S. citizenship or permanent residency.
3. No prior Phase‑I award exceeding $250,000.
4. Industry classification matches SBIR categories.

**Q: Which language model does GrantFlow use?**  
A: By default, GrantFlow uses the open‑source `llama-7b` model via the `llama.cpp` runtime. This model is fully offline and respects data privacy.

**Q: Can I customize the proposal templates?**  
A: Yes. Open `templates/proposal_template.md` and edit the Markdown structure. The app will regenerate sections based on the new template.

**Q: Is my data stored anywhere?**  
A: All data is stored locally in the `data/` directory. No data is sent to external servers.

**Q: What if I need help?**  
A: Open an issue on the GitHub repository or email support@grantflow.io.

License
-------
GrantFlow is released under the MIT License. See `LICENSE` for details.

Acknowledgements
----------------
* OpenAI’s research for inspiration.
* The `llama.cpp` community for the lightweight inference engine.
* Flask for the web framework.

Happy Grant Writing!