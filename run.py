# from app import create_app

# app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True)

from app import create_app
import app.controllers.auth.auth_controller as test
print(test)

app = create_app()
print(" RUN.PY IS EXECUTING")
print(" APP CREATED")
print(app.url_map)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)