import json

# Load the original GeoJSON
with open("nielsen_dma.json") as f:
    geojson = json.load(f)

# Check if Anchorage is already present
ids = {f["id"] for f in geojson["features"]}
if "743" not in ids:
    print("Adding Anchorage polygon...")
    anchorage_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [-151.5, 60.7],
                [-148.5, 60.7],
                [-148.5, 61.7],
                [-151.5, 61.7],
                [-151.5, 60.7]
            ]]
        },
        "properties": {
            "dma": 743,
            "dma1": "Anchorage, AK",
            "dma_name": "Anchorage",
            "latitude": 61.2,
            "longitude": -149.9
        },
        "id": "743"
    }

    geojson["features"].append(anchorage_feature)

    # Save patched file
    with open("nielsen_dma_patched.json", "w") as f_out:
        json.dump(geojson, f_out, indent=2)

    print("Saved to nielsen_dma_patched.json")
else:
    print("Anchorage already present.")
