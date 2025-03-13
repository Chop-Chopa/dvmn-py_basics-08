from geopy import distance
from dotenv import load_dotenv
import os
import folium
import json
import requests


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def load_coffee_shops(file_path):
    with open(file_path, "r") as my_file:
        return json.loads(my_file.read())


def calculate_distances(coord_place_one, coffee_shops):
    return [{
        'title': name['Name'],
        'distance': distance.distance(coord_place_one, name['geoData']['coordinates'][::-1]).km,
        'latitude': name['Latitude_WGS84'],
        'longitude': name['Longitude_WGS84']
    } for name in coffee_shops]


def get_distance(shop):
    return shop['distance']


def create_map(coord_place_one, closest_coffee_shops, place_one):
    m = folium.Map(coord_place_one, zoom_start=12)
    folium.Marker(
        location=coord_place_one,
        tooltip="Click me!",
        popup=place_one,
        icon=folium.Icon(color="red"),
    ).add_to(m)

    for shop in closest_coffee_shops:
        folium.Marker(
            location=(shop['latitude'], shop['longitude']),
            tooltip="Click me!",
            popup=shop['title'],
            icon=folium.Icon(color="green"),
        ).add_to(m)

    return m


def main():
    global apikey

    load_dotenv()
    apikey = os.getenv("YANDEX_API_KEY")

    place_one = input("Введите адрес: ")
    coffee_shops_data = load_coffee_shops("coffee.json")
    coord_place_one = fetch_coordinates(apikey, place_one)[::-1]
    coffee_shops = calculate_distances(coord_place_one, coffee_shops_data)

    closest_coffee_shops = sorted(coffee_shops, key=get_distance)[:5]

    m = create_map(coord_place_one, closest_coffee_shops, place_one)

    m.save("index.html")


if __name__ == "__main__":
    main()

