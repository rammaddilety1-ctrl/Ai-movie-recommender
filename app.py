import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------
# Page configuration
# ---------------------------------
st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 AI Movie Recommender System")
st.write("Discover movies similar to your favorite movies using AI 🤖")

# ---------------------------------
# Load dataset
# ---------------------------------
@st.cache_data
def load_data():
    try:
        movies = pd.read_csv("data/movies.csv")
    except FileNotFoundError:
        st.error("movies.csv not found inside the data folder.")
        st.stop()

    return movies

movies = load_data()

# ---------------------------------
# Check required columns
# ---------------------------------
required_columns = ["title", "genres", "overview"]

for column in required_columns:
    if column not in movies.columns:
        st.error(f"Required column '{column}' is missing from movies.csv")
        st.stop()

# Fill missing values
movies["genres"] = movies["genres"].fillna("")
movies["overview"] = movies["overview"].fillna("")

# Combine important features
movies["combined_features"] = movies["genres"] + " " + movies["overview"]

# ---------------------------------
# TF-IDF model
# ---------------------------------
@st.cache_resource
def create_model(data):
    vectorizer = TfidfVectorizer(stop_words="english")
    feature_matrix = vectorizer.fit_transform(data["combined_features"])
    similarity_matrix = cosine_similarity(feature_matrix)
    return similarity_matrix

similarity = create_model(movies)

# ---------------------------------
# Recommendation function
# ---------------------------------
def recommend_movies(movie_name, number_of_movies=5):
    movie_name = movie_name.lower()
    matches = movies[movies["title"].str.lower() == movie_name]

    if matches.empty:
        return None

    movie_index = matches.index[0]
    similarity_scores = list(enumerate(similarity[movie_index]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    for index, score in similarity_scores[1:number_of_movies + 1]:
        movie = movies.iloc[index]
        recommendations.append({
            "title": movie["title"],
            "genres": movie["genres"],
            "similarity": round(score * 100, 2)
        })

    return recommendations

# ---------------------------------
# User interface
# ---------------------------------
st.subheader("🔍 Choose a Movie")

movie_list = movies["title"].dropna().tolist()
selected_movie = st.selectbox("Select your favorite movie:", movie_list)
number_of_movies = st.slider("Number of recommendations:", min_value=3, max_value=10, value=5)

if st.button("🎯 Recommend Movies"):
    recommendations = recommend_movies(selected_movie, number_of_movies)

    if recommendations:
        st.success(f"Movies similar to **{selected_movie}**:")

        for i, movie in enumerate(recommendations, 1):
            st.markdown(
                f"""
                ### {i}. 🎬 {movie['title']}

                **Genre:** {movie['genres']}

                **AI Similarity:** {movie['similarity']}%
                """
            )
            st.divider()
    else:
        st.warning("Movie not found. Please select another movie.")

# ---------------------------------
# About section
# ---------------------------------
st.sidebar.title("ℹ️ About")
st.sidebar.write(
    """
    This AI Movie Recommender uses:

    • TF-IDF Vectorization
    • Cosine Similarity
    • Content-Based Filtering
    • Natural Language Processing

    The system analyzes movie genres and descriptions
    to recommend movies with similar characteristics.
    """
)

st.sidebar.markdown("---")
st.sidebar.write("🎓 AI/ML Project")
