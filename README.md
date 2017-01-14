## Synopsis

This is my solution (Dominick Modica) to the API coding challenge. Entry point is within Vimeo.py.

## Installation

1. Install Python 2.7.12+
2. Ensure your current working directory is at the top level of this project. (Ex: ~/Vimeo)
3. Issue the command 'pip install -r requirements.txt' from your terminal to install project dependencies.
4. Issue the comand 'python Vimeo.py' to startup the server. It should now be running locally and accessible via 127.0.0.1:5000.

## API Routes/Reference
###/user/\<user_id\>:
* GET returns JSON which contains uploaded,liked,and watched videos for the particular user.
* POST utilized to register a new user. Supply ?country=\<country_code\>&&ip=\<ip\>.
* PATCH utilized to edit existing user. Supply   ?country=\<country_code\>&&ip=\<ip\>.
* DELETE deletes the user from the DB who has \<user_id\>.

###/video/\<video_id\>:
* GET Fetches a video watch count analysis grouped by country.

###/country/\<country_name\>:
* GET  returns JSON which contains a list of user IDs for that particular country.

###/trending
* GET calculates and returns the 5 most watched video\'s at any given time.

###/trending-live
* GET calculates and returns the 5 most watched video\'s at any given time (In real time).

## Tests

TODO

## Contributors

Dominick Modica

## License
