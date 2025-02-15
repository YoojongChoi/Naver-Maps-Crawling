## 🔍Project Overview

### 📌 Title
- Restaurant Recommendations Based on Current Location with Naver Maps

### 📌 Objective
- The goal of this project is to collect nearby restaurant information from Naver Maps based on the user's current location. The program will then select the top 3 restaurants for each criterion (rating and number of reviews) and provide this information to the user. The implementation will follow these steps:

### 📌 Duration
- 2024.05 ~ 2024.06

## 🔍Project Flow

### 1. Determine User Location
- Use the Requests library to obtain the user's IP address and track their location.
Extract location data including latitude and longitude.


### 2. Access Naver Maps
- Use Selenium to navigate to the Naver Maps website.
- Search for the user’s current location on Naver Maps using their latitude and longitude.


### 3. Search for Restaurants
- Input "맛집" ("restaurants") in the search bar. Since the search includes latitude and longitude, a list of nearby restaurants will be displayed.
- Scroll down the page to load additional restaurant data.


### 4. Switch Frames and Extract Data

- To extract detailed information about a restaurant, you should click on a restaurant in the search results to open a detailed information panel.
- To do this, switch to the 'searchIframe' frame. Once the detailed panel appears, switch to the 'entryIframe' frame to extract the information.
- Repeat the process for each restaurant by alternating between 'searchIframe' (to click on restaurants) and 'entryIframe' (to gather details).


### 5. Collect and Rank Restaurant Data

- Use BeautifulSoup to extract detailed information for each restaurant.
- Extract data such as restaurant name, type, operating status, rating, number of reviews, location, detailed address, and key review phrases.
- Exclude restaurants with a "closed" operating status from the recommendation list.
- Continuously update the top 3 restaurants for both highest ratings and most reviews as data is collected.


### 6. Output Information
- Display detailed information for the selected top restaurants to the user.

## 🔍Limitations and Improvements
- First, if the structure of Naver Maps changes, the web crawling may not function properly. If the elements on the web page are modified, the code may fail to locate the necessary elements. To address this issue, it is essential to update the code periodically and improve the crawling logic.
- Second, location tracking based on user's IP address has limited accuracy. Since an IP address alone may not provide precise location information, incorporating additional location details provided by the user or implementing a GPS-based tracking method would enhance accuracy.

## 🔍Reflections on the Project


During this project, I gained several important experiences and lessons.

**First, I developed a deep understanding of the complexity and challenges of web crawling.** In particular, I realized that collecting stable and reliable data from the complex structure of the Naver Map webpage requires meticulous attention and continuous maintenance. I learned various ways to handle exceptions, especially during the process of switching between multiple frames and processing dynamically loaded content triggered by scrolling.

**Second, I recognized the importance of balancing data collection with information accuracy.** Attempting to collect every piece of data can often lead to unforeseen errors or exceptions, and addressing these issues requires efficient error handling and data validation processes.

**Third, the project provided an opportunity to consider ways to improve user experience.** I discovered that simply collecting data is not enough to provide users with the precise and prompt information they need; it is equally important to organize and process the collected data into meaningful insights.

**Fourth, I reflected on both the limitations and possibilities of location-based services.** I experienced firsthand the limitations in accuracy when tracking location based on IP addresses, which highlighted the need for more precise location-tracking methods. This realization led me to think about how to enhance the reliability of location-based services and improve user satisfaction.

**Finally, the project taught me a great deal about problem-solving and code maintainability.** I learned the importance of writing robust code that can handle various exceptional cases, as well as the significance of enhancing code readability and reusability.

**Overall, this project was an extremely valuable opportunity to experience the practical application of web crawling and location-based services.** I look forward to leveraging these experiences in future projects and work to develop even better solutions.
