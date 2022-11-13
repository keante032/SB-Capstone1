****Your Weather****
https://personalized-weather.herokuapp.com/

**API link:** https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/

This site presents basic weather forecast data, weather alerts (storm watches/warnings), and a radar map for a given location.

In addition, any user who chooses to register with an email and password may save a searched location as a favorite (or remove a location from his favorites). The list of favorites appears on the homepage if a user is logged in.

Any user (no need to log in) can search for any location from the homepage. The browser will then be redirected to a page for that location showing the forecast, alerts (if any), and the radar map. From that location page, if the user is logged in, they will have a button available for adding or removing that location as a favorite.

The search bar in the center of the homepage also appears in the navbar for any page other than the homepage, making it convenient for a user to search for another location.

If a user is not logged in, then the register and login buttons are always available in the navbar. If a user is logged in, then the logout button is available in the navbar.

**Tech Stack**
HTML
Bootstrap
Python
Flask
SQLAlchemy
