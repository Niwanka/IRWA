import streamlit as st

# Sample data for demonstration
sample_recipes = [
    {"name": "🥗 Vegan Pasta", "cuisine": "🍝 Italian", "time": "⏱ 30 min", "diet": "🌱 Vegan", "rating": "⭐ 4.5", "reviews": 150},
    {"name": "🍛 Chicken Curry", "cuisine": "🍲 Indian", "time": "⏱ 45 min", "diet": "🍗 Non-Vegetarian", "rating": "⭐ 4.8", "reviews": 220},
    {"name": "🍣 Vegetarian Sushi", "cuisine": "🍱 Japanese", "time": "⏱ 20 min", "diet": "🥒 Vegetarian", "rating": "⭐ 4.3", "reviews": 80},
    {"name": "🥘 Beef Stew", "cuisine": "🍖 American", "time": "⏱ 60 min", "diet": "🍖 Non-Vegetarian", "rating": "⭐ 4.7", "reviews": 200},
    {"name": "🍜 Vegetable Stir Fry", "cuisine": "🥡 Chinese", "time": "⏱ 15 min", "diet": "🌱 Vegan", "rating": "⭐ 4.2", "reviews": 95},
]

# Set a background image and style customizations
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

# Sidebar for filters
st.sidebar.header("Customize Your Search")
st.sidebar.markdown("<br>", unsafe_allow_html=True)
time_filter = st.sidebar.slider("⏱ Maximum Cooking Time (minutes)", min_value=1, max_value=120, value=60)
st.sidebar.markdown("<br>", unsafe_allow_html=True)  # Add space between sliders
preparing_time_filter = st.sidebar.slider("⏱ Maximum Preparing Time (minutes)", min_value=1, max_value=60, value=30)
st.sidebar.markdown("<br>", unsafe_allow_html=True)  # Add space between sliders
rating_filter = st.sidebar.slider("⭐ Minimum Recipe Rating", min_value=0.0, max_value=5.0, value=4.0, step=0.1)

# Main section
st.markdown('<img src="https://i.pinimg.com/564x/e1/44/f3/e144f36783c75725fb0f2625c6bcd7c8.jpg" class="logo">', unsafe_allow_html=True)  # Add your logo here
st.markdown('<h1 class="title">CookBook Recipe Search Engine</h1>', unsafe_allow_html=True)  # Centered title
st.markdown("<br>", unsafe_allow_html=True)

# Search bar without a label
search_query = st.text_input(
    "",
    placeholder="Enter recipe name or ingredient",
    key="search",
    label_visibility="collapsed"  # Hide the label
)

# Add search icon using Markdown
if search_query:
    st.markdown('<i class="search-icon"></i>', unsafe_allow_html=True)

# Filter and search logic
def search_recipes(query, max_time, min_rating):
    filtered_recipes = []

    for recipe in sample_recipes:
        # Check if the recipe matches the search query and filters
        if query.lower() in recipe["name"].lower() or query.lower() in recipe["cuisine"].lower():
            cooking_time = int(recipe["time"].split(" ")[1])  # Extract cooking time as an integer
            rating = float(recipe["rating"].split(" ")[1])  # Extract rating as a float
            if cooking_time <= max_time and rating >= min_rating:
                filtered_recipes.append(recipe)

    return filtered_recipes

# Automatically search when input changes
if search_query:
    results = search_recipes(search_query, time_filter, preparing_time_filter)
    
    if results:
        st.subheader("📋 Search Results")
        for recipe in results:
            st.write(f"**{recipe['name']}** - {recipe['cuisine']} - {recipe['time']} - {recipe['diet']} - {recipe['rating']} ({recipe['reviews']} reviews)")
            st.button("❤️ Save Recipe", key=recipe['name'])  # Save recipe button
    else:
        st.write("🚫 No recipes found matching your search.")


# Footer with an inspirational message 
st.write("---")
st.markdown('<div style="text-align: center;">🥘Find recipes that match your taste, dietary preferences, and cooking time!🥘</div>', unsafe_allow_html=True)
