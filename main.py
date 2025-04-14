import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # This tells TensorFlow to ignore any GPUs
from flask import Flask, request, jsonify
import requests
from config import MAKE_WEBHOOK_URL
from utils import (
    Requester_fetch_images_from_airtable,
    match_faces,
    fetch_related_data,
    finder_fetch_images_from_airtable,
    clean_temp_folder
)

app = Flask(__name__)

@app.route('/receive_data', methods=['POST'])
def receive_data():
    print("\n===========================")
    print("Received data from API")
    print("===========================\n")

    try:
        data = request.json

        requester_id = data.get("id")
        type = data.get("Type")
        name = data.get("Name")
        phone = data.get("Phone")
        age = data.get("Age")
        gender = data.get("Gender")
        status = data.get("Status")
        image_url1 = data.get("Image1")
        image_url2 = data.get("Image2")
        document_url = data.get("Doc")

        print(f"Type: {type} | Matching with: {'Requester' if type == 'Requester' else 'Finder'}\n")

        stored_images = Requester_fetch_images_from_airtable() if type == "Requester" else finder_fetch_images_from_airtable()

        print("Comparing the images...\n")
        match_result = match_faces(image_url1, image_url2, stored_images)

        if match_result["match_found"]:
            matched_person = match_result["matched_person"]
            related_data = fetch_related_data(matched_person["id"])

            webhook_data = {
                "message": "Match found!",
                "requester_id": requester_id,
                "matched_person": matched_person,
                "related_data": related_data
            }

            print("Match found! Sending data to Make.com...\n")
            try:
                requests.post(MAKE_WEBHOOK_URL, json=webhook_data)
            except Exception as e:
                print(f"Error sending match data to webhook: {e}\n")

            return jsonify({
                "message": " Match found and data sent to webhook!",
                "requester_id": requester_id,
                "matched_person": matched_person
            })

        else:
            webhook_data = {
                "message": "No match found!",
                "requester_id": requester_id,
                "name": name,
                "Type": type,
                "phone": phone,
                "age": age,
                "gender": gender,
                "status": status,
                "image_url_1": image_url1,
                "image_url_2": image_url2,
                "document_url": document_url,
                "related_data": "N/A",
                "store_request": True
            }

            print("No match found. Sending request to store in Airtable...\n")
            try:
                requests.post(MAKE_WEBHOOK_URL, json=webhook_data)
            except Exception as e:
                print(f"Error sending 'no match' data to webhook: {e}\n")

            return jsonify({
                "message": "No match found, storing requester info",
                "requester_id": requester_id,
                "store_request": True
            })

    finally:
        clean_temp_folder()

if __name__ == '__main__':
    print("\n===============================")
    print("Flask server starting on port 5000...")
    print("===============================\n")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
