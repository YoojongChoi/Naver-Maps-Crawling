# Restaurant Recommendations Based on Current Location with Naver Maps

## Project Overview

The goal of this project is to collect nearby restaurant information from Naver Maps based on the user's current location. The program will then select the top 3 restaurants for each criterion (rating and number of reviews) and provide this information to the user. The implementation will follow these steps:


1. Determine User Location

- Use the Requests library to obtain the user's IP address and track their location.
Extract location data including latitude and longitude.


2. Access Naver Maps

- Use Selenium to navigate to the Naver Maps website.
- Search for the user’s current location on Naver Maps using their latitude and longitude.


3. Search for Restaurants

- Input "맛집" ("restaurants") in the search bar. Since the search includes latitude and longitude, a list of nearby restaurants will be displayed.
- Scroll down the page to load additional restaurant data.


4. Switch Frames and Extract Data

- To extract detailed information about a restaurant, you should click on a restaurant in the search results to open a detailed information panel.
- To do this, switch to the 'searchIframe' frame. Once the detailed panel appears, switch to the 'entryIframe' frame to extract the information.
- Repeat the process for each restaurant by alternating between 'searchIframe' (to click on restaurants) and 'entryIframe' (to gather details).


5. Collect and Rank Restaurant Data

- Use BeautifulSoup to extract detailed information for each restaurant.
- Extract data such as restaurant name, type, operating status, rating, number of reviews, location, detailed address, and key review phrases.
- Exclude restaurants with a "closed" operating status from the recommendation list.
- Continuously update the top 3 restaurants for both highest ratings and most reviews as data is collected.


6. Output Information

- Display detailed information for the selected top restaurants to the user.

