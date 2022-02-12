import folium
from geopy.geocoders import Nominatim
from bs4 import BeautifulSoup
import requests
import pandas as pd

# Returns a dictionary in the form event:[place, time]


def get_scraped_content():
    url = 'https://www.eventbrite.com/d/wi--madison/events--this-weekend/'
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'html.parser')

    titles = soup.find_all('div', class_='eds-event-card__formatted-name--is-clamped eds-event-card__'
                                         'formatted-name--is-clamped-three eds-text-weight--heavy')
    locations = soup.find_all('div', class_='card-text--truncated__one')
    times = soup.find_all('div', class_='eds-event-card-content__sub-title eds-text-color--ui-orange '
                                        'eds-l-pad-bot-1 eds-l-pad-top-2 eds-text-weight--heavy eds-text-bm')
    event_dict = {}
    title_list = []
    content = ''

    # Fills event_dict with the content above
    for title in titles:
        content = title.text.strip()
        event_dict[title.text.strip()] = []
        title_list.append(content)
    for index, location in enumerate(locations):
        content = location.text.strip().replace(' •', ',')
        event_dict[title_list[index]].append(content)
    for index, time in enumerate(times):
        content = time.text.strip()
        event_dict[title_list[index]].append(content)

    # Removes first and last index in event_dict
    for key, val in event_dict.items():
        event_dict[key].pop(0)
        event_dict[key].pop(len(val) - 1)
    return event_dict

data = get_scraped_content()
dataf = pd.DataFrame.from_dict(data)
addresses = dataf.loc[0].tolist()
events = dataf.columns.values.tolist()
time = dataf.loc[1].tolist()
geolocator = Nominatim(user_agent= "specify_your_app_here")
lats = []
longs = []
valid_events = []
time_events = []

for index, i in enumerate(addresses):

    location = geolocator.geocode(i)

    if location != None:

        valid_events.append(events[index])

        lats.append(location.latitude)

        longs.append(location.longitude)

        time_events.append(time[index])

#create map object
m = folium.Map(location=[43.0731, -89.4012], zoom_start = 12)

#global tooltip
tooltip = 'Click for more info'

# create markers
for i in range(len(valid_events)):
    folium.Marker([lats[i], longs[i]],
                  popup = f'<strong>{valid_events[i]}</strong>'
                          f'<p>{time_events[i]}</p>',
                  tooltip = tooltip,
                  icon = folium.Icon(icon = 'star')).add_to(m)

# Generate map
m.save('map.html')
