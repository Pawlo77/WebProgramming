FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /book_shop

COPY requirements.txt /book_shop/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /book_shop/

RUN mkdir -p /book_shop/staticfiles && chmod -R 755 /book_shop/staticfiles

RUN python manage.py collectstatic --noinput

RUN python manage.py migrate

RUN  python manage.py shell < book_shop/generate_examples.py

RUN echo "from django.contrib.auth import get_user_model; \
User = get_user_model(); \
User.objects.filter(username='admin').exists() or \
User.objects.create_superuser('admin', 'admin@example.com', 'admin', first_name='admin', last_name='admin')" \
| python manage.py shell

EXPOSE 8000

CMD ["gunicorn", "--timeout", "120", "--workers", "2", "--threads", "3", "--bind", "0.0.0.0:8000", "book_shop.wsgi:application"]