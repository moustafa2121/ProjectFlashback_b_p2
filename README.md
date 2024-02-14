# FlashBack
[Live app](http://35.222.8.176/)

## About 🛈
Project FlashBack “simulates” a period of time. It is made of several phases, currently Phase1 and Phase2 are live.

Live Demo is deployed on Ubuntu VM on Google Cloud

### Phase1
[Throwback](https://github.com/moustafa2121/ProjectFlashback_b): Inspired by the question of “what the internet was like back then?”. It fetches data from several sources, trying to give a feel what was it like browsing the internet in a given year. Data scraped from several sources, providing posts from Reddit, Twitter, Spotify, IMDB, Wikipedia, KnowYourMeme.

User can input the year, posts are fetched as the user scrolls (infinite scroll).

### Phase2
[Lens Into The Past](https://github.com/moustafa2121/ProjectFlashback_b_p2): It uses OpenAI’s ChatGPT API and Dall-E API to simulate events in the distant past. The user submits a query (ex: William The Conqueror Invading Britain), and that query will be submitted to ChatGPT API. The latter will return 5 paragraphs, describing different stages of the historical story regarding the given query.\
Afterwards, Dall-E will be promoted for 5 images regarding each different stories. Query results will be returned, saved in the DB, and sent to the user in real-time.

Furthermore, the user can scroll down to view other stories (including those of other users).

User is limited to 3 queries per day. All users have a combined limit of 10 queries per day.

🚩Try avoiding controversial subjects as that will be blocked by OpenAI’s policy of the whatever. Anything that may involve gory scenarios or sensitive subjects will be rejected by ChatGPT or Dall-E’s API (in which the latter seems to be more strict). 🚩

## Built with 🔧
- Django REST Framework
- React
- Bootstrap
- Nginx
- Gunicorn
- Docker
- Google Cloud
- OpenAI/ChatGPT/Dall-E

## Features 📋
- SPA
-	Responsive display
-	Infinite scroll



## Usage 🧮
There are 4 repositories that make up the entire project. Nginx, backend1, backend2 (each run on a Docker container), and React's frontend. To run, do the following:\
1- Clone them and place them in the following structure:\
├── [main repo container docker-compose](https://github.com/moustafa2121/flashback-docker/tree/main)\
│   ├── [Phase1 backend](https://github.com/moustafa2121/ProjectFlashback_b)\
│   ├── [Phase2 backend](https://github.com/moustafa2121/ProjectFlashback_b_p2)\
│   ├── [React Frontend](https://github.com/moustafa2121/project-flashback_f)

2- Install docker and docker-compose\
3- In the React project, change the IP address of the backend API called on by the frontend (found in the frontend repo -> src/helper.js), which is expected to be that of the machine you're building on the code.\
4- Then, while in the main repo, run
```sh
sudo docker-compose up --build
```

Note that even though phase2 will retrieve the previous stories, it will fail in making queries. This is because you need your own OpenAI API key (the one for live demo is hidden, obviously). You can add your own in the Docker file of the backend2 repo.

## Architecture
![architecture](https://github.com/moustafa2121/flashback-docker/blob/main/Architecture.jpg)

## Demo ⏵
🚩Note that some frames were trimmed from the demo gif to shorten the phase2 prompting because it takes a while. Takes around 30 seconds for ChatGPT to return a query, and maybe 10-15 seconds for the each image (they are queried concurrently though). 🚩

![demo](https://github.com/moustafa2121/flashback-docker/blob/main/demo.gif)
