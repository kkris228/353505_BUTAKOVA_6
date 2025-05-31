from django.core.management.base import BaseCommand
from core.services import NewsService

class Command(BaseCommand):
    help = 'Fetches latest transportation news from NewsAPI'

    def handle(self, *args, **options):
        self.stdout.write('Fetching news...')
        success = NewsService.fetch_transportation_news()
        
        if success:
            self.stdout.write(self.style.SUCCESS('Successfully fetched news'))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch news')) 