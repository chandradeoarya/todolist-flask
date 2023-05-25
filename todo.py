import logging
import os
from flask import Flask, jsonify, abort, request, make_response
from flaskext.mysql import MySQL
from flask_cors import CORS
from elasticapm.contrib.flask import ElasticAPM

# Set up logging
# logging.basicConfig(filename='application.log', level=logging.INFO)

# Create a formatter that includes a timestamp
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create a logger and configure it with the formatter
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Specify the directory path and create it if it doesn't exist
log_directory = 'logs'  # Replace 'logs' with the desired directory name
os.makedirs(log_directory, exist_ok=True)

# Specify the log file path
log_file_path = os.path.join(log_directory, 'application.log')

# Create a file handler and add it to the logger
file_handler = logging.FileHandler(log_file_path, mode='a')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Log a sample message
logger.info('This is a sample log message to test.')

app = Flask(__name__)
CORS(app)

app.config['ELASTIC_APM'] = {
# Set the required service name. Allowed characters:
# a-z, A-Z, 0-9, -, _, and space
'SERVICE_NAME': 'todolist-flask_apm',

# Use if APM Server requires a secret token
'SECRET_TOKEN': '',

# Set the custom APM Server URL (default: http://localhost:8200)
'SERVER_URL': 'http://localhost:8200',

# Set the service environment
'ENVIRONMENT': 'development',
}

apm = ElasticAPM(app)


# Configuring MySQL database
app.config['MYSQL_DATABASE_HOST'] = 'todo-database-server'
app.config['MYSQL_DATABASE_USER'] = 'chandra'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Chandra@123'
app.config['MYSQL_DATABASE_DB'] = 'todo_db'
app.config['MYSQL_DATABASE_PORT'] = 3306
mysql = MySQL()
mysql.init_app(app)
connection = mysql.connect()
connection.autocommit(True)
cursor = connection.cursor()

# Function to initialize to-do database
def init_todo_db():
    """Function to initialize the to-do list database by creating and populating the table."""
    # Drop table if it exists
    drop_table = 'DROP TABLE IF EXISTS todo_db.todos;'
    # Create new table
    todos_table = """
    CREATE TABLE todo_db.todos(
    task_id INT NOT NULL AUTO_INCREMENT,
    title VARCHAR(100) NOT NULL,
    description VARCHAR(200),
    is_done BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (task_id)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    # Insert data into table
    data = """
    INSERT INTO todo_db.todos (title, description, is_done)
    VALUES
        ("Learning Linux and AWS", "Finishing all topics", 1 ),
        ("Infra and automation", "Just forgot. Need to revise again.", 0),
        ("CICD", "Learn more", 0);
    """
    cursor.execute(drop_table)
    cursor.execute(todos_table)
    cursor.execute(data)

# Logging helper functions
def log_request_start():
    logging.info('Request started: %s %s', request.method, request.url)

def log_request_end():
    logging.info('Request ended: %s %s', request.method, request.url)

def log_task_operation(operation):
    logging.info('Task %s: %s', operation, request.json['title'])

def log_request_error(error_code):
    logging.error('Request error: %s %s', error_code, request.url)

# Flask request hooks
@app.before_request
def before_request():
    log_request_start()

@app.after_request
def after_request(response):
    log_request_end()
    return response



def get_all_tasks():
    """Function to retrieve all tasks from the database."""
    query = "SELECT * FROM todos;"
    cursor.execute(query)
    result = cursor.fetchall()
    tasks =[{'task_id':row[0], 'title':row[1], 'description':row[2], 'is_done': bool(row[3])} for row in result]
    return tasks

def find_task(id):
    """Function to find a task by its ID in the database."""
    query = f"SELECT * FROM todos WHERE task_id={id};"
    cursor.execute(query)
    row = cursor.fetchone()
    task = None
    if row is not None:
        task = {'task_id':row[0], 'title':row[1], 'description':row[2], 'is_done': bool(row[3])}
    return task

def insert_task(title, description):
    """Function to insert a new task into the database."""
    insert = f"INSERT INTO todos (title, description) VALUES ('{title}', '{description}');"
    cursor.execute(insert)
    query = f"SELECT * FROM todos WHERE task_id={cursor.lastrowid};"
    cursor.execute(query)
    row = cursor.fetchone()
    return {'task_id':row[0], 'title':row[1], 'description':row[2], 'is_done': bool(row[3])}

def change_task(task):
    """Function to change the details of an existing task in the database."""
    update = f"UPDATE todos SET title='{task['title']}', description = '{task['description']}', is_done = {task['is_done']} WHERE task_id= {task['task_id']};"
    cursor.execute(update)
    query = f"SELECT * FROM todos WHERE task_id={task['task_id']};"
    cursor.execute(query)
    row = cursor.fetchone()
    return {'task_id':row[0], 'title':row[1], 'description':row[2], 'is_done': bool(row[3])}

def remove_task(task):
    """Function to remove a task from the database."""
    delete = f"DELETE FROM todos WHERE task_id= {task['task_id']};"
    cursor.execute(delete)
    query = f"SELECT * FROM todos WHERE task_id={task['task_id']};"
    cursor.execute(query)
    row = cursor.fetchone()
    return True if row is None else False


# Set up Flask routes for API
@app.route('/')
def home():
    """Home route that returns a welcome message."""
    return "Welcome to the to-do API Service"

@app.route('/todos', methods=['GET'])
def get_tasks():
    """API route to retrieve all tasks."""
    try:
        tasks = get_all_tasks()
        return jsonify({'tasks': tasks})
    except Exception as e:
        log_request_error(500)
        return make_response(jsonify({'error': 'Internal server error'}), 500)

@app.route('/todos/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """API route to retrieve a specific task by ID."""
    try:
        task = find_task(task_id)
        if task is None:
            abort(404)
        return jsonify({'task found': task})
    except Exception as e:
        log_request_error(500)
        return make_response(jsonify({'error': 'Internal server error'}), 500)

@app.route('/todos', methods=['POST'])
def add_task():
    """API route to add a new task."""
    try:
        if not request.json or not 'title' in request.json:
            abort(400)
        new_task = insert_task(request.json['title'], request.json.get('description', ''))
        log_task_operation('created')
        return jsonify({'newly added task': new_task}), 201
    except Exception as e:
        log_request_error(500)
        return make_response(jsonify({'error': 'Internal server error'}), 500)

@app.route('/todos/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """API route to update an existing task."""
    try:
        task = find_task(task_id)
        if task is None:
            abort(404)
        if not request.json:
            abort(400)
        task['title'] = request.json.get('title', task['title'])
        task['description'] = request.json.get('description', task['description'])
        task['is_done'] = int(request.json.get('is_done', int(task['is_done'])))
        updated_task = change_task(task)
        log_task_operation('updated')
        return jsonify({'updated task': updated_task})
    except Exception as e:
        log_request_error(500)
        return make_response(jsonify({'error': 'Internal server error'}), 500)

@app.route('/todos/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """API route to delete a task."""
    try:
        task = find_task(task_id)
        if task is None:
            abort(404)
        result = remove_task(task)
        if result:
            log_task_operation('deleted')
        else:
            log_request_error(500)
        return jsonify({'result': result})
    except Exception as e:
        log_request_error(500)
        return make_response(jsonify({'error': 'Internal server error'}), 500)

@app.errorhandler(404)
def not_found(error):
    """Error handler for 404 errors."""
    log_request_error(404)
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    """Error handler for 400 errors."""
    log_request_error(400)
    return make_response(jsonify({'error': 'Bad request'}), 400)

if __name__ == '__main__':
    init_todo_db()

    app.run(host='0.0.0.0', port=80)