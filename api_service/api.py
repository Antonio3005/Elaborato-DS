from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Chiave API di OpenWeatherMap
api_key = 'f5bea9a7cd302abdca838d809883d3eb'

import requests

url = 'https://api.tequila.kiwi.com/v2/search'
headers = {
    'accept': 'application/json',
    'apikey': 'D-ljrLyhPOeM1-eWQWcVliV9mBNListf'
}

params = {
    'fly_from': 'FRA',
    'fly_to': 'PRG',
    'date_from': '01/04/2024',
    'date_to': '03/04/2024',
    'return_from': '04/04/2024',
    'return_to': '06/04/2024',
    'nights_in_dst_from': 2,
    'nights_in_dst_to': 3,
    'max_fly_duration': 20,
    'ret_from_diff_city': True,
    'ret_to_diff_city': True,
    'one_for_city': 0,
    'one_per_date': 0,
    'adults': 2,
    'children': 2,
    'selected_cabins': 'C',
    'mix_with_cabins': 'M',
    'adult_hold_bag': '1,0',
    'adult_hand_bag': '1,1',
    'child_hold_bag': '2,1',
    'child_hand_bag': '1,1',
    'only_working_days': False,
    'only_weekends': False,
    'partner_market': 'us',
    'max_stopovers': 2,
    'max_sector_stopovers': 2,
    'vehicle_type': 'aircraft',
    'limit': 100
}

response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print(f"Error: {response.status_code}, {response.text}")


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')

    if not city:
        return jsonify({'error': 'Specificare una città nella richiesta'}), 400

    # Costruisci l'URL per l'API di OpenWeatherMap
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'

    # Effettua la richiesta all'API di OpenWeatherMap
    response = requests.get(url)
    data = response.json()

    # Verifica se la richiesta ha avuto successo
    if response.status_code == 200:
        weather_info = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
        }
        return jsonify(weather_info)
    else:
        return jsonify({'error': 'Errore durante la richiesta API'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
