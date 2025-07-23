from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# Данные по районам Кишинёва (на основе реальных исследований 2024-2025)
districts = {
    "Центр": {"price_per_m2": 1628, "description": "Исторический центр города"},
    "Рышкановка": {"price_per_m2": 1444, "description": "Престижный район"},
    "Телецентру": {"price_per_m2": 1325, "description": "Развивающийся район"},
    "Чеканы": {"price_per_m2": 1293, "description": "Жилой район"},
    "Ботаника": {"price_per_m2": 1200, "description": "Популярный район"},
    "Буюканы": {"price_per_m2": 1150, "description": "Спокойный район"},
    "Дурлешты": {"price_per_m2": 1095, "description": "Пригородная зона"},
    "Чокана": {"price_per_m2": 1050, "description": "Развивающийся район"}
}

def get_district(address):
    """Определяет район по адресу"""
    address_lower = address.lower()
    for district in districts:
        if district.lower() in address_lower:
            return district
    return "Ботаника"  # по умолчанию

def calculate_price(district, area, floor, rooms, condition):
    """Рассчитывает стоимость квартиры"""
    base_price = districts[district]['price_per_m2']
    total_price = base_price * area

    # Корректировки по количеству комнат
    if rooms >= 3:
        total_price *= 1.1
    elif rooms == 1:
        total_price *= 0.95

    # Корректировки по этажу
    if floor == 1:
        total_price *= 0.9  # первый этаж дешевле
    elif floor > 8:
        total_price *= 0.95  # высокие этажи немного дешевле

    # Корректировки по состоянию
    condition_multipliers = {
        "без_ремонта": 0.8,
        "белый_вариант": 0.9,
        "евроремонт": 1.2,
        "хорошее": 1.0
    }
    total_price *= condition_multipliers.get(condition, 1.0)

    return round(total_price, 2)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/evaluate', methods=['POST'])
def evaluate():
    try:
        data = request.json
        address = data.get('address', '')
        area = float(data.get('area', 0))
        floor = int(data.get('floor', 1))
        rooms = int(data.get('rooms', 1))
        condition = data.get('condition', 'хорошее')

        if area <= 0:
            return jsonify({'error': 'Площадь должна быть больше 0'}), 400

        district = get_district(address)
        price = calculate_price(district, area, floor, rooms, condition)
        price_per_m2 = districts[district]['price_per_m2']

        return jsonify({
            'success': True,
            'district': district,
            'price': price,
            'price_per_m2': price_per_m2,
            'description': districts[district]['description']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/districts', methods=['GET'])
def get_districts():
    return jsonify(districts)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))