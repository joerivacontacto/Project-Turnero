import urllib.request
import json
import sys

def get_wheel_url(package, version, pycp="cp311", abi="cp311", platform="manylinux_2_17_x86_64"):
    url = f"https://pypi.org/pypi/{package}/{version}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
            for f in data["urls"]:
                if f["filename"].endswith(".whl") and platform in f["filename"] and abi in f["filename"]:
                    return f["url"], f["filename"]
            # Fallback: any whl for this package
            for f in data["urls"]:
                if f["filename"].endswith(".whl") and "manylinux" in f["filename"]:
                    return f["url"], f["filename"]
    except Exception as e:
        print(f"Error: {e}")
    return None, None

for pkg, ver in [("SQLAlchemy", "2.0.27"), ("python-jose", "3.3.0"), ("passlib", "1.7.4"), ("bcrypt", "4.1.2")]:
    url, fname = get_wheel_url(pkg, ver)
    print(f"{pkg}: {fname} -> {url}")
