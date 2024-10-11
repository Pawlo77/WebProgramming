import random
from datetime import date

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from faker import Faker
from items.models import Award, Book
from people.models import Author, Critic
from reviews.models import Reaction, Review
from users.models import CustomUser

User = get_user_model()
fake = Faker()

roles = [CustomUser.USER, CustomUser.MANAGER, CustomUser.ADMIN]
educations = [
    CustomUser.UNEDUCATED,
    CustomUser.PRIMARY,
    CustomUser.MIDDLE,
    CustomUser.HIGH,
]

# Use sets to track unique usernames and emails
unique_usernames = set()
unique_emails = set()

users = []
for _ in range(100):
    username = fake.user_name()
    # Ensure unique username
    while username in unique_usernames:
        username = fake.user_name()
    unique_usernames.add(username)

    first_name = fake.first_name()
    last_name = fake.last_name()

    email = fake.email()
    # Ensure unique email
    while email in unique_emails:
        email = fake.email()
    unique_emails.add(email)

    password = "Pass123!"
    role = random.choice(roles)
    education = random.choice(educations)
    date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)

    custom_user = CustomUser(
        username=username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        education=education,
        date_of_birth=date_of_birth,
    )
    custom_user.set_password(password)
    custom_user.save()
    users.append(custom_user)

print("Generated 100 users successfully.")

authors = []
for _ in range(20):
    author = Author(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        description=fake.paragraph(),
        birth_date=fake.date_of_birth(minimum_age=20, maximum_age=70),
        nationality=fake.country(),
        website=fake.url(),
        photo="/static/logo.png",
        created_by=random.choice(users),
    )
    author.save()
    authors.append(author)

print("Generated 20 authors successfully.")

critics = []
for _ in range(30):
    critic = Critic(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        description=fake.paragraph(),
        birth_date=fake.date_of_birth(minimum_age=20, maximum_age=70),
        expertise_area=fake.word(),
        nationality=fake.country(),
        website=fake.url(),
        photo=None,
        created_by=random.choice(users),
    )
    critic.save()
    critics.append(critic)

print("Generated 30 critics successfully.")

books = []
for author in authors:
    for _ in range(5):
        book = Book(
            title=fake.sentence(nb_words=3),
            author=author,
            date_published=fake.date_between(start_date="-5y", end_date="today"),
            isbn=fake.isbn13(),
            pages=fake.random_int(min=100, max=500),
            language=fake.language_name(),
            summary=[
                "\n".join(fake.paragraph() for _ in range(1, random.randint(1, 10)))
            ],
            rating=random.uniform(0.0, 5.0),
            created_by=random.choice(users),
        )
        book.save()
        books.append(book)

print("Generated books successfully.")

for i in range(random.randint(len(authors) // 3, len(authors))):
    author = authors[i]
    for _ in range(random.randint(1, 6)):
        award = Award(
            name=fake.word().capitalize() + " Award",
            description=[
                "\n".join(fake.paragraph() for _ in range(1, random.randint(1, 10)))
            ],
            year_awarded=random.randint(2000, date.today().year),
            author=author,
            created_by=random.choice(users),
        )
        award.save()

print("Generated awards successfully.")

reviews = []
for i in range(random.randint(len(authors) // 3, len(authors))):
    author = authors[i]
    for critic in critics:
        review = Review(
            content_type=ContentType.objects.get_for_model(Author),
            object_id=author.id,
            content=f"This is a review for {author.first_name} {author.last_name}."
            + fake.paragraph(),
            critic=critic,
            created_by=random.choice(users),
        )
        review.save()
        reviews.append(review)

print("Generated reviews for authors successfully.")

for i in range(random.randint(len(books) // 3, len(books))):
    book = books[i]
    for critic in critics:
        review = Review(
            content_type=ContentType.objects.get_for_model(Book),
            object_id=book.id,
            content=f"This is a review for the book '{book.title}'.",
            critic=critic,
            created_by=random.choice(users),
        )
        review.save()
        reviews.append(review)

print("Generated reviews for books successfully.")

for review in reviews:
    for i in range(random.randint(len(users) // 3, len(users))):
        user = users[i]
        reaction = Reaction(
            review=review,
            reaction_type=random.choice(
                [Reaction.ReactionType.LIKE, Reaction.ReactionType.DISLIKE]
            ),
            created_by=user,
        )
        reaction.save()

print("Generated reactions successfully.")

print("Data generation completed successfully.")
