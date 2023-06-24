# Django Api example: Forecast Google Trends

In this tutorial we show an example implementation of a REST API in Django for a forecasting model. Here's the [related article](https://effectiveforecasting.com/build-a-forecasting-api-an-example-with-django-and-google-trends/).

For this example we don't use the shared environment at the root of the repository, but we define a custom one inside this folder.

To get started, run the following snippet:
```bash
# Clone the project
git clone git@github.com:davide-burba/effective-forecasting.git

# Move to the right folder
cd tutorials/api-example-django/project

# Launch the app (or just `./manage.py runserver` in a poetry shell)
docker compose up -d

# Create a (super)user for your app (or just `./manage.py createsuperuser`)
docker compose exec django ./manage.py createsuperuser 
```
and connect to `localhost:8000/gtrends`!

