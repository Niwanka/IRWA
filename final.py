import streamlit as st
import numpy as np
from pymongo import MongoClient
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from sklearn.neighbors import NearestNeighbors
from textblob import TextBlob  # For spell correction
import pickle

# MongoDB client setup
client = MongoClient("mongodb+srv://Haran:NGjWcKG55e3K83SB@cluster0.0ttlk.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["searchEngine"]
collection = db["Recipe"]
pdf_collection = db['pdf_files']  # Collection for PDFs



# Load pre-trained model for generating query embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Load TF-IDF scores for query expansion
with open('idf_values.pkl', 'rb') as file:
    tfidf_scores = pickle.load(file)

# Load Word2Vec model
with open('word2vec_model.pkl', 'rb') as file:
    expanded_model = pickle.load(file)

# Function for spell checking
def check_spelling(query):
    blob = TextBlob(query)
    corrected_text = blob.correct()
    if query == str(corrected_text):
        return query
    else:
        return f"Did you mean: {corrected_text}?", str(corrected_text)

# Cosine similarity search
def search_with_cosine_similarity(query_embedding, top_n=10):
    docs = list(collection.find({}, {"RecipeId": 1, "Name": 1, "encoded_vector": 1}))
    if not docs:
        return []
    doc_embeddings = np.array([doc['encoded_vector'] for doc in docs])
    doc_ids = [doc['RecipeId'] for doc in docs]
    doc_names = [doc['Name'] for doc in docs]

    similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
    top_n_indices = similarities.argsort()[::-1][:top_n]

    results = []
    for idx in top_n_indices:
        results.append({
            'RecipeId': doc_ids[idx],
            'Name': doc_names[idx],
            'Similarity': similarities[idx]
        })
    return results

# Nearest Neighbors search
def search_with_nearest_neighbors(query_embedding, top_n=10):
    docs = list(collection.find({}, {"RecipeId": 1, "Name": 1, "encoded_vector": 1}))
    if not docs:
        return []
    doc_embeddings = np.array([doc['encoded_vector'] for doc in docs])
    doc_ids = [doc['RecipeId'] for doc in docs]
    doc_names = [doc['Name'] for doc in docs]

    neigh = NearestNeighbors(n_neighbors=top_n, metric='cosine')
    neigh.fit(doc_embeddings)
    distances, indices = neigh.kneighbors([query_embedding], n_neighbors=top_n)

    results = []
    for idx, distance in zip(indices[0], distances[0]):
        results.append({
            'RecipeId': doc_ids[idx],
            'Name': doc_names[idx],
            'Similarity': 1 - distance
        })
    return results

# Cluster-based search
def search_using_clusters(query_embedding, top_n=10):
    documents = list(collection.find({}, {"encoded_vector": 1, "cluster": 1}))
    doc_embeddings = np.array([doc['encoded_vector'] for doc in documents])
    clusters = np.array([int(doc['cluster']) for doc in documents])

    cluster_distances = cosine_similarity([query_embedding], doc_embeddings)[0]
    closest_cluster = clusters[np.argmax(cluster_distances)]

    filtered_docs = list(collection.find({"cluster": int(closest_cluster)}, {"RecipeId": 1, "Name": 1, "encoded_vector": 1}))
    doc_embeddings = np.array([doc['encoded_vector'] for doc in filtered_docs])
    doc_ids = [doc['RecipeId'] for doc in filtered_docs]
    doc_names = [doc['Name'] for doc in filtered_docs]

    similarities = cosine_similarity([query_embedding], doc_embeddings)[0]
    top_n_indices = similarities.argsort()[::-1][:top_n]

    results = []
    for idx in top_n_indices:
        results.append({
            'RecipeId': doc_ids[idx],
            'Name': doc_names[idx],
            'Similarity': similarities[idx]
        })
    return results

# Search PDFs (kept unchanged)
def search_pdf(query_embedding, top_n=10):
    pdf_data = list(pdf_collection.find({}))
    pdf_embeddings = [np.array(pdf['embedding']) for pdf in pdf_data]

    similarities = cosine_similarity([query_embedding], pdf_embeddings)[0]
    top_indices = similarities.argsort()[::-1][:top_n]

    top_pdfs = []
    for index in top_indices:
        top_pdfs.append({
            'name': pdf_data[index]['file_name'],
            'download_link': pdf_data[index]['download_link'],
            'Similarity': similarities[index]
        })

    return top_pdfs

# Function to show recipe details
def show_recipe_details(recipe_id):
    recipe = collection.find_one({"RecipeId": recipe_id})
    
    st.title(recipe['Name'])
    st.write(f"**Author:** {recipe['AuthorName']}")
    
    # Format cook time and prep time
    cook_time = recipe['CookTime']
    prep_time = recipe['PrepTime']
    
    st.write(f"**Cook Time:** {cook_time}")
    st.write(f"**Prep Time:** {prep_time}")
    
    # Format ingredients and instructions
    formatted_ingredients = recipe['RecipeIngredientParts']
    formatted_instructions = recipe['RecipeInstructions']
    
    st.write(f"**Ingredients:** {formatted_ingredients}")
    st.write(f"**Instructions:** {formatted_instructions}")
st.markdown(
    """
    <style>
    .stApp {
        background-image: url("");  /* Replace with your image URL */
        background-size: contain;
        background-position: center;
        color: #F5F5F5;
        height: 100vh;
    }
    .sidebar .sidebar-content {
        background-color: rgba(255, 255, 255, 0.8);
        border-radius: 15px;
        padding: 10px;
    }
    .stButton>button {
        color: white;
        background-color: #ff6347;
        border-radius: 12px;
        padding: 12px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #ff4500;
    }
    .stTextInput>div>div>input {
        border-radius: 30px;  /* Rounded corners */
        padding: 10px 40px;  /* Space for the icon */
        color: #ffffff;
    }
    .stTextInput>div>div>input::placeholder {
        color:  #d7dbdd;  /* Placeholder text color */
    }
    .stTextInput>div {
        position: relative;  /* Make the container relative for absolute positioning */
    }
    .search-icon {
        position: absolute;
        right: 10px;  /* Adjust position */
        top: 50%;  /* Center vertically */
        transform: translateY(-50%);  /* Adjust for centering */
        color: #ff6347;  /* Icon color */
        pointer-events: none;  /* Prevent mouse events on the icon */
    }
    .logo {
        width: 175px;  /* Increased logo width */
        height: 175px;  /* Increased logo height */
        border-radius: 50%;  /* Make it round */
        object-fit: cover;  /* Cover the area of the logo */
        display: block;
        margin: 0 auto;  /* Center the logo */
    }
    .title {
        text-align: center;  /* Center the title */
        font-size: 2.5em;  /* Increase title size if needed */
        margin-top: 20px;  /* Add space above title */
    }
    .stSlider>div>div>input {
        color: #ff6347;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# Streamlit UI
st.markdown('<img src="https://i.pinimg.com/564x/e1/44/f3/e144f36783c75725fb0f2625c6bcd7c8.jpg" class="logo">', unsafe_allow_html=True)  # Add your logo here
st.markdown('<h1 class="title">CookBook Recipe Search Engine</h1>', unsafe_allow_html=True)  # Centered title
st.markdown("<br>", unsafe_allow_html=True)
# Narrow layout for search type
with st.sidebar:
    search_type = st.selectbox("Search Type:", ["Cosine Similarity", "Nearest Neighbors", "Cluster-Based", "PDF Search"])

# Input section
query = st.text_input("Enter your search query:", placeholder="e.g., Italian pasta, healthy recipes...")

# Check spelling correction
spelling_result = check_spelling(query)
if isinstance(spelling_result, tuple):
    st.markdown(f"### {spelling_result[0]}")
    correct_query = spelling_result[1]
else:
    correct_query = spelling_result

# Search logic
if correct_query:
    query_embedding = model.encode([correct_query])[0]

    if search_type == "Cosine Similarity":
        results = search_with_cosine_similarity(query_embedding)
        st.subheader("🔗 Cosine Similarity Search Results")
        for result in results:
            if st.button(result['Name'], key=result['RecipeId']):
                st.session_state['selected_recipe'] = result['RecipeId']
                #st.experimental_rerun()
                st.rerun()

    elif search_type == "Nearest Neighbors":
        results = search_with_nearest_neighbors(query_embedding)
        st.subheader("🔗 Nearest Neighbors Search Results")
        for result in results:
            if st.button(result['Name'], key=result['RecipeId']):
                st.session_state['selected_recipe'] = result['RecipeId']
                #st.experimental_rerun()
                st.rerun()

    elif search_type == "Cluster-Based":
        results = search_using_clusters(query_embedding)
        st.subheader("🔗 Cluster-Based Search Results")
        for result in results:
            if st.button(result['Name'], key=result['RecipeId']):
                st.session_state['selected_recipe'] = result['RecipeId']
                #st.experimental_rerun()
                st.rerun()

    elif search_type == "PDF Search":
        pdf_results = search_pdf(query_embedding)
        st.subheader("📄 PDF Search Results")
        for pdf in pdf_results:
            st.write(f"[**{pdf['name']}**]({pdf['download_link']}) (Similarity: `{pdf['Similarity']:.2f}`)")

# Show selected recipe details
if 'selected_recipe' in st.session_state:
    show_recipe_details(st.session_state['selected_recipe'])

# Footer section
st.write("---")
