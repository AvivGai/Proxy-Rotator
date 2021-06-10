# Proxy-Rotator

## Required installation:
flask

redis

## How to run:
clone the repository and cd into it.
```bash
python app.py
```

### Comments:
* If I had more time/experience O would have distribute the app so it will run on multiple servers for a more scalable solution.
* I tried to run my project with Docker without success, so it runs locally (but atl least it works :))
* Time complexity:
  1. Getting a proxy address is done in O(1).
  2. Reporting a proxy invalid is done in O(n) in the worst case. I know it is not ideal, but with the knowledge and tools I had it's the best I got. 
  3. (I had another solution where getting a proxy was O(n) and reporting a proxy was O(1) but assuming that the GET requests are more common I chose the cuurent implementaion)
