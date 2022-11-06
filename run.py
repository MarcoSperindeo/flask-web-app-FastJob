from fastjob import create_app, db

app = create_app()

with app.app_context():
    db.create_all()

# we could have passed a Configuration object as an argument.
# If no argument is passed, the Config class we created will be used as default

if __name__ == '__main__':
    app.run(debug=True)
