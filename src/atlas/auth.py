import os
import requests

# Third party imports
from cachetools import cached, TTLCache
from gql import Client, AIOHTTPTransport

# Credentials for authenticating to Atlas
ATLAS_LABBY_USERNAME = os.environ["ATLAS_LABBY_USERNAME"]
ATLAS_LABBY_PASSWORD = os.environ["ATLAS_LABBY_PASSWORD"]

AUTHENTICATION_ENDPOINT = "https://auth.lambdaschool.com/sign-in"
ATLAS_ENDPOINT = "https://api.lambdaschool.com/atlas/graphql/"


@cached(cache=TTLCache(maxsize=1024, ttl=600))
def client():
    """Returns a ready to use instance of a GQL client for querying Atlas"""
    jwt = __get_jwt()

    # Create the transport for executing queries
    transport = AIOHTTPTransport(
        url=f"{ATLAS_ENDPOINT}",
        headers={
            "Authorization": f"Bearer {jwt}",
            "apollographql-client-name": "labby",
            "apollographql-client-version": "1.0",
        },
    )

    print(f"Transport headers: {transport.headers}")

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=False)

    return client


def __get_jwt():
    """Authenticates and returns the JWT for calling Atlas"""
    print(f"Authenticating to Atlas endpoint: {AUTHENTICATION_ENDPOINT}")

    # The data we'll be posting
    post_data = {"email": ATLAS_LABBY_USERNAME, "password": ATLAS_LABBY_PASSWORD}

    # Get a session and post our credentials
    session = requests.session()
    response = session.post(AUTHENTICATION_ENDPOINT, data=post_data)

    print(f"Response from Atlas authentication: {response.content}")

    jwt_cookie = response.cookies["jwt.lambdaschool.com"]
    print(f"JWT from Atlas authentication: {jwt_cookie}")

    return jwt_cookie
