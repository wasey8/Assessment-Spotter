from rest_framework.views import APIView
from django.http import JsonResponse
from .utils import load_fuel_prices, select_fuel_stops, get_coordinates  # Assuming utils.py for reusable code
import requests
from decouple import config

class OptimalRouteView(APIView):
    """
    API view to calculate the optimal route, including refueling stops
    and total fuel cost, between two locations.
    """

    def post(self, request):
        """
        Handle POST requests to calculate and return the optimal route.
        """
        start_location = request.data.get("start_location")
        end_location = request.data.get("end_location")

        if not start_location or not end_location:
            return JsonResponse(
                {"error": "Start and end locations are required."},
                status=400
            )

        # Get coordinates for the start and end locations
        start_location_coordinates = get_coordinates(start_location)
        end_location_coordinates = get_coordinates(end_location)

        if not start_location_coordinates or not end_location_coordinates:
            return JsonResponse(
                {"error": "Unable to retrieve coordinates for the provided locations."},
                status=400
            )
        
        # Step 1: Get route and map using a routing API
        route_data = self.get_route_data(start_location_coordinates, end_location_coordinates)

        if not route_data:
            return JsonResponse(
                {"error": "Could not retrieve route data."},
                status=400
            )

        # Step 2: Calculate refuel points along the route
        fuel_stops, total_fuel_cost = select_fuel_stops(route_data, start_location, end_location)

        # Step 3: Prepare the map URL using google maps
        map_url = self.generate_map_url(start_location_coordinates, end_location_coordinates)

        return JsonResponse({
            "route_map_url": map_url,
            "fuel_stops": fuel_stops,
            "total_fuel_cost": total_fuel_cost,
        })

    def get_route_data(self, start, end):
        """
        Fetch route details between two locations using OSRM or a similar API.
        """
        try:
            url = f"https://router.project-osrm.org/route/v1/driving/{start};{end}?overview=full"
            response = requests.get(url)

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except requests.RequestException as e:
            print(f"Error fetching route data: {e}")
            return None

    def generate_map_url(self, start_location_coordinates, end_location_coordinates):
        """
        Generate a URL using Google Maps Embed API to create an interactive map.
        """
        # Replace with your actual Google Maps API key
        api_key = config("GOOGLEMAPS_API_KEY")

        # Construct the URL for Google Maps Embed API to display the route
        map_url = (
            f"https://www.google.com/maps/embed/v1/directions?"
            f"key={api_key}&origin={start_location_coordinates}"
            f"&destination={end_location_coordinates}"
        )

        return map_url
