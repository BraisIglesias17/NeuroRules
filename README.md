# NeuroRule

NeuroRule is a desktop application for exploring and analysing small datasets. It combines data preparation, statistical tests, visualisation, conventional machine-learning models, and interpretable neurofuzzy rule generation in one graphical interface.

The project was developed as a master's final project. It is intended for exploratory and educational work rather than high-stakes or production decision-making.

## Main features

With NeuroRule you can:

- Import CSV and Excel (`.xlsx`) datasets or create a dataset manually.
- Inspect and edit data in a spreadsheet-style grid.
- Add, rename, hide, or remove columns and rows.
- Mark columns as identifiers so they are excluded from modelling.
- Find, remove, or replace missing values and outliers.
- Scale numerical variables using Min-Max, quantile, or robust scaling.
- Discretise numerical variables.
- Encode categorical variables using label encoding or one-hot encoding.
- Create histograms, box plots, count plots, correlation and covariance matrices, regression plots, and 2D or 3D plots.
- Produce descriptive summaries.
- Run Shapiro, Pearson, Student's t, ANOVA, Kruskal-Wallis, and Mann-Whitney U tests.
- Train regression and classification models with train/test validation, cross-validation, and optional grid search.
- Generate interpretable neurofuzzy regression rules and decision-tree classification rules.
- Review metrics, make predictions, export reports, and save tasks for later use.

Available prediction algorithms include:

- Linear regression
- Support vector machines
- Random forests
- Multilayer perceptrons
- K-nearest neighbours for classification
- Neurofuzzy models for regression rule generation
- Decision trees for classification rule generation

## Requirements

- Python 3.10 or newer
- A desktop environment supported by wxPython
- Graphviz installed on the operating system if you want to use features that render Graphviz diagrams

The application has primarily been developed and tested on Windows. Installing wxPython may require platform-specific system packages on Linux.

## Installation

Clone or download the repository, open a terminal in its root directory, and create a virtual environment.

On Windows PowerShell:

```powershell
py -3.10 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

On macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If `wxPython` cannot be installed from a wheel, consult the wxPython installation instructions for your operating system and Python version.

## Launching NeuroRule

Run the application from the repository root so its bundled images and help pages can be found:

```bash
python main.py
```

The main NeuroRule window should then open. Closing the window stops the application.

## Basic workflow

1. Select **Import data** and choose a `.csv` or `.xlsx` file. For CSV files, confirm the separator and decimal character. Alternatively, use **Data > Create set** to start manually.
2. Inspect the data grid. Use the column and row context menus to rename, hide, identify, or delete data where necessary.
3. Use **Clean data** to configure missing-value and outlier handling.
4. Use **Transform data** to scale, discretise, or encode variables.
5. Explore the dataset using **Plot**, **Statistics**, and **Summary**.
6. Choose **Prediction Model** to train standard regression or classification algorithms, or **Neurofuzzy Model** to generate readable rules.
7. Select input and target variables, choose models and validation settings, and start training.
8. Open **Results** to inspect validation metrics, model parameters, plots, rules, and predictions.
9. Save the processed dataset or task when you want to continue later.

The **Help** options inside the application provide more detail for individual dialogs and analyses.

## Data and task files

- Input and exported datasets: `.csv` and `.xlsx`
- Text reports: `.txt`
- Saved NeuroRule tasks: `.nrl`

A saved task contains its dataset, preprocessing state, selected models, and results. Task files use Python pickle-based serialization for compatibility with trained scientific-Python objects. The loader restricts the modules that may be reconstructed, but you should still open only `.nrl` files from sources you trust.

Saved tasks may depend on the versions of Python and scientific libraries used to create them. For reproducible work, keep a copy of the environment or dependency versions alongside important results.

## Interpreting results

Model reports can include accuracy, precision, recall, F1 score, R², mean squared error (MSE), root mean squared error (RMSE), and range-normalised RMSE (NRMSE), depending on the task type.

Statistical significance does not by itself establish practical importance or causality. When running many statistical tests, consider applying an appropriate multiple-comparison correction outside NeuroRule. Small datasets also produce uncertain validation estimates, particularly when a target class contains very few observations.

## Project structure

```text
back/                   Data handling, statistics, tasks, and ML models
front/                  wxPython views, plots, settings, and resources
main.py                 Application entry point
requirements.txt        Python dependencies
NeuroRule.spec          PyInstaller configuration
```

## Troubleshooting

- **The window does not open:** run `python main.py` in a terminal and read the displayed traceback.
- **A module is missing:** activate the virtual environment and run `python -m pip install -r requirements.txt` again.
- **CSV columns are parsed incorrectly:** choose the correct separator and decimal character in the import dialog.
- **Cross-validation fails:** reduce the number of folds. It cannot exceed the training sample count or, for classification, the size of the smallest class.
- **A saved task cannot be opened:** use compatible dependency versions and confirm that the file was created by NeuroRule and comes from a trusted source.
- **Resources are missing:** start the program from the repository root, not from `front/` or `back/`.

## Status and limitations

NeuroRule is research software under active development. Before relying on a result, validate it independently and inspect the data, model assumptions, train/test split, and class balance. Contributions that improve tests, documentation, portability, accessibility, and statistical validation are welcome.
