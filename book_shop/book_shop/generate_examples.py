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

users = []
for _ in range(10):
    username = fake.user_name()
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.email()
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


authors = []
for _ in range(5):
    author = Author(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        description=fake.paragraph(),
        birth_date=fake.date_of_birth(minimum_age=20, maximum_age=70),
        nationality=fake.country(),
        website=fake.url(),
        photo="/static/logo.png",
        created_by=User.objects.first(),
    )
    author.save()
    authors.append(author)

critics = []
for _ in range(5):
    critic = Critic(
        first_name=fake.first_name(),
        last_name=fake.last_name(),
        description=fake.paragraph(),
        birth_date=fake.date_of_birth(minimum_age=20, maximum_age=70),
        expertise_area=fake.word(),
        nationality=fake.country(),
        website=fake.url(),
        photo=None,
        created_by=User.objects.first(),
    )
    critic.save()  #
    critics.append(critic)

books = []
for author in authors:
    for _ in range(3):
        book = Book(
            title=fake.sentence(nb_words=3),
            author=author,
            date_published=fake.date_between(start_date="-5y", end_date="today"),
            isbn=fake.isbn13(),
            pages=fake.random_int(min=100, max=500),
            language=fake.language_name(),
            summary=fake.paragraph(),
            rating=random.uniform(0.0, 5.0),
            created_by=User.objects.first(),
        )
        book.save()
        books.append(book)

for author in authors[:2]:
    for _ in range(2):
        award = Award(
            name=fake.word().capitalize() + " Award",
            description=fake.paragraph(),
            year_awarded=random.randint(2000, date.today().year),
            author=author,
            created_by=User.objects.first(),
        )
        award.save()

reviews = []
for author in authors[:2]:
    for critic in critics:
        review = Review(
            content_type=ContentType.objects.get_for_model(Author),
            object_id=author.id,
            content=f"This is a review for {author.name}.",
            critic=critic,
            created_by=User.objects.first(),
        )
        review.save()
        reviews.append(review)
for book in books[:3]:
    for critic in critics:
        review = Review(
            content_type=ContentType.objects.get_for_model(Book),
            object_id=book.id,
            content=f"This is a review for the book '{book.title}'.",
            critic=critic,
            created_by=User.objects.first(),
        )
        review.save()
        reviews.append(review)


for review in reviews:
    for user in users[:3]:
        reaction = Reaction(
            review=review,
            reaction_type=random.choice(
                [Reaction.ReactionType.LIKE, Reaction.ReactionType.DISLIKE]
            ),
            created_by=user,
        )
        reaction.save()

print("Data generated successfully.")
