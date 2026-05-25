import streamlit as st
import pickle
import pandas as pd
import requests

st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

st.markdown("""
<style>

/* IMAGE */
.img-wrap{
    display: flex;
    justify-content: center;
}

.img-wrap img{
    border-radius: 14px;
    transition: transform 0.3s ease;
}

.img-wrap img:hover{
    transform: scale(1.08);
    cursor: pointer;
}

/* CARD */
.movie-card{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 12px;
    border-radius: 16px;

    transition: transform 0.3s ease, box-shadow 0.3s ease;
    will-change: transform;
}

/* IMPORTANT: FORCE HOVER ON WHOLE CARD */
.movie-card:hover{
    transform: translateY(-10px) scale(1.08);
    box-shadow: 0 20px 50px rgba(0,0,0,0.4);
    cursor: pointer;
    z-index: 20;
}

/* TEXT FIX */
.movie-text{
    text-align: center;
    transition: transform 0.3s ease;
}

.movie-card:hover .movie-text{
    transform: translateY(-4px);
}

/* prevent clipping */
div[data-testid="column"]{
    overflow: visible !important;
}

</style>
""", unsafe_allow_html=True)


def fetch_movie_details(movie_id):

    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=b153151153d12d34548876c2988069b4"

        response = requests.get(url, timeout=10)
        data = response.json()

        # SAFE poster handling
        poster_path = data.get("poster_path")

        if poster_path:
            poster = "https://image.tmdb.org/t/p/w500/" + poster_path
        else:
            poster = "https://via.placeholder.com/500x750?text=No+Image"

        rating = data.get("vote_average", "N/A")
        release = data.get("release_date", "N/A")
        overview = data.get("overview", "No overview available")

        # safer title handling
        title = data.get("title", "movie")

        trailer = f"https://www.youtube.com/results?search_query={title}+trailer"

        return poster, rating, release, overview, trailer

    except Exception as e:

        print("Error:", e)

        return (
            "https://via.placeholder.com/500x750?text=No+Image",
            "N/A",
            "N/A",
            "No overview available",
            "#"
        )
    
movies_dict = pickle.load(open('movies_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

def recommend(movie):

    movie_index = movies[movies['title'] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_poster = []
    recommended_ratings = []
    recommended_release = []
    recommended_overview = []
    recommended_trailer = []

    for i in movies_list:

        movie_id = movies.iloc[i[0]].movie_id

        title = movies.iloc[i[0]].title
        recommended_movies.append(title)

        poster, rating, release, overview, trailer = fetch_movie_details(movie_id)

        recommended_movies_poster.append(poster)
        recommended_ratings.append(rating)
        recommended_release.append(release)
        recommended_overview.append(overview)
        recommended_trailer.append(trailer)

    return (
        recommended_movies,
        recommended_movies_poster,
        recommended_ratings,
        recommended_release,
        recommended_overview,
        recommended_trailer
    )


st.markdown(
    "<h1 style='text-align:center;'>🎬 Movie Recommender System</h1>",
    unsafe_allow_html=True
)

st.caption(
    "Find similar movies using Machine Learning and TMDB API"
)

with st.sidebar:

    st.header("About Project")

    st.write(
        """
        Movie Recommendation System using:

        ✅ Machine Learning  
        ✅ Cosine Similarity  
        ✅ Streamlit  
        ✅ TMDB API
        """
    )

    st.write("---")

    st.subheader("Developer")

    st.write("Faizan Khan")


selected_movie_name = st.selectbox(
    'Select Movie',
    movies['title'].values
)

if st.button('Recommend'):

    with st.spinner("Finding similar movies... 🎬"):
        names, posters, ratings, release, overviews, trailers = recommend(selected_movie_name)

    st.success("Recommendations Ready ✅")

    st.subheader("Recommended Movies")

    cols = st.columns(5)

    for i in range(len(names)):

      with cols[i]:

            st.markdown('<div class="movie-card">', unsafe_allow_html=True)

            # IMAGE
            st.markdown(
                f"""
                <div class="img-wrap">
                    <img src="{posters[i]}" width="150">
                </div>
                """,
                unsafe_allow_html=True
            )

            # TEXT (ONLY ONCE)
            st.markdown(
                f"""
                <div class="movie-text">
                    <h4>{names[i]}</h4>
                    <p>⭐ {ratings[i]}</p>
                    <p>📅 {release[i][:4]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

            # TRAILER BUTTON
            st.link_button(
                "▶ Trailer",
                trailers[i]
            )

            st.markdown('</div>', unsafe_allow_html=True)