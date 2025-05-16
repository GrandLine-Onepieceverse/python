from flask import Flask, jsonify, request, abort
import json
import os
from functools import wraps
# Add CORS support to allow cross-origin requests
from flask_cors import CORS
import logging
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Enable CORS for all routes
CORS(app)

# Add this after the app initialization
@app.before_request
def log_request_info():
    logger.info('Request: %s %s', request.method, request.path)

# Simple in-memory data storage (in a real app, use a database)
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize data files if they don't exist
def init_data_files():
    data_files = {
        'pirates.json': [
            {
                "id": 1,
                "name": "Straw Hat Pirates",
                "logo": "/placeholder.svg?height=100&width=100",
                "description": "A notorious pirate crew led by Monkey D. Luffy, seeking the One Piece treasure.",
                "members": [
                    {
                        "id": 1,
                        "name": "Monkey D. Luffy",
                        "role": "Captain",
                        "bounty": 1500000000,
                        "image": "/placeholder.svg?height=80&width=80",
                        "status": "active",
                        "devilFruit": "Gomu Gomu no Mi",
                        "origin": "East Blue, Foosha Village",
                        "specialty": "Fighting"
                    },
                    {
                        "id": 2,
                        "name": "Roronoa Zoro",
                        "role": "Swordsman",
                        "bounty": 320000000,
                        "image": "/placeholder.svg?height=80&width=80",
                        "status": "active",
                        "devilFruit": "",
                        "origin": "East Blue",
                        "specialty": "Swordsmanship"
                    },
                    {
                        "id": 3,
                        "name": "Nami",
                        "role": "Navigator",
                        "bounty": 66000000,
                        "image": "/placeholder.svg?height=80&width=80",
                        "status": "active",
                        "devilFruit": "",
                        "origin": "East Blue, Cocoyasi Village",
                        "specialty": "Navigation"
                    }
                ],
                "sea": "East Blue",
                "status": "active",
                "shipName": "Thousand Sunny",
                "baseLocation": "Grand Line",
                "yearFounded": 1522,
                "alliances": ["Heart Pirates"]
            },
            {
                "id": 2,
                "name": "Heart Pirates",
                "logo": "/placeholder.svg?height=100&width=100",
                "description": "A pirate crew led by Trafalgar Law, a powerful Warlord of the Sea.",
                "members": [
                    {
                        "id": 1,
                        "name": "Trafalgar D. Water Law",
                        "role": "Captain",
                        "bounty": 500000000,
                        "image": "/placeholder.svg?height=80&width=80",
                        "status": "active",
                        "devilFruit": "Ope Ope no Mi",
                        "origin": "North Blue, Flevance",
                        "specialty": "Medicine"
                    },
                    {
                        "id": 2,
                        "name": "Bepo",
                        "role": "Navigator",
                        "bounty": 500,
                        "image": "/placeholder.svg?height=80&width=80",
                        "status": "active",
                        "devilFruit": "",
                        "origin": "Zou",
                        "specialty": "Martial Arts"
                    }
                ],
                "sea": "North Blue",
                "status": "active",
                "shipName": "Polar Tang",
                "baseLocation": "Grand Line",
                "yearFounded": 1520,
                "alliances": ["Straw Hat Pirates"]
            }
        ],
        'marines.json': [
            {
                "id": 1,
                "name": "Fleet Admiral Akainu",
                "rank": "Fleet Admiral",
                "specialty": "Magma-Magma Fruit User",
                "image": "/placeholder.svg?height=100&width=100",
                "status": "active",
                "baseLocation": "Marine Headquarters",
                "division": "Main Force",
                "yearsOfService": 35,
                "achievements": ["Defeated Whitebeard Pirates", "Survived Revolutionary Army attack"],
                "devilFruit": "Magu Magu no Mi",
                "subordinates": ["Admiral Kizaru", "Admiral Fujitora", "Admiral Ryokugyu"]
            },
            {
                "id": 2,
                "name": "Admiral Kizaru",
                "rank": "Admiral",
                "specialty": "Light-Light Fruit User",
                "image": "/placeholder.svg?height=100&width=100",
                "status": "active",
                "baseLocation": "Marine Headquarters",
                "division": "Main Force",
                "yearsOfService": 30,
                "achievements": ["Defeated Supernovas at Sabaody"],
                "devilFruit": "Pika Pika no Mi",
                "subordinates": []
            },
            {
                "id": 3,
                "name": "Vice Admiral Garp",
                "rank": "Vice Admiral",
                "specialty": "Haki Master",
                "image": "/placeholder.svg?height=100&width=100",
                "status": "active",
                "baseLocation": "Marine Headquarters",
                "division": "Training Division",
                "yearsOfService": 40,
                "achievements": ["Cornered Gol D. Roger multiple times", "Hero of the Marines"],
                "devilFruit": "",
                "subordinates": ["Koby", "Helmeppo"]
            },
            {
                "id": 4,
                "name": "Captain Tashigi",
                "rank": "Captain",
                "specialty": "Swordsmanship",
                "image": "/placeholder.svg?height=100&width=100",
                "status": "active",
                "baseLocation": "G-5",
                "division": "G-5",
                "yearsOfService": 10,
                "achievements": ["Collected famous swords"],
                "devilFruit": "",
                "subordinates": []
            }
        ],
        'world-gov.json': [
            {
                "id": 1,
                "name": "Taib Hasan Alif",
                "title": "Five Elders Member",
                "description": "One of the highest-ranking officials in the World Government, making crucial decisions that affect the entire world.",
                "location": "Mariejois, Bangladesh",
                "image": "/placeholder.svg?height=200&width=200",
                "status": "active",
                "organization": "Five Elders",
                "authority": ["Policy Making", "Military Command", "Judicial Oversight"],
                "yearsInPosition": 15,
                "specialAbilities": ["Haki", "Strategic Mind"],
                "affiliations": ["World Government", "Five Elders"]
            },
            {
                "id": 2,
                "name": "Riyadh",
                "title": "Commander-in-Chief",
                "description": "The supreme military commander of all World Government forces, including the Marines and Cipher Pol.",
                "location": "Navy Headquarters, Bangladesh",
                "image": "/placeholder.svg?height=200&width=200",
                "status": "active",
                "organization": "World Government",
                "authority": ["Military Command", "Intelligence"],
                "yearsInPosition": 8,
                "specialAbilities": ["Martial Arts", "Strategic Mind"],
                "affiliations": ["World Government", "Marines"]
            }
        ],
        'bounties.json': {
            "topBounties": [
                {
                    "id": 1,
                    "name": "Monkey D. Luffy",
                    "bounty": 1500000000,
                    "crew": "Straw Hat Pirates",
                    "crewId": 1,
                    "role": "Captain",
                    "image": "/placeholder.svg?height=80&width=80",
                    "sea": "Grand Line"
                },
                {
                    "id": 2,
                    "name": "Trafalgar D. Water Law",
                    "bounty": 500000000,
                    "crew": "Heart Pirates",
                    "crewId": 2,
                    "role": "Captain",
                    "image": "/placeholder.svg?height=80&width=80",
                    "sea": "North Blue"
                },
                {
                    "id": 3,
                    "name": "Roronoa Zoro",
                    "bounty": 320000000,
                    "crew": "Straw Hat Pirates",
                    "crewId": 1,
                    "role": "Swordsman",
                    "image": "/placeholder.svg?height=80&width=80",
                    "sea": "East Blue"
                },
                {
                    "id": 4,
                    "name": "Nami",
                    "bounty": 66000000,
                    "crew": "Straw Hat Pirates",
                    "crewId": 1,
                    "role": "Navigator",
                    "image": "/placeholder.svg?height=80&width=80",
                    "sea": "East Blue"
                },
                {
                    "id": 5,
                    "name": "Bepo",
                    "bounty": 500,
                    "crew": "Heart Pirates",
                    "crewId": 2,
                    "role": "Navigator",
                    "image": "/placeholder.svg?height=80&width=80",
                    "sea": "North Blue"
                }
            ],
            "topSea": "Grand Line"
        }
    }
    
    for filename, data in data_files.items():
        file_path = os.path.join(DATA_DIR, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

init_data_files()

# Simple authentication middleware
def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        # In a real app, validate a proper token
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# Helper functions
def read_data(filename):
    try:
        with open(os.path.join(DATA_DIR, filename), 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def write_data(filename, data):
    with open(os.path.join(DATA_DIR, filename), 'w') as f:
        json.dump(data, f, indent=2)

# Routes
@app.route('/api/pirates', methods=['GET'])
def get_pirates():
    pirates = read_data('pirates.json')
    return jsonify(pirates)

@app.route('/api/pirates', methods=['POST', 'PUT'])
@auth_required
def update_pirates():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    write_data('pirates.json', data)
    return jsonify({"message": "Pirates data updated successfully"})

@app.route('/api/marines', methods=['GET'])
def get_marines():
    marines = read_data('marines.json')
    return jsonify(marines)

@app.route('/api/marines', methods=['POST', 'PUT'])
@auth_required
def update_marines():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    write_data('marines.json', data)
    return jsonify({"message": "Marines data updated successfully"})

@app.route('/api/world-gov', methods=['GET'])
def get_world_gov():
    world_gov = read_data('world-gov.json')
    return jsonify(world_gov)

@app.route('/api/world-gov', methods=['POST', 'PUT'])
@auth_required
def update_world_gov():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    write_data('world-gov.json', data)
    return jsonify({"message": "World Government data updated successfully"})

# New endpoint for top bounties
@app.route('/api/bounties/top', methods=['GET'])
def get_top_bounties():
    bounties_data = read_data('bounties.json')
    return jsonify(bounties_data)

@app.route('/api/bounties/top', methods=['POST', 'PUT'])
@auth_required
def update_top_bounties():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    write_data('bounties.json', data)
    return jsonify({"message": "Top bounties data updated successfully"})

# Add this new endpoint for data backup
@app.route('/api/backup', methods=['GET'])
@auth_required
def backup_data():
    try:
        backup = {
            'pirates': read_data('pirates.json'),
            'marines': read_data('marines.json'),
            'world-gov': read_data('world-gov.json'),
            'bounties': read_data('bounties.json')
        }
        return jsonify(backup)
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        return jsonify({"error": f"Failed to create backup: {str(e)}"}), 500

# Add this new endpoint for data restoration
@app.route('/api/restore', methods=['POST'])
@auth_required
def restore_data():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    try:
        data = request.get_json()
        
        if 'pirates' in data:
            write_data('pirates.json', data['pirates'])
        
        if 'marines' in data:
            write_data('marines.json', data['marines'])
        
        if 'world-gov' in data:
            write_data('world-gov.json', data['world-gov'])
            
        if 'bounties' in data:
            write_data('bounties.json', data['bounties'])
        
        return jsonify({"message": "Data restored successfully"})
    except Exception as e:
        logger.error(f"Error restoring data: {str(e)}")
        return jsonify({"error": f"Failed to restore data: {str(e)}"}), 500

# Modify the health check endpoint to include more information
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Check if data files exist and are readable
        pirates_data = read_data('pirates.json')
        marines_data = read_data('marines.json')
        world_gov_data = read_data('world-gov.json')
        bounties_data = read_data('bounties.json')
        
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "data_counts": {
                "pirates": len(pirates_data),
                "marines": len(marines_data),
                "world_gov": len(world_gov_data),
                "bounties": len(bounties_data.get("topBounties", [])) if isinstance(bounties_data, dict) else 0
            },
            "timestamp": datetime.datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }), 500
        
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5328))  # 5328 is fallback for local use
    app.run(host='0.0.0.0', port=port, debug=True)

