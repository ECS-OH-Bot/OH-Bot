# [<img src="https://img.icons8.com/color/48/000000/discord-logo.png"/>](https://discordapp.com/)OH-Bot

### The Discord Office Hour Butler

<p align=center style="font-size:large">
<a href=#purpose>Purpose</a> • 
<a href=#overview>Overview</a> • 
<a href=#installation>Installation</a> • 
<a href=https://ecs-oh-bot.github.io/OH-Bot/docs/build/html/index.html>Docs</a> •
<a href=#liscense>License</a>
</p>

## Purpose

With the need for online learning becoming increasingly higher, efficient means of reaching educators has become extremely important. 
We implemented a discord bot to help instructors automate the process of their Office Hours through Discord.

We created this bot with the goal of allowing students to effectively communicate with their instructors,
with the option to be able to ask their peers for help while they wait.
   
## Overview 
**OH-Bot** is a server managment automation bot. This means that tasks like notifying and moving students when they are ready to been seen are handled by **OH-Bot**

**OH-Bot** is a *self-hotsted* bot - meaning that you will need to host and maintain your own instance. See [installation](#installation) to get started. 

The standard OH-Session protocol that we follow:
1. Instructors Opens OH-Queue
2. Students enter queue and enter waiting room
3. Instructors dequeue students
4. Instructors close queue when OH-Session is over

## Waiting Queue System

**OH-Bot** implements a simple *first come first serve* queue where student are allowed to enter and leave the queue whenever they like while OH is being held.

## Server [Template](https://discord.new/53Q2rPtTh5EG)
**OH-Bot** makes use of Discord's Server Template feature

There are three roles in the **OH-Bot** server [template](#TODO:add_template_link):

* Admin - total control of bot functionality and server interfaces
* Instructor - control over OH sessions and locked channels
* Student - ability to interface with OH-Queue

### Commands

**OH-Bot** commands have access level based on sender roles

* `/open` - Access Role: [Admin, Instructor]
    * Open the OH-queue for students to join using `/eq`
* `/close` - Access Role: [Admin, Instructor]
    * Close the OH-queue, stop students from entering the queue
    * Students that were in the queue before closing will still be regisitered for OH
* `/clear /cq` - Access Role: [Admin, Instructor]
    * Empties the OH-queue of students
* `/enterqueue /eq` - Access Role: [Admin, Instructor, Student]
    * Enter sender into the OH-queue
* `/leavequeue /lq` - Access Role: [Admin, Instructor, Student]
    * Removes sender from the OH-queue
* `/dequeue /dq` - Access Role: [Admin, Instructor]
    * Removes next student from the queue and moves them into the voice channel the sender is currently connected to.
* `/help` - Access Role: [Admin, Instructor]
    * Sends a DM to the sender containing the above commands and their behavior relative to sender access level

## Requirements
* [Git](https://git-scm.com/) (Optional if using packaged release)
* [Python 3.7](https://www.python.org/downloads/) (or higher)
    * [Pip](https://pip.pypa.io/en/stable/installing/)
* [Discord](https://discordapp.com/) app & account

## Installation (In Progress)

Clone the source code

```bash
git clone https://github.com/ECS-**OH-Bot**/**OH-Bot**/tree/master && cd OH-Bot
```

Follow the instructions [here](https://discordpy.readthedocs.io/en/v1.3.3/discord.html#creating-a-bot-account) for obtaining a token for your instance of the Bot

Run the setup script
```bash
python3 setup.py
```

Run the script to start up the bot
```bash
./run.sh
```
# [Docs](https://ecs-oh-bot.github.io/OH-Bot/docs/build/html/index.html)

## License

Released under the [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.en.html) license.

`Copyright (C) 2020  Grant Gilson, Noah Rose Ledesma, Stephen Ott`
