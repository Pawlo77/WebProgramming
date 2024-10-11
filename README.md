# WebProgramming
Programming of WWW Applications course for DS studies in Winter 2024/25.

Details are available in [raport](/raport/raport.pdf).

# Project Requirements
- allow users login and password reset
- there are a normal user, manager and backend admin roles 
- the application allows only the logged-in user to access restricted resources
- at least 2 tables with items browsable by the regular user, which can be filtered 
- the application is aesthetically pleasing 
- the application is responsive (i.e. adapted to at least two resolutions - e.g. computer and tablet or computer and smartphone)
- all forms data is validated
- the application allows you to save or modify records
- use of AJAX technology or similar technique
- The application follow good programming practices
- The application has no difficulty in deployment on a separate machine
- Automatic tests
- short report with idea outline, dataflow and main views screenshots
- source codes

# Project Deployment

## Using docker

```bash
docker build -t "book-shop" .

```

## Natively

```bash

# in the same dir as readme
pip install -r requirements.txt

# in book_shop home dir (one with manager.py)
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
python manage.py shell < book_shop/generate_examples.py
python manage.py runserver --insecure               

```