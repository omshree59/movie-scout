import os
import urllib.request

POSTERS_DIR = r"d:\CODE79HACK WEB DEV SECRET HACK SIGMA\MovieScout\frontend\public\posters"
os.makedirs(POSTERS_DIR, exist_ok=True)

IMAGES = {
    "cloy.jpg": "https://image.tmdb.org/t/p/w500/A02zEUZ1Ue1oYdGatP5yBngX2Z.jpg",
    "goblin.jpg": "https://image.tmdb.org/t/p/w500/2jPZtUe706MIs5uN2qtoMh4Hk9R.jpg",
    "squid.jpg": "https://image.tmdb.org/t/p/w500/dDlEmu3EZ0PbrByd2V05cqzZXmP.jpg",
    "dots.jpg": "https://image.tmdb.org/t/p/w500/tL0jB24y5K2w2f5kS2qToF8gW3v.jpg",
    "iotnbo.jpg": "https://image.tmdb.org/t/p/w500/2L2A6S37M61Nl5bXYu4O6M3h8S4.jpg",
    "itaewon.jpg": "https://image.tmdb.org/t/p/w500/yMw53nOfE2w3R10uG9W0l8WfRGu.jpg",
    "vincenzo.jpg": "https://image.tmdb.org/t/p/w500/lOrQhQjP5FjN6s0BZyX9Ym8P63A.jpg",
    "reply.jpg": "https://image.tmdb.org/t/p/w500/mHnt1Z1B4yNIf6M3A58WdZkS4X1.jpg",
    "hospital.jpg": "https://image.tmdb.org/t/p/w500/m1i3H08eM1Xq5zR6z4G1t7L22D4.jpg",
    "mister.jpg": "https://image.tmdb.org/t/p/w500/1N1xV3h7X3R3X4G8W4tZ9w0n3Y.jpg",
    "signal.jpg": "https://image.tmdb.org/t/p/w500/w1y9Z6Q6T2tP5oO6H1G6a0d4Y1f.jpg",
    "sunshine.jpg": "https://image.tmdb.org/t/p/w500/wP1N2Y9P0O0X3V2G2Q5N4J9U0P1.jpg",
    "kingdom.jpg": "https://image.tmdb.org/t/p/w500/zSpAFIeT1DhuVfI3L26gWeOq1XJ.jpg",
    "glory.jpg": "https://image.tmdb.org/t/p/w500/jWe0PZ8CnaE9GshvNokqRj5A0p4.jpg",
    "sweet.jpg": "https://image.tmdb.org/t/p/w500/yD1b0B4d9XtyM1Iu1P75eLzZByE.jpg",
    "banner.jpg": "https://image.tmdb.org/t/p/original/bKxiLHTuXheXfcA9kZf1Zq4kEDj.jpg"
}

opener = urllib.request.build_opener()
opener.addheaders = [('User-agent', 'Mozilla/5.0')]
urllib.request.install_opener(opener)

for name, url in IMAGES.items():
    path = os.path.join(POSTERS_DIR, name)
    # Use weserv.nl proxy to bypass blocks
    proxy_url = "https://images.weserv.nl/?url=" + url.replace("https://", "")
    try:
        print(f"Downloading {name} via proxy...")
        urllib.request.urlretrieve(proxy_url, path)
    except Exception as e:
        print(f"Failed to download {name}: {e}")
