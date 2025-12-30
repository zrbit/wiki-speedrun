import streamlit as st
from traversal import (
    naive_traversal,
    embedding_traversal,
    better_embedding_traversal
)
from utils import (
    get_popular_links,
    get_random_links
)

st.set_page_config(layout="wide")
st.title("Wiki Speedrun")

if "start_link" not in st.session_state:
    st.session_state.start_link = None
if "end_link" not in st.session_state:
    st.session_state.end_link = None
if "selected_difficulty" not in st.session_state:
    st.session_state.selected_difficulty = None



difficulty_levels = ["Easy", "Medium", "Hard", "Expert"]
difficulty = st.selectbox("Select Difficulty Level", difficulty_levels)

if st.button("🎲 Reroll Links"):
    st.session_state.selected_difficulty = None

if st.session_state.selected_difficulty != difficulty:
    if difficulty == "Easy":
        st.session_state.start_link = get_popular_links("wiki_links.db", 1)[0]
        st.session_state.end_link = get_popular_links("wiki_links.db", 1)[0]

    elif difficulty == "Medium":
        st.session_state.start_link = get_popular_links("wiki_links.db", 1)[0]
        st.session_state.end_link = get_random_links("wiki_links.db", 1)[0]

    elif difficulty == "Hard":
        st.session_state.start_link = get_random_links("wiki_links.db", 1)[0]
        st.session_state.end_link = get_popular_links("wiki_links.db", 1)[0]

    else:  # Expert
        st.session_state.start_link = get_random_links("wiki_links.db", 1)[0]
        st.session_state.end_link = get_random_links("wiki_links.db", 1)[0]

    st.session_state.selected_difficulty = difficulty

start_link = st.session_state.start_link
end_link = st.session_state.end_link

st.write(f"**Start Link:** {start_link}")
st.write(f"**End Link:** {end_link}")

traversal_methods = {
    "Naive Traversal": naive_traversal,
    "Embedding Traversal": embedding_traversal,
    "Better Embedding Traversal": better_embedding_traversal
}
selected_method = st.multiselect("Select Traversal Method", list(traversal_methods.keys()),default=["Better Embedding Traversal"])

results = []

if st.button("Start Traversal"):
    with st.spinner("Finding optimal path..."):
        results.clear()
        for method in selected_method:
            traversal_func = traversal_methods[method]
            time_taken, links_traversed, traversal_path, found = traversal_func(start_link, end_link)
            results.append((method, time_taken, links_traversed, traversal_path, found))


st.write("## 📊 Results Summary")
st.table(
    {
        "Method": [r[0] for r in results],
        "Time Taken": [r[1] for r in results],
        "Links Traversed": [r[2] for r in results],
        "Found Target": [r[4] for r in results],
    }
)

#if they want to see detailed paths
for method, time_taken, links_traversed, traversal_path, found in results:
    with st.expander(f"See Detailed Path for {method}"):
        if found:
            for idx, link in enumerate(traversal_path):
                st.write(f"{idx + 1}. {link}")
        else:
            st.write("Target link not found within the traversal limits.")





