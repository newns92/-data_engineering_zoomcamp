import requests
from kestra import Kestra

r = requests.get('https://api.github.com/repos/kestra-io/kestra')

gh_stars = r.json()['stargazers_count']

# print(gh_stars)

# Make the output available in the Kestra platform
Kestra.outputs({'gh_stars': gh_stars})