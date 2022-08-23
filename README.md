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
```
pip install bintang-buddy
```

## Usage
The steps are straightforward and very human.

Try running the commands below:
```
bintang-buddy -d "2022-01-13" -g "milpitas" -g "sunnyvale"
```

This script has two arguments:
1. `-d`: Date string, in the form of `YYYY-MM-DD`
2. `-g`: The names of the gyms you'd like to load court schedules for. If you leave this empty you'll get every court for every gym, and you'll be waiting for a while. Your choices: `campbell, dublin, milpitas, san carlos, sunnyvale`.
