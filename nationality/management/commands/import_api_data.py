import requests
from django.core.management.base import BaseCommand
from nationality.models import Nationality

class Command(BaseCommand):
    help = 'Fetch and populate nationality data from an API'

    def handle(self, *args, **options):
        name = "smith"
        api_url = f"https://api.nationalize.io/?name={name}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            self.populate_nationality(data)
            # Write message to terminal
            self.stderr.write(self.style.SUCCESS('Successfully populated data'))
        else:
            self.stdout.write(self.style.ERROR("Failed to fetch data"))

    def populate_nationality(self, data):
        # Get the 'country' key from the response object
        country_data = data.get("country", [])

        for item in country_data:
            country_id = item.get("country_id")
            probability = item.get("probability")

            # Check for valid probability number
            try:
                probability = float(probability)
            except (TypeError, ValueError):
                self.stdout.write(self.style.WARNING(f"Invalid probability for country {country_id}"))
                continue
            
            # Create or update a record for the database
            nationality, created = Nationality.objects.update_or_create(
                # Key used to find the existing record
                country_id = country_id,
                # If record exists, update attributes in 'defaults' dictionary
                defaults = {"probability": probability}
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Added {country_id}"))
            else:
                self.stdout.write(self.style.SUCCESS(f"Updated {country_id}"))
