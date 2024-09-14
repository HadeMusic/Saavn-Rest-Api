import requests
from rich import print

r = requests.get('https://hayqbhgr.slider.kz/vk_auth.php?q=How%20Could%20I%20Stay%20')



print(r.json())


