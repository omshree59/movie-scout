import os
import json
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

IMAGES = {
    "cloy": "https://image.tmdb.org/t/p/w500/A02zEUZ1Ue1oYdGatP5yBngX2Z.jpg",
    "goblin": "https://image.tmdb.org/t/p/w500/2jPZtUe706MIs5uN2qtoMh4Hk9R.jpg",
    "squid": "https://image.tmdb.org/t/p/w500/dDlEmu3EZ0PbrByd2V05cqzZXmP.jpg",
    "dots": "https://image.tmdb.org/t/p/w500/tL0jB24y5K2w2f5kS2qToF8gW3v.jpg",
    "iotnbo": "https://image.tmdb.org/t/p/w500/2L2A6S37M61Nl5bXYu4O6M3h8S4.jpg",
    "itaewon": "https://image.tmdb.org/t/p/w500/yMw53nOfE2w3R10uG9W0l8WfRGu.jpg",
    "vincenzo": "https://image.tmdb.org/t/p/w500/lOrQhQjP5FjN6s0BZyX9Ym8P63A.jpg",
    "reply": "https://image.tmdb.org/t/p/w500/mHnt1Z1B4yNIf6M3A58WdZkS4X1.jpg",
    "hospital": "https://image.tmdb.org/t/p/w500/m1i3H08eM1Xq5zR6z4G1t7L22D4.jpg",
    "mister": "https://image.tmdb.org/t/p/w500/1N1xV3h7X3R3X4G8W4tZ9w0n3Y.jpg",
    "signal": "https://image.tmdb.org/t/p/w500/w1y9Z6Q6T2tP5oO6H1G6a0d4Y1f.jpg",
    "sunshine": "https://image.tmdb.org/t/p/w500/wP1N2Y9P0O0X3V2G2Q5N4J9U0P1.jpg",
    "kingdom": "https://image.tmdb.org/t/p/w500/zSpAFIeT1DhuVfI3L26gWeOq1XJ.jpg",
    "glory": "https://image.tmdb.org/t/p/w500/jWe0PZ8CnaE9GshvNokqRj5A0p4.jpg",
    "sweet": "https://image.tmdb.org/t/p/w500/yD1b0B4d9XtyM1Iu1P75eLzZByE.jpg",
    "banner": "https://image.tmdb.org/t/p/original/bKxiLHTuXheXfcA9kZf1Zq4kEDj.jpg"
}

results = {}

print("Uploading to Cloudinary...")
for name, url in IMAGES.items():
    try:
        response = cloudinary.uploader.upload(url, public_id=f"moviescout_{name}")
        secure_url = response.get("secure_url")
        results[name] = secure_url
        print(f"Uploaded {name}: {secure_url}")
    except Exception as e:
        print(f"Failed to upload {name}: {e}")
        # fallback to stylized placehold.co
        display_name = name.capitalize()
        results[name] = f"https://placehold.co/600x900/141414/E50914?text={display_name}"

with open("cloudinary_urls.json", "w") as f:
    json.dump(results, f, indent=4)

print("Done! URLs saved to cloudinary_urls.json")
