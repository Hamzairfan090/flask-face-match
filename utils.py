import requests
import os
from deepface import DeepFace
from PIL import Image
from io import BytesIO
from config import AIRTABLE_BASE_ID, TABLE_NAME, HEADERS

TEMP_FOLDER = "temp_images"
os.makedirs(TEMP_FOLDER, exist_ok=True)

# === Fetch stored images from Airtable (Requester Table) ===
def Requester_fetch_images_from_airtable():
    print("\nFetching data from Airtable (Requester Table)...\n")
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print(" Error fetching data from Airtable (Requester):", response.text)
        return []

    print("Fetched data successfully from Airtable (Requester Table)\n")
    records = response.json().get("records", [])

    stored_images = []
    for record in records:
        fields = record.get("fields", {})
        stored_images.append({
            "id": fields.get("ID"),
            "name": fields.get("Name", "Unknown"),
            "phone": fields.get("Number", "N/A"),
            "age": fields.get("Age", "N/A"),
            "gender": fields.get("Gender", "N/A"),
            "status": fields.get("Status", "N/A"),
            "image_url": fields.get("Image 1", ""),
            "image_url_2": fields.get("Image 2", ""),
            "document_url": fields.get("Doc", ""),
            "found_by": fields.get("Name", "Unknown"),
            "found_phone": fields.get("Number", "N/A")
        })

    return stored_images


# === Fetch stored images from Airtable (Finder Table) ===
def finder_fetch_images_from_airtable():
    print("\nFetching data from Airtable (Finder Table)...\n")
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/Finder"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("Error fetching data from Airtable (Finder):", response.text)
        return []

    print("Fetched data successfully from Airtable (Finder Table)\n")
    records = response.json().get("records", [])

    stored_images = []
    for record in records:
        fields = record.get("fields", {})
        stored_images.append({
            "id": fields.get("ID"),
            "name": fields.get("Name", "Unknown"),
            "phone": fields.get("Number", "N/A"),
            "age": fields.get("Age", "N/A"),
            "gender": fields.get("Gender", "N/A"),
            "status": fields.get("Status", "N/A"),
            "image_url": fields.get("Image 1", ""),
            "image_url_2": fields.get("Image 2", ""),
            "document_url": fields.get("Doc", ""),
            "found_by": fields.get("Name", "Unknown"),
            "found_phone": fields.get("Number", "N/A")
        })

    return stored_images


# === Download image from URL ===
def download_image(image_url, filename):
    try:
        print(f"\nDownloading image from URL: {image_url}...\n")
        response = requests.get(image_url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            filepath = os.path.join(TEMP_FOLDER, filename)
            img.save(filepath)
            print(f"Downloaded image saved at: {filepath}\n")
            return filepath
        else:
            print(f"Failed to download image: {image_url}\n")
    except Exception as e:
        print(f"Error downloading image: {e}\n")
    return None


# === Face Matching ===
def match_faces(requester_image_url1, requester_image_url2, stored_images):
    print("\n===========================")
    print("Starting face matching process...\n")
    print("===========================\n")

    requester_image_path1 = download_image(requester_image_url1, "requester1.jpg") if requester_image_url1 else None
    requester_image_path2 = download_image(requester_image_url2, "requester2.jpg") if requester_image_url2 else None

    if not requester_image_path1 and not requester_image_path2:
        print("No images provided for matching.\n")
        return {"match_found": False, "message": "No requester images provided."}

    def try_match(img1, img2, person):
        try:
            print(f"\nComparing {img1} with {img2}...\n")
            result = DeepFace.verify(
                img1,
                img2,
                enforce_detection=False,
                threshold=0.3,
                model_name='Facenet512'
            )
            print(f"DeepFace verification result: {result}\n")
            if result.get("verified"):
                distance = result.get("distance")
                confidence = max(0, 1 - distance / 0.3) if distance is not None else None
                print(f"Match found! Confidence: {confidence}, Distance: {distance}\n")
                return {
                    "match_found": True,
                    "confidence": confidence,
                    "distance": distance,
                    "matched_person": person
                }
        except Exception as e:
            print(f"Error in DeepFace verification: {e}\n")
        return None

    # === Step 1: Compare Requester Image 1 with all Image 1s in Airtable ===
    print("Step 1: Comparing Requester Image 1 with Image 1s from Airtable...\n")
    for person in stored_images:
        stored_path1 = download_image(person.get("image_url"), f"{person['id']}_1.jpg") if person.get("image_url") else None

        if requester_image_path1 and stored_path1:
            match = try_match(requester_image_path1, stored_path1, person)
            if match:
                return match

    # === Step 2: Compare Requester Image 2 with all Image 2s in Airtable ===
    print("Step 2: Comparing Requester Image 2 with Image 2s from Airtable...\n")
    for person in stored_images:
        stored_path2 = download_image(person.get("image_url_2"), f"{person['id']}_2.jpg") if person.get("image_url_2") else None

        if requester_image_path2 and stored_path2:
            match = try_match(requester_image_path2, stored_path2, person)
            if match:
                return match

    # === Step 3: Cross-check Requester Image 1 with Image 2s and Requester Image 2 with Image 1s ===
    print("Step 3: Cross-checking Requester Image 1 with Image 2s and Requester Image 2 with Image 1s...\n")
    for person in stored_images:
        stored_path1 = download_image(person.get("image_url"), f"{person['id']}_1.jpg") if person.get("image_url") else None
        stored_path2 = download_image(person.get("image_url_2"), f"{person['id']}_2.jpg") if person.get("image_url_2") else None

        # Cross-check: Requester Image 1 with Image 2
        if requester_image_path1 and stored_path2:
            match = try_match(requester_image_path1, stored_path2, person)
            if match:
                return match

        # Cross-check: Requester Image 2 with Image 1
        if requester_image_path2 and stored_path1:
            match = try_match(requester_image_path2, stored_path1, person)
            if match:
                return match

    print("No match found after all comparisons.\n")
    return {"match_found": False, "message": "No match found"}


# === Fetch Related Data from Airtable ===
def fetch_related_data(matched_id):
    print(f"\nFetching related data for matched person ID: {matched_id}...\n")
    url = f"https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{TABLE_NAME}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code != 200:
        print("Error fetching related data:", response.text)
        return []

    records = response.json().get("records", [])
    for record in records:
        fields = record.get("fields", {})
        if fields.get("ID") == matched_id:
            print(f"Related data for matched person: {fields}\n")
            return [{
                "id": fields.get("ID"),
                "name": fields.get("Name", "Unknown"),
                "phone": fields.get("Number", "N/A"),
                "age": fields.get("Age", "N/A"),
                "gender": fields.get("Gender", "N/A"),
                "status": fields.get("Status", "N/A"),
                "image_url": fields.get("Image 1", ""),
                "image_url_2": fields.get("Image 2", ""),
                "document_url": fields.get("Doc", ""),
                "found_by": fields.get("Found By", "Unknown"),
                "found_phone": fields.get("Found Phone", "N/A")
            }]
    return []
