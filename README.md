<p align="center">
  <img src="https://user-images.githubusercontent.com/10181537/147032585-65154e0a-8885-4777-befd-405437d917cd.png" alt="title" width="50%" /> 
</p>


<h3 align="center">
    <p>The easiest way to view 🏸 court reservations in the Bay Area</p>
</h3>

Ever wanted to play badminton at a certain time? Have you tried looking at court reservations on https://bintangbadminton.org/court-reservations/? If yes, you've probably seen this:

![this is what you first see when you try to make a bintang booking](https://user-images.githubusercontent.com/10181537/147029092-45062d7c-7b88-4a91-bcc6-edbbfefab487.png)

No experience parallels looking for courts and when they're free, only to click through this nightmare: 😱🙀

<p float="left">
  <img src="https://user-images.githubusercontent.com/10181537/147029277-8453ad3c-2c1c-454a-9c45-08b22e2dda39.png" alt="when you click through on one gym you see many courts" width="40%" /> 
  <img src="https://user-images.githubusercontent.com/10181537/147029436-63d6cc9a-9a74-458a-a8cf-5ed333299a14.png" alt="when you click through on one court you finally see the times" width="40%" />
</p>

That's OK, with a few easy steps, you can be viewing court schedules with buttery smoothness:
![image](https://user-images.githubusercontent.com/10181537/147728223-ac92d19c-455a-4cce-b666-924f0cdede11.png)

# Command line tool

## Installation
Steps below are for Python 3, but it should work for Python 2 as well. To get your Bearer Token, follow steps in [Getting the Bearer Token](https://github.com/teoh/bintang-buddy/blob/main/README.md#getting-the-bearer-token).
```
git clone https://github.com/teoh/bintang-buddy.git
cd bintang-buddy
python3 -m venv venv
source venv/bin/activate
pip3 install -r python/requirements.txt
export BEARER=<your bearer token>
```

## Usage
The steps are straightforward and very human.

Try running the commands below:
```
cd bintang-buddy
python3 python/bintang_schedules.py  -d "20220113" -g "san carlos" -g "sunnyvale"
```

This script has two arguments:
1. `-d`: Date string, in the form of `YYYYMMDD`
2. `-g`: The names of the gyms you'd like to load court schedules for. If you leave this empty you'll get every court for every gym, and you'll be waiting for a while. Your choices: `campbell, dublin, milpitas, san carlos, sunnyvale`

## Getting the Bearer Token
I hate this step, I wish I didn't have to include it, but pasting tokens on a public repo didn't seem like a good idea. 
Steps below:
1. On Chrome, go to https://bintangbadminton.org/court-reservations/
2. Scroll to the bottom and look for this: ![image](https://user-images.githubusercontent.com/10181537/147729891-ad980af9-cf10-40c8-8c0d-d8dae8c91299.png)
3. `⌥+⌘+I` to open developer tools
4. On the developer tools, click the "Network" tab: <img width="1792" alt="Screen Shot 2021-12-29 at 23 18 35" src="https://user-images.githubusercontent.com/10181537/147730076-07251ad4-b126-488a-8e78-02c5371d691a.png">
5. Do `⌘+E` to clear the network history 
6. Click any court on the left, e.g. Campbell Courts: <img width="1788" alt="Screen Shot 2021-12-29 at 23 20 23" src="https://user-images.githubusercontent.com/10181537/147730150-8647b514-bd99-496d-9cf2-85f811f41258.png">
7. Some requests should show up on the right: <img width="350" alt="Screen Shot 2021-12-29 at 23 22 44" src="https://user-images.githubusercontent.com/10181537/147730281-0f5755ee-fe73-4307-a3cc-72a8011b7e95.png">
8. Keep clicking around the list until you see a `Request URL` that starts with `https://app.bukza.com/api/`: <img width="922" alt="Screen Shot 2021-12-29 at 23 24 45" src="https://user-images.githubusercontent.com/10181537/147730444-f1a8f873-5a58-41f3-b422-29f94e0a7c5a.png">
9. Scroll down to `Request Headers` and copy the long text beside "Bearer". This is your Bearer Token: <img width="782" alt="Screen Shot 2021-12-29 at 23 28 00" src="https://user-images.githubusercontent.com/10181537/147730765-71bd112a-0d8b-4393-b047-5af3d486b677.png">

