# Plex to Radarr Integration

This repository provides a script for integrating Plex watchlist with Radarr. It allows users to automatically add movies from their Plex watchlist to Radarr for automated downloading and management.

## Features

- Fetch Plex watchlist and process movies
- Retrieve TMDB ID for each movie
- Add movies to Radarr using specified quality profile
- Error handling for failed requests

## Prerequisites

Before using this script, make sure you have the following:

- Python 3 installed on your system.
- Radarr installed and configured with an API key.
- Plex server with a valid Plex token.

## Setup Instructions

1. Clone the repository to your local machine or server.
2. Install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```
3. Open the `plex_to_arr.py` file in a text editor.
4. Update the following variables with your own values:
   - `PLEX_TOKEN`: Your Plex token.
   - `RADARR_API_KEY`: Your Radarr API key.
   - `RADARR_URL`: The URL of your Radarr instance.
   - `RADARR_ROOT_FOLDER`: The root folder path where Radarr should save the downloaded movies.
5. Save the changes.

## Usage

To use the script, follow these steps:

1. Make sure Radarr and Plex are running and accessible.
2. Open a terminal or command prompt.
3. Navigate to the directory where the `plex_to_arr.py` file is located.
4. Run the following command to start the script:
   ```
   python plex_to_arr.py
   ```
5. The script will fetch your Plex watchlist and process the movies.
6. For each movie, it will search for the corresponding TMDB ID.
7. If found, the movie will be added to Radarr using the specified quality profile.
8. Check the script output for any errors or status updates.

## Customization

Feel free to customize the script further based on your specific setup and requirements. You can modify the quality profile, add additional error handling, or enhance the functionality as needed.

## Contributions

Contributions to this repository are welcome! If you have any improvements or bug fixes, feel free to submit a pull request.

## Acknowledgements

- The developers and contributors of Radarr, Plex, and TMDB for their fantastic tools and APIs.
