# Excel to MySQL Uploader

> A lightning-fast, zero-dependency Python web app to import Excel sheets into your MySQL database in seconds.

![App Interface](images/interface.img)

*Refer to the UI screenshot above (located at `images/interface.img`).*

---

## 🧩 Problem It Solves

Importing Excel data into MySQL can be tedious: manual CSV exports, custom scripts, and bulky ETL tools slow you down. This app streamlines the process—connect, upload, and import in one click.

## 🚀 Quick Start

1. **Clone the repo**

   ```bash
   git clone https://github.com/<your-username>/<repo-name>.git
   cd <repo-name>
   ```
2. **Install Python 3.x** (if not already).
3. **Run the app**

   ```bash
   python app.py
   ```
4. **Open** your browser at [http://127.0.0.1:5000](http://127.0.0.1:5000) and verify the interface (see `images/interface.img`).

## 🗂 Project Structure

```plaintext
app.py               # Main Flask application
templates/           # HTML templates
├── index.html       # Connection form
└── upload.html      # Excel upload page
images/              # Assets
└── interface.img    # UI screenshot
```

## 💡 How It Works

1. **Connect**: Enter your MySQL host, port, database, username, and password.
2. **Upload**: Select an `.xls` or `.xlsx` file.
3. **Import**: Rows are ingested directly into the database (table auto-creation supported).

## 👍 Why You’ll Love It

* **Blazing-Fast**: Outperforms MySQL Workbench’s native importer.
* **Zero Dependencies**: Only require Python 3.x.
* **Clean UI**: Simple form-based workflow.
* **Lightweight**: Minimal code, maximal efficiency.

---

*Created by Suman*
