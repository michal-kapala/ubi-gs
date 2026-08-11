# Ubisoft Game Service

Game Service (GS) was an online game feature SDK developed by Ubisoft.

It allowed for implementation of user auth, friends, matchmaking, in-game chat, CD key validation and more.

The games published by Ubisoft ca. 2000-2005 used `gsconnect.ubisoft.com` for online config, along with a dedicated network protocol suite for game server communication.

## Usage

To install all dependencies, run:
```
pip install -r requirements.txt
```

See dedicated READMEs for service usage info:

| Directory | Description |
|:-:|:-:|
| [`gsconnect`](gsconnect) | Common `gsconnect.ubisoft.com` web service |
| [`homm5`](homm5) | GS game servers for Heroes of Might and Magic V |
| [`tests`](tests) | Unit tests |

Python 3 is required for running the scripts (3.11+ recommended).

# Disclaimers

This project is not maintained by or affiliated with Ubisoft or Nival (formerly Nival Interactive).

All emulated services and tools were developed using techniques of software reverse engineering, on the basis of Ubisoft's end-of-life [announcement](https://www.ubisoft.com/en-us/help/purchases-and-rewards/article/decommissioning-of-online-services-for-older-legacy-ubisoft-games-a-m/000064576) for the game's online services, which implies termination of the [EULA](https://www.ubisoft.com/legal/documents/eula/en-US).

All rights belong to their respective owners.

## Games
An incomplete list of titles using GS SDK:
- Heroes of Might and Magic V
- Tom Clancy's Splinter Cell: Chaos Theory
- Brothers in Arms: Road to Hill 30
