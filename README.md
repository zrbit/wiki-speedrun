# Overview
**Wiki Speedrun** is a challenge where you navigate from one Wikipedia article to another in the fewest clicks possible.

---

# Features

### 1. Streamlit UI
A Streamlit-based interface where you can randomly select a difficulty level, start playing, and compare your performance with different algorithms.

### 2. Traversal Algorithms
- **Naive Traversal:** Randomly clicks links. Stops if the target is found or if 40 hops are reached.  
- **Embedding Traversal:** Uses semantic similarity to select the link most similar to the target page title. Limited to 40 hops.  
- **Improved Embedding Traversal:** Utilizes two different embedding models, averages their similarity scores, and selects the most semantically relevant link. Limited to 40 hops.

### 3. Evaluation Notebook
`evaluation_results.ipynb` tests and compares the algorithms. The current evaluation is experimental and not fully accurate yet.


## Setup Instructions

1. clone the repository
```sh
git clone repo
cd repo
```
2️. Install dependencies
```sh
uv sync
```
3. Run the Streamlit application
```sh
uv run streamlit run main.py
```

# TODO
1. Scrape all links and store them in a database.
2. Store embeddings for all models to improve lookup speed.
3. Asynchronously fetch data from Wikipedia to optimize performance.
4. Implement backtracking by storing visited paths.
5. Use probabilistic search instead of always selecting the highest-scoring link.
6. Improve UI
