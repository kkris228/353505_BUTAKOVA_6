import os
import requests
from datetime import datetime, timedelta
from django.conf import settings
from .models import News

class NewsService:
    API_KEY = settings.NEWS_API_KEY
    BASE_URL = "https://newsapi.org/v2/everything"
    
    @classmethod
    def fetch_transportation_news(cls):
        # Search query for transportation and logistics news
        query = "transportation OR logistics OR shipping OR freight OR cargo"
        
        # Get news from the last 7 days
        from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        params = {
            'q': query,
            'apiKey': cls.API_KEY,
            'language': 'en',
            'from': from_date,
            'sortBy': 'publishedAt',
            'pageSize': 10  # Limit to 10 articles
        }
        
        try:
            response = requests.get(cls.BASE_URL, params=params)
            response.raise_for_status()
            articles = response.json().get('articles', [])
            
            # Save articles to database
            for article in articles:
                News.objects.get_or_create(
                    title=article['title'],
                    defaults={
                        'description': article.get('description', ''),
                        'content': article.get('content', ''),
                        'image_url': article.get('urlToImage'),
                        'source_name': article['source']['name'],
                        'source_url': article['url'],
                        'published_at': datetime.strptime(
                            article['publishedAt'], 
                            '%Y-%m-%dT%H:%M:%SZ'
                        )
                    }
                )
            
            return True
            
        except Exception as e:
            print(f"Error fetching news: {str(e)}")
            return False 

class JokeService:
    """Сервис для получения случайных шуток"""
    API_URL = "https://official-joke-api.appspot.com/random_joke"
    
    @classmethod
    def get_random_joke(cls):
        try:
            response = requests.get(cls.API_URL)
            response.raise_for_status()
            joke_data = response.json()
            return {
                'setup': joke_data.get('setup', ''),
                'punchline': joke_data.get('punchline', ''),
                'type': joke_data.get('type', 'general')
            }
        except Exception as e:
            print(f"Error fetching joke: {str(e)}")
            return {
                'setup': 'Why did the cargo truck feel lonely?',
                'punchline': 'Because it had no trailer!',
                'type': 'general'
            }  # Fallback joke if API fails 