from pyexpat.errors import messages
from django.shortcuts import render
from .models import Review
from .forms import User_Review
from django.shortcuts import get_object_or_404,redirect
# Create your views here.



import sqlite3
from langchain_google_genai import GoogleGenerativeAI
import re
from tabulate import tabulate
from django.http import JsonResponse


def Reviews_List(request):
    reviews = Review.objects.all()

    # Get filter parameters from GET request
    restaurant_name = request.GET.get('restaurant_name', '')
    restaurant_location = request.GET.get('restaurant_location', '')
    min_rating = request.GET.get('min_rating', None)
    max_rating = request.GET.get('max_rating', None)


    # Apply filters based on provided data
    if restaurant_name:
        reviews = reviews.filter(restaurant_name__icontains=restaurant_name)
    if restaurant_location:
        reviews = reviews.filter(restaurant_location__icontains=restaurant_location)
    
    # Convert min_rating and max_rating to float if provided
    if min_rating:
        try:
            min_rating = float(min_rating)
            reviews = reviews.filter(rating__gte=min_rating)
        except ValueError:
            pass  # In case of invalid min_rating input, just ignore it

    if max_rating:
        try:
            max_rating = float(max_rating)
            reviews = reviews.filter(rating__lte=max_rating)
        except ValueError:
            pass  # In case of invalid max_rating input, just ignore it

    # Check if any reviews are found
    if not reviews.exists():
        messages.info(request, 'No reviews found matching the given filters.')

    return render(request, 'reviews/index.html', {'reviews': reviews})



def Review_created(request):
    if request.method == "POST":
        form = User_Review(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)  # Don't save to DB yet
            review.user = request.user  # Assign the current logged-in user to the review
            review.save()  # Save the review after assigning the user
            return redirect('Reviews_List')  # Redirect to the reviews list page
    else:
        form = User_Review()

    return render(request, 'reviews/Review_created.html', {'form': form})


def Review_edit(request, review_id):
    # Get the review object or return a 404 if not found or the user doesn't own it
    review = get_object_or_404(Review, pk=review_id, user=request.user)

    if request.method == "POST":
        form = User_Review(request.POST, request.FILES, instance=review)

        if form.is_valid():
            form.save()  # Save the form after assigning the current user
            return redirect('Reviews_List')  # Redirect to the reviews list page

    else:
        form = User_Review(instance=review)

    return render(request, 'reviews/Review_created.html', {'form': form})


def Review_detail(request, review_id):
    review = get_object_or_404(Review, pk=review_id)
    return render(request, 'reviews/review_detail.html', {'review': review})


def Review_deleted(request, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == "POST":
        review.delete()
        return redirect('Reviews_List')  # Assuming this is the name of the URL for the reviews list

    return render(request, 'reviews/Review_deleted.html', {'review': review})






##Selected
import sqlite3
import re
from langchain_google_genai import GoogleGenerativeAI
from django.http import JsonResponse
from django.shortcuts import render

# ✅ Your Google API Key
api_key = "AIzaSyAEbMVPZ65BP1umolnJB3mh4DK9219qN10"

# ✅ Initialize Gemini AI
llm = GoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=api_key,
    temperature=0.7,  # More reliable results
    max_output_tokens=2048
)

# ✅ Database Connection
db_path = r'D:\Foodgo\Fyp\food\db.sqlite3'

# ✅ Step 1: Fetch Table and Column Names
def get_db_schema():
    """Retrieve all table names and their respective columns."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [table[0] for table in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]
        schema[table] = columns  # Store table and column names
    
    conn.close()
    return schema

db_schema = get_db_schema()  # Get schema dynamically

# ✅ Function to Execute Dynamic Queries
def execute_sql_query(query):
    """Converts a natural language query into SQL and executes it."""
    
    # 🔹 Generate SQL with AI (using schema for accuracy)
    prompt = f"""
    You are an expert SQL query generator for an SQLite database. 
    The database schema is as follows:
    {db_schema}
    
    Convert the following natural language query into a valid SQLite SQL query:
    "{query}"
    
    Ensure:
    - Table and column names exactly match the schema.
    - Queries are SELECT-only (no updates, deletions, or inserts).
    - Include necessary JOINs if required.
    - Use LIKE for string matching to handle case insensitivity or variations in spacing.
    - Ensure there are no leading or trailing spaces (TRIM) in vendor names or any fields involved.
    
    Return ONLY the SQL query without explanation, and do NOT wrap it in markdown or code blocks.
    """
    
    sql_query = llm.invoke(prompt).strip()
    
    # 🔹 Remove unwanted markdown/code formatting
    sql_query = re.sub(r"```(sql)?", "", sql_query).strip()
    
    # 🔹 Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute(sql_query)  # Run query
        results = cursor.fetchall()
        conn.close()
        
        # Check if results are returned
        if results:
            # Format the results into a beautiful table
            columns = [description[0] for description in cursor.description]  # Fetch column names
            formatted_results = tabulate(results, headers=columns, tablefmt="fancy_grid")
            return formatted_results
        else:
            return "No results found. Please check the query or data."
    
    except Exception as e:
        conn.close()
        return f"❌ Error: {e}"

# ✅ Function to Check if Query is Related to Database or General AI Query
def is_database_query(query):
    """Check if the query is related to the database."""
    keywords = ['restaurant', 'item', 'price', 'menu', 'category', 'dish', 'food', 'restaurant', 'menu', 'dish', 'food', 'meal', 'cuisine', 'snack', 'fast food',
        'combo', 'deal', 'special', 'offer', 'buffet', 'street food', 'topping', 'side dish',
        'portion', 'spicy', 'sweet', 'savory', 'dessert', 'chocolate', 'ice cream', 'cake',
        'pastry', 'cookies', 'pudding', 'fries', 'burger', 'pizza', 'pasta', 'shawarma',
        'sandwich', 'biryani', 'rice', 'kebab', 'steak', 'grill', 'barbecue', 'roast',
        'wrap', 'soup', 'salad', 'noodles', 'sushi', 'dim sum', 'taco', 'burrito',
        'enchilada', 'quesadilla', 'pakora', 'samosa', 'golgappa', 'pani puri',
        'chaat', 'dahi puri', 'kachori', 'halwa', 'jalebi', 'rasmalai', 'gulab jamun',
        'barfi', 'laddu', 'sohan halwa', 'falooda', 'kheer', 'sheer khurma', 'gajar ka halwa',

        # 🍔 Fast Food Items
        'cheeseburger', 'chicken burger', 'beef burger', 'fish burger', 'zinger',
        'nuggets', 'fried chicken', 'broast', 'hot wings', 'popcorn chicken', 
        'hotdog', 'corn dog', 'club sandwich', 'grilled cheese', 'sub sandwich',
        'garlic bread', 'wrap', 'frankfurter', 'panini',

        # 🥘 Traditional Pakistani/Indian Food
        'dal', 'chana', 'sabzi', 'keema', 'nihari', 'haleem', 'payee', 'karahi',
        'qorma', 'handi', 'butter chicken', 'tandoori chicken', 'mutton korma',
        'sajji', 'katakat', 'chicken tikka', 'chapli kebab', 'seekh kebab',
        'shami kebab', 'tikka boti', 'malai boti', 'reshmi kebab', 'mutton chops',
        'paya', 'bihari boti', 'mutton biryani', 'chicken biryani', 'sindhi biryani',

        # 🍩 Desserts & Sweets
        'mithai', 'halwa', 'jalebi', 'gulab jamun', 'rasgulla', 'barfi', 'kaju katli',
        'chocolate cake', 'black forest cake', 'cheesecake', 'mousse', 'waffles',
        'pancakes', 'brownies', 'cookies', 'ice cream', 'kulfi', 'falooda',

        # 🍗 Meat & Protein Dishes
        'chicken', 'beef', 'mutton', 'fish', 'prawns', 'lobster', 'crab',
        'duck', 'lamb', 'egg', 'tofu', 'paneer', 'steak', 'grilled chicken',
        'barbecue chicken', 'shashlik', 'chicken karahi', 'mutton karahi',

        # 🥦 Vegetarian & Vegan Food
        'vegetarian', 'vegan', 'salad', 'spinach', 'broccoli', 'tofu', 'dal makhani',
        'chana masala', 'baingan bharta', 'aloogobi', 'methi', 'bhindi', 'paneer tikka',

        # 🍛 Asian, Chinese, Thai & Continental
        'chinese', 'thai', 'szechuan', 'ramen', 'stir fry', 'dim sum', 'sushi',
        'spring rolls', 'hakka noodles', 'wontons', 'teriyaki', 'kimchi', 'yakitori',

        # 🍹 Beverages
        'chai', 'tea', 'green tea', 'karak chai', 'doodh pati', 'coffee',
        'latte', 'cappuccino', 'espresso', 'americano', 'hot chocolate',
        'smoothie', 'shake', 'milkshake', 'soft drink', 'soda', 'juice',
        'mocktail', 'cocktail', 'lemonade', 'water', 'bottle', 'energy drink',
        'lassi', 'falooda', 'cold coffee', 'sherbet',

        # 🍽️ Meal Timings
        'breakfast', 'brunch', 'lunch', 'dinner', 'supper', 'late night', 'high tea',

        # 🏙️ Locations (Cities & Areas)
        'hyderabad', 'karachi', 'lahore', 'islamabad', 'rawalpindi', 'quetta',
        'peshawar', 'multan', 'faisalabad', 'sukkur', 'sialkot', 'murree', 'gilgit',
        'skardu', 'clifton', 'defence', 'gulshan', 'saddar', 'bahadurabad', 'blue area',
        'f-7', 'f-8', 'g-9', 'north nazimabad', 'scheme 33',

        # 🍱 Food Service & Dining Options
        'dine-in', 'takeaway', 'delivery', 'drive-thru', 'order', 'reservation',
        'booking', 'table', 'home delivery', 'pick-up', 'online order',

        # 💰 Pricing & Payment
        'price', 'cost', 'bill', 'discount', 'voucher', 'coupon', 'cash', 'card',
        'wallet', 'QR payment', 'tips', 'service charge', 'GST', 'tax',

        # ⭐ Restaurant Ratings & Reviews
        'rating', 'review', 'stars', 'feedback', 'customer service', 'recommendation',

        # 🌍 Ethnic Cuisines
        'desi', 'pakistani', 'indian', 'chinese', 'thai', 'italian', 'turkish',
        'afghan', 'arabic', 'japanese', 'mexican', 'french', 'german', 'persian',

        # 🔥 Miscellaneous Food & Dining Terms
        'opening hours', 'closing time', 'timings', 'peak hours', 'busy hours',
        'best time to visit', 'menu card', 'staff', 'ambience', 'theme', 'decor',
        'music', 'parking', 'washroom', 'wifi', 'smoking area', 'rooftop',
        'garden seating', 'family-friendly', 'kids menu', 'pet-friendly',
        'play area', 'buffet', 'brunch', 'food truck', 'catering', 'bake shop']
    return any(keyword.lower() in query.lower() for keyword in keywords)

# ✅ Function to Get AI Response for Non-Database Queries
def get_ai_response(query):
    """Use AI to respond to general questions."""
    prompt = f"Answer this question: {query}"
    response = llm.invoke(prompt).strip()
    return response

# ✅ Main function to handle user query
def handle_user_query(query):
    if is_database_query(query):
        return execute_sql_query(query)
    else:
        return get_ai_response(query)

# ✅ View to handle search form
def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
            response = handle_user_query(query)
            return JsonResponse({'response': response})
        else:
            return JsonResponse({'response': "No query provided."})
    return render(request, 'reviews/search.html')  # If not a POST request, render the search form

