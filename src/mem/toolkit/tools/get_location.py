import ipapi


async def get_location_data(**args):
    """Get the user's location based on their IP address."""
    location = ipapi.location()
    if location:
        return {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "city": location["city"],
        }


if __name__ == "__main__":
    loco = get_location_data()
    print(f"Location: {loco}")
