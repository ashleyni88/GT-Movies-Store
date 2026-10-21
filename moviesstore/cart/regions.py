REGIONS = [
    {
        "code": "northeast",
        "name": "Northeast",
        "lat": 42.0,
        "lng": -74.0,
    },
    {
        "code": "southeast",
        "name": "Southeast",
        "lat": 33.0,
        "lng": -84.0,
    },
    {
        "code": "midwest",
        "name": "Midwest",
        "lat": 42.0,
        "lng": -93.0,
    },
    {
        "code": "southwest",
        "name": "Southwest",
        "lat": 34.0,
        "lng": -108.0,
    },
    {
        "code": "west",
        "name": "West",
        "lat": 41.0,
        "lng": -119.0,
    },
]

REGION_CHOICES = [
    (region["code"], region["name"])
    for region in REGIONS
]
