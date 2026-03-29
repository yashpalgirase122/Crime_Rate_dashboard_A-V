import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import warnings

warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'ai_crime_dashboard_secret_key'

# MySQL Config - Important: Update if your local MySQL has a different password
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Y@shpal123' 
app.config['MYSQL_DB'] = 'crime_dashboard_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'crime_dataset_india.csv')

def get_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame()

def get_dashboard_stats():
    df = get_data()
    if df.empty:
        return {}
    
    total_crimes = int(df['Crime_Count'].sum())
    most_common_crime = df.groupby('Crime_Type')['Crime_Count'].sum().idxmax()
    
    city_crimes = df.groupby('City')['Crime_Count'].sum()
    most_dangerous_city = city_crimes.idxmax()
    
    yearly_crime = df.groupby('Year')['Crime_Count'].sum().reset_index()
    X = yearly_crime[['Year']]
    y = yearly_crime['Crime_Count']
    model = LinearRegression()
    model.fit(X, y)
    
    last_year = int(yearly_crime['Year'].max())
    future_years = np.array([[last_year + i] for i in range(1, 6)])
    predictions = model.predict(future_years)
    forecast = {int(last_year + i): float(predictions[i-1]) for i in range(1, 6)}
    
    return {
        'total_crimes': total_crimes,
        'most_common_crime': str(most_common_crime),
        'most_dangerous_city': str(most_dangerous_city),
        'forecast': forecast
    }

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password", "error")
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_pw = generate_password_hash(password)
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)", 
                        (username, email, hashed_pw))
            mysql.connection.commit()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))
        except Exception as e:
            flash("Email already registered.", "error")
        finally:
            cur.close()
            
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        flash("OTP sent to your email! (Mock)", "success")
    return render_template('forgot_password.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    stats = get_dashboard_stats()
    df = get_data()
    
    cities = df['City'].unique().tolist() if not df.empty else []
    crime_types = df['Crime_Type'].unique().tolist() if not df.empty else []
    
    total_c = stats.get('total_crimes', 0)
    if isinstance(total_c, (int, float)) and total_c > 100000:
         flash("ALERT: Total recorded crimes exceed 100K threshold!", "warning")
    
    return render_template('dashboard.html', stats=stats, cities=cities, crime_types=crime_types, username=session.get('username'))

@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Access Denied. Admins only.", "error")
        return redirect(url_for('dashboard'))
        
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username, email, role FROM users")
    users = cur.fetchall()
    cur.execute("SELECT * FROM crime_predictions ORDER BY created_at DESC LIMIT 10")
    predictions = cur.fetchall()
    cur.execute("SELECT * FROM alerts ORDER BY created_at DESC LIMIT 10")
    alerts = cur.fetchall()
    cur.close()
    
    return render_template('admin.html', users=users, predictions=predictions, alerts=alerts)

@app.route('/chatbot')
def chatbot():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('chatbot.html')

@app.route('/api/crime_data')
def api_crime_data():
    df = get_data()
    if df.empty:
        return jsonify({})
    
    city_dist = df.groupby('City')['Crime_Count'].sum().to_dict()
    city_dist = {str(k): int(v) for k, v in city_dist.items()}
    
    cat_dist = df.groupby('Crime_Type')['Crime_Count'].sum().to_dict()
    cat_dist = {str(k): int(v) for k, v in cat_dist.items()}
    
    yearly = df.groupby('Year')['Crime_Count'].sum().to_dict()
    yearly = {int(k): int(v) for k, v in yearly.items()}
    
    return jsonify({
        'city_distribution': city_dist,
        'category_distribution': cat_dist,
        'yearly_trend': yearly
    })

@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.json
    city = data.get('city')
    crime_type = data.get('crime_type')
    
    df = get_data()
    if df.empty:
        return jsonify({'error': 'No data'})
        
    filtered = df[(df['City'] == city) & (df['Crime_Type'] == crime_type)]
    if filtered.empty:
        return jsonify({'error': 'Not enough data for this combination'})
        
    X = filtered[['Year']]
    y = filtered['Crime_Count']
    model = LinearRegression()
    model.fit(X, y)
    
    next_year = int(filtered['Year'].max()) + 1
    prediction = model.predict([[next_year]])[0]
    prediction = max(0, int(prediction))
    
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO crime_predictions (city, crime_type, predicted_count, prediction_year) VALUES (%s, %s, %s, %s)",
                    (city, crime_type, prediction, next_year))
        mysql.connection.commit()
        cur.close()
        
    return jsonify({
        'city': city,
        'crime_type': crime_type,
        'year': next_year,
        'predicted_count': int(prediction)
    })

@app.route('/api/map_data')
def api_map_data():
    df = get_data()
    if df.empty:
        return jsonify([])
        
    sample_df = df.sample(min(len(df), 1000), random_state=42)
    city_totals = df.groupby('City')['Crime_Count'].sum()
    max_crime = float(city_totals.max())
    
    map_points = []
    for _, row in sample_df.iterrows():
        city_crime = city_totals[row['City']]
        risk_level = 'LOW'
        if city_crime > max_crime * 0.7:
            risk_level = 'HIGH'
        elif city_crime > max_crime * 0.4:
            risk_level = 'MEDIUM'
            
        map_points.append({
            'lat': float(row['Latitude']),
            'lng': float(row['Longitude']),
            'intensity': float(row['Crime_Count']),
            'city': str(row['City']),
            'crime': str(row['Crime_Type']),
            'risk': risk_level
        })
        
    return jsonify(map_points)

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    data = request.json
    question = data.get('question', '').lower()
    df = get_data()
    
    response = "I couldn't understand the question. Try asking 'Which city has highest crime?', 'Which crime is most common?', or 'Which year had highest crime?'"
    
    if 'highest crime' in question and 'city' in question:
        city = df.groupby('City')['Crime_Count'].sum().idxmax()
        count = int(df.groupby('City')['Crime_Count'].sum().max())
        response = f"The city with the highest crime is {city} with a total of {count} recorded crimes."
    
    elif 'most common' in question and 'crime' in question:
        crime = df.groupby('Crime_Type')['Crime_Count'].sum().idxmax()
        response = f"The most common crime type is {crime}."
        
    elif 'highest crime' in question and 'year' in question:
        year = int(df.groupby('Year')['Crime_Count'].sum().idxmax())
        response = f"The year with the highest overall crime was {year}."
        
    return jsonify({'answer': response})

@app.route('/api/patrol_routes')
def api_patrol_routes():
    df = get_data()
    if df.empty:
        return jsonify([])
        
    coords = df[['Latitude', 'Longitude']].dropna()
    if len(coords) < 5:
        return jsonify([])
        
    kmeans = KMeans(n_clusters=5, random_state=42)
    kmeans.fit(coords)
    
    centers = kmeans.cluster_centers_
    routes = [{'lat': float(c[0]), 'lng': float(c[1])} for c in centers]
    
    return jsonify(routes)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
