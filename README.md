# GSConnect
Game servers for games built using Ubisoft's Game Service SDK.

## Game Service
Game Service (GS) was an online game feature SDK developed by Ubisoft.

It allowed for implementation of user auth, friends, matchmaking, in-game chat, CD key validation and more.

The games published by Ubisoft ca. 2000-2005 used `gsconnect.ubisoft.com` for online config, along with a dedicated network protocol suite for game server communication.

## Usage
See dedicated READMEs for service usage info:

| Directory | Service |
|:-:|:-:|
| [`gsconnect`](gsconnect) | Common `gsconnect.ubisoft.com` web service |
| [`homm5`](homm5) | GS game servers for Heroes of Might and Magic V |

Python 3 is required for running the scripts (3.11+ recommended).

## Games
An incomplete list of titles using GS SDK:
- Heroes of Might and Magic V
- Tom Clancy's Splinter Cell: Chaos Theory
