import requests

def get_random_joke():
    """
    Получает случайную шутку через API JokeAPI
    Returns:
        dict: Словарь с шуткой, содержащий поля:
            - setup: начало шутки (для двухчастных шуток)
            - delivery: окончание шутки (для двухчастных шуток)
            - joke: полная шутка (для одночастных шуток)
    """
    url = "https://v2.jokeapi.dev/joke/Programming?safe-mode"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверяем на ошибки HTTP
        data = response.json()
        
        if data['error']:
            return {
                'error': True,
                'message': 'Failed to fetch joke'
            }
            
        # Возвращаем шутку в зависимости от её типа
        if data['type'] == 'twopart':
            return {
                'error': False,
                'type': 'twopart',
                'setup': data['setup'],
                'delivery': data['delivery']
            }
        else:
            return {
                'error': False,
                'type': 'single',
                'joke': data['joke']
            }
            
    except requests.RequestException as e:
        return {
            'error': True,
            'message': f'Error fetching joke: {str(e)}'
        }
    except (KeyError, ValueError) as e:
        return {
            'error': True,
            'message': f'Error parsing joke response: {str(e)}'
        } 