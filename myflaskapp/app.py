from flask import Flask, render_template,request,redirect
from flask_restx import Api, Resource,reqparse
import mysql.connector
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('DB_HOST')
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
db = os.getenv('DB_NAME')

app = Flask(__name__,template_folder='./templates')
@app.route('/')
def index():
     return render_template('index.html')

# db_config = {
#     'host': 'localhost',
#     'user': 'root',
#     'password': 'root',
#     'database': 'bdiplus',
# }

connection = pymysql.connect(
    host=host,
    user=user,
    password=password,
    db=db,
    cursorclass=pymysql.cursors.DictCursor
)

# def execute_query(query):
#     connection = pymysql.connect(db_config)
#     cursor = connection.cursor()
#     cursor.execute(query)
#     cursor.commit()
    
#     result = cursor.fetchall()

#     cursor.close()
#     return result



@app.route('/create')
def create():
     return render_template('taskForm.html')


@app.route("/delete")
def delete():
     return render_template('deleteForm.html')

@app.route("/edit")
def edit():
     return render_template('editForm.html')

@app.route("/search")
def search():
     return render_template("searchByIdForm.html")

@app.route("/error")
def error():
    return render_template("error.html")
     

@app.route('/tasks')
def showAllTasks():
    with connection.cursor() as cursor:
            sql = "SELECT * FROM `tasks`"
            cursor.execute(sql)
            result = cursor.fetchall()
            # print(result)
            return render_template('showAllTasks.html', tasks=result)


@app.route("/create_task",methods=['POST'])
def createTask():
     
     try:
         
        if request.method=="POST":
            
            task_id = request.form.get('task_id')
            task_name = request.form.get('task_name')

            # with connection.cursor() as cursor:
            #     cursor.execute("SELECT * FROM `tasks` WHERE `task_ID` = %s", (task_id,))
            #     existing_task = cursor.fetchone()

            # if existing_task:
                
            #     error_message = f"Task with TaskID {task_id} already exists."
            #     return render_template('500.html', error_message=error_message), 500
            
            with connection.cursor() as cursor:

                cursor.execute("INSERT into `tasks` (`task_ID`,`task_name`) values (%s,%s)",(task_id,task_name))
                connection.commit()
                # console.log("Added success")
                cursor.close()

            
                # print(result)
            return redirect('/tasks')
     except Exception as e:
         error_message = f"An error occurred: {str(e)}"
         return render_template('500.html', error_message=error_message), 500
         

         
@app.route("/delete_task", methods=["POST"])
def deleteTask():
    try:

        if request.method=="POST":
            task_id = request.form.get('task_id')
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM `tasks` WHERE `task_ID` = %s", (task_id,))
                existing_task = cursor.fetchone()

            if existing_task:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE from `tasks` where `task_ID`=%s",task_id)
                    connection.commit()
                    cursor.close()
            else:

                error_message = f"Task with TaskID {task_id} do not exist."
                return render_template('500.html', error_message=error_message), 500
            
                
        return redirect('/tasks')
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return render_template('500.html', error_message=error_message), 500 


@app.route("/edit_task",methods=['POST'])
def editTask():
    try:
         if request.method=="POST":
          
            task_id = request.form.get('task_id')
            task_new_name = request.form.get('task_name')

            print(task_id,task_new_name)
            
            with connection.cursor() as cursor:

                cursor.execute("UPDATE  `tasks` set `task_name`=%s where `task_ID`=%s",(task_new_name,task_id))
                connection.commit()
                # console.log("Added success")
                cursor.close()

        
            # print(result)
            return redirect('/tasks')
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        return render_template('500.html', error_message=error_message), 500
         

@app.route("/search_task", methods=["POST"])
def searchTask():
    try:
        if request.method=="POST":
            task_id = request.form.get('task_id')
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM `tasks` where `task_ID`=%s",task_id)
                result = cursor.fetchone()
                print(result)
                connection.commit()
                cursor.close()
                
            return render_template('showSingleTask.html',task = result)
    except Exception as e:
         error_message = f"An error occurred: {str(e)}"
         return render_template('500.html', error_message=error_message), 500
    

api = Api(app,doc='/swagger')
tasks_ns = api.namespace('tasks', description='Task operations')
create_task_parser = reqparse.RequestParser()
create_task_parser.add_argument('task_id', type=int, required=True, help='The ID of the task')
create_task_parser.add_argument('task_name', type=str, required=True, help='The name of the task')

@tasks_ns.route('/create_task')
class CreateTaskResource(Resource):
    @api.doc(responses={500: 'Internal Server Error'})
    @api.expect(create_task_parser)
    def post(self):
        """
        Create a new task.
        """
        try:
            args = create_task_parser.parse_args()
            task_id = args['task_id']
            task_name = args['task_name']

            # Your existing code for creating a task goes here
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM `tasks` WHERE `task_ID` = %s", (task_id,))
                existing_task = cursor.fetchone()

            if existing_task:
                
                error_message = f"Task with TaskID {task_id} already exists."
                return render_template('500.html', error_message=error_message), 500
            
            with connection.cursor() as cursor:

                cursor.execute("INSERT into `tasks` (`task_ID`,`task_name`) values (%s,%s)",(task_id,task_name))
                connection.commit()
                # console.log("Added success")
                cursor.close()

            return redirect('/tasks')
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return render_template('500.html', error_message=error_message), 500
        
delete_task_parser = api.parser()
delete_task_parser.add_argument('task_id', type=int, location='form', required=True, help='The ID of the task to delete')

@tasks_ns.route('/delete_task')
class DeleteTaskResource(Resource):
    @api.doc(responses={500: 'Internal Server Error'})
    @api.expect(delete_task_parser)
    def post(self):
        """
        Delete a task by ID.
        """
        try:
            args = delete_task_parser.parse_args()
            task_id = args['task_id']

            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM `tasks` WHERE `task_ID` = %s", (task_id,))
                existing_task = cursor.fetchone()

            if existing_task:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM `tasks` WHERE `task_ID`=%s", (task_id,))
                    connection.commit()
                    cursor.close()
            else:
                error_message = f"Task with TaskID {task_id} does not exist."
                return render_template('500.html', error_message=error_message), 500

            return "Successfully Deleted"
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            return render_template('500.html', error_message=error_message), 500

if __name__ == '__main__':
    app.run(debug=True)