<p align="center"><img src="http://i.imgur.com/vJshMwW.png" /></p>

GeeMusic is an Alexa skill which bridges Google Music and Amazon's Alexa. It hopes to rescue all of those who want an Echo/Dot but don't want to switch off of Google Music or pay extra for an Amazon Music Unlimited subscription.

This project is still in its early phases and subject to a bit of change, however it is functional and ready for use! The only catch is that you'll need to run it on your own server for the time being (ideally I'll eventually release this on the Alexa Skills marketplace, but there's a lot of work to do before then).

### Notes

**This Skill is not made by nor endorsed by Google.** That being said, it is based off of the wonderful [gmusicapi](https://github.com/simon-weber/gmusicapi) by [Simon Weber](https://simon.codes), which has been around since 2012, so this should work as long as Google doesn't decide to lock down its APIs in a major way.

### Supported Echo languages

**This Skill was developed to only work on devices (Echo, Dot, Tap etc) using English(US) on a Amazon US account**
This is due to the Skill using features from the [Developer Preview of the ASK Built-in Library](https://developer.amazon.com/blogs/post/Tx2EWC85F6H422/Introducing-the-ASK-Built-in-Library-Developer-Preview-Pre-Built-Models-for-Hund). Which frustratingly has only been made available to developers in the US (edit: six months later and there is still no access for UK/DE).

There is a workaround for English(UK) users (Amazon UK account) if they setup the Skill slightly differently, instructions are included below.

This language issue only affects the Echo/Amazon side of things and not your Google Music account [#100](https://github.com/stevenleeg/geemusic/issues/100)

## Features
What can this puppy do, you might ask? Here's a list of example phrases that you can try once you get GeeMusic up and running. Remember that each of these phrases needs to be prefixed with "Alexa, tell Geemusic to..." in order for Alexa to know that you're requesting music from GeeMusic, not the built-in music services. They're also fuzzy, so feel free to try slight variations of phrases to see if they'll work.

### Currently Implemented
```
Play artist Radiohead
Play songs by LCD Soundsystem
Play top songs by Nujabes
Play music by A Tribe Called Quest

Play the album Science For Girls
Play album Plastic Beach
Play the album To Pimp A Butterfly by Kendrick Lamar
Play album and The Anonymous Nobody by De La Soul

Play the song Fitter Happier
Play song Cocoa Butter Kisses
Play the song Drunk Girls by LCD Soundsystem
Start a radio station for artist Weezer
Play some music (plays your I'm Feeling Lucky station)
Start playlist Dancy Party

What is currently playing?
Like this song
Dislike this song
Thumbs-up this song
Thumbs-down this song

Play the latest album by Run The Jewels
List the latest albums by The Wonder Years
List all albums by Pink Floyd (up to 25 listed)
Play an album by Dryjacket
Play a different album

Skip to Scar Tissue by Red Hot Chili Peppers
Jump to Knee Deep by Zac Brown Band
```

Of course you can also say things like "Alexa stop," "Alexa next," etc.

### Roadmap
```
Play a station for bedtime
Play a station for partying
```
- [ ] Play a station for bedtime
- [ ] Play a station for partying

## Setup
Let's cut right to the chase: how can you enable this skill on your own Dot/Echo? Unfortunately the process is a bit finicky, but I'll try to make it as simple as I can.

The following instructions have been tested on UNIXy environments, namely OS X, Arch, and Ubuntu. It's great if you are able to get this running on Windows, but if not please do not open an issue, as it is an unsupported environment.

### Start a local development server
Let's start out by getting the GeeMusic server running on your machine. Before you get started, please note that this server must be running at all times and be publicly accessible to the internet in order for this skill to run. If the server shuts down the party stops.

First things first, clone this repository to your server:

```bash
$ git clone https://github.com/stevenleeg/geemusic.git
```

Next make sure you have Python 3 installed and `cd` in and install the dependencies, you ideally want to do this within a `virtualenv` if you have it installed, but otherwise you can omit those steps and just run the `pip3 install` line. Note that some of the dependencies require a few packages that you may not already have on your system: `python3-dev`, `libssl-dev`, and `libffi-dev`. On Ubuntu these can be installed by running `sudo apt-get install python3-dev libssl-dev libffi-dev`.

```bash
# Run this if you have virtualenv installed:
$ virtualenv .venv
$ source .venv/bin/activate

# Continue on if you have virtualenv or start here if you don't:
$ pip3 install -r requirements.txt
```

Once the requirements are installed we'll need to create a file, `.env` to store our credentials. Here's an example:

```
# Google credentials
GOOGLE_EMAIL=steve@stevegattuso.me
GOOGLE_PASSWORD=password

# Publicly accessible URL to your server, WITHOUT trailing slash
APP_URL=https://alexa-geemusic.stevegattuso.me
```

I would *highly reccomend* that you enable 2-factor authentication on your Google account and only insert an application specific password into this file. Remember that it is stored in plaintext on your local computer! (TODO: fix this!)

Once you have your `.env` file ready to go, let's start the server. I personally use [Foreman](https://github.com/ddollar/foreman) to run the server, as it will automatically load the `.env` file into my environment and boot up the webserver. There are surely other ways of doing this, but if you'd like to follow my lead you can run `gem install foreman`.

Once `foreman` is ready to go, simply run

```bash
$ foreman start
```

and you should see your web server start at http://localhost:4000 (although it won't do much if you visit it with your browser).

## Create the development Skill on Amazon

Open up the [Alexa Dashboard](https://developer.amazon.com/edw/home.html), click "Get Started" in the **Alexa Skills Kit** box. Then click on the yellow "Add a New Skill" button in the top right corner.

Going through the various sections

### Skill Information

| Field | Value |
| ----- | ----- |
| Skill Type | Custom Interaction Model |
| Language | Select US English or UK English |
| Name | Gee Music |
| Invocation Name | gee music |
| Audio Player | Yes |

### Interaction model

This setup varies depending on the language settings your Echo device is using.

See the note at the top about supported languages. 

#### US English users

On the "Interaction Model" step, paste in the contents of `speech_assets/intentSchema.json` to the intent schema field and the contents of `speech_assets/sampleUtterances.txt` to the sample utterances field.

#### UK English users

On the "Interaction Model" step, you need to create your Custom Slot Types before the intent schema and sample utterances.

You need to make four slots and fill them with sample data for each of the following:

* MUSICALBUM
* MUSICGROUP
* MUSICRECORDING
* MUSICPLAYLIST

Click "Add Slot Type" and enter `MUSICALBUM` into the "type", then copy and paste the contents of `/speech_assets/non_us_custom_slot_version/sample_slot_data/MUSICALBUM.txt` into the "values" section.

Repeat the process for each of the slots.

The sample data was scraped from the UK top 100 singles and album chart. For the MUSICPLAYLISTS there are some generic sample phrases. The sample data is fine to use, don't feel you need to fill these slots to match your own collection.

After you have added the "Custom Slots" you need to copy and paste the contents of `/speech_assets/non_us_custom_slot_version/intentSchema.json` to the intent schema field and the contents of `speech_assets/sampleUtterances.txt` to the sample utterances field.


### Configuration

We'll point our skill at the URL for our development server. Select HTTPS as the endpoint type and enter your server's URL in the corresponding box. Remember that your development server must be publicly accessible AND using HTTPS in order for Amazon to be able to connect/interact with it.

If your development server is running on a server that is already available on the internet, type its URL (such as `https://geemusic.example.com/alexa`). Make sure you include the `/alexa`, otherwise this won't work!

If you are running the server on a computer behind a firewall we'll need to expose the server via a tunnel in order for this to work. I usually use [ngrok](https://ngrok.com/) for these situations and have used it to develop this project. To start a tunnel run `ngrok http 4000` in a console window. You should then see a few URLs, one of which being a publicly accessible HTTPS link to your development server. Copy this URL, being sure to append `/alexa` so the final result looks something like `https://[some-code].ngrok.io/alexa`. **Important:** Make sure you update your `.env` file's `APP_URL` to this new URL, otherwise Alexa will not be able to stream music!

You'll also want to select "No" for the "Account Linking" field before moving on.

### SSL Certificate

If using [ngrok](https://ngrok.com/) or [heroku](https://heroku.com) select the second option "My development endpoint is a subdomain of a domain that has a wildcard certificate from a certificate authority."

### Test

Scroll down to the "Service Simulator" section, the check the Skill is talking to Alexa correcty enter the word help  _"help"_ then click "Ask Gee Music", and you'll ideally see some resulting JSON in the Service Response box. You can then try testing phrases like_"Play album In Rainbows by Radiohead"_

### Publishing Information, Privacy & Compliance

Do not fill these in and make sure you never click "SUBMIT FOR CERTIFICATION". You are NOT submitting the Skill to Amazon to include in the public Skill store.  

----

If all goes well the skill should also be up and running on your Echo/Dot! Take a look at the features section of this Readme to get an idea of what you can tell it to do.

Enjoy streaming Google Music via Alexa!

## (Optional) Setup a Heroku instance

Setting up an instance on Heroku may be an easier option for you, and these instructions detail how to accomplish this. The following steps replace the need to setup a local server. First one must have Heroku setup on your local machine and an account associated. Visit [the CLI documentation](https://devcenter.heroku.com/articles/heroku-cli) for details on setting this up.

One must then clone the repository.

```bash
$ git clone https://github.com/stevenleeg/geemusic.git
```

Next, `cd` in to deploy the code. Then, setup the Heroku server by typing the following two commands.

```bash
$ heroku create
$ git push heroku master
```

We now need to configure it to work with your Google account. Type the following commands, and replace details with your own account credentials and app settings.

```bash
$ heroku config:set GOOGLE_EMAIL=steve@stevegattuso.me
$ heroku config:set GOOGLE_PASSWORD=[password]
$ heroku config:set APP_URL=https://[heroku_app_name].herokuapp.com
```

At this point, your server should by live and ready to start accepting requests at `https://[heroku_app_name].herokuapp.com/alexa.` Note, that while using the free tier, you may experience timeout errors when you server has received no requests for over 30 minutes.

## (Optional) Use Docker

If you have docker running on a server, running this server as a docker container may make the most sense for your setup. As of right now there is not an image available in the dockerhub, but building the container is very easy.

First, clone this repository.

```bash
$ git clone https://github.com/stevenleeg/geemusic.git
```

Now, `cd` in and build the container. We'll tag it 'geemusic', but you can call it whatever you want.

```bash
$ docker build -t geemusic .
```

Finally, run the container with the appropriate environment variables and port forwards. Alternatively set up a compose file or your orchestration engine, but those are outside the scope of this readme.

```bash
$ docker run -d -e GOOGLE_EMAIL=steve@stevegattuso.me -e GOOGLE_PASSWORD=[password] \
-e APP_URL=http://alexa-geemusic.stevegattuso.me -p 4000:4000 geemusic
```

At this point you're set up and ready.

## Free Google Music Support
If you do not subscribe to Google Music and would like to play your Uploaded Music Library, put in this enviornment variable (in your .env file):
# Set to only use my uploaded library and ignore the store ids, use this if you are a free google user
USE_LIBRARY_FIRST=true

This will search your library instead of querying the api for store versions of songs.

## (Optional) Last.fm support
*Only attempt this if you have significant technical expertise.* To scrobble all played tracks to [Last.fm](http://www.last.fm) follow the instructions at [this repo](https://github.com/huberf/lastfm-scrobbler) to get auth tokens.

Then add them as environement variables to your setup (e.g. `LAST_FM_API`, `LAST_FM_SECRET`, `LAST_FM_SESSION_KEY`). To finish enabling create a `LAST_FM_ACTIVE` environement variable and set it to `True`.

## Troubleshooting
### Pausing/resuming skips to the beginning of the song.
Flask Ask used to have a bug that would not resume the song from the correct offset. Make sure it, and the rest of your pip modules are up to date.

### Music won't start playing
Issues where Alexa responds to your requests but doesn't play music are generally caused by the `APP_URL` environment variable being set improperly. Be sure that it is set to something like `APP_URL=https://ff9b5cce.ngrok.io` **without a trailing slash or `/alexa`**.

## Contributing
Please feel free to open an issue or PR if you've found a bug. If you're looking to implement a feature, please open an issue before creating a PR so I can review it and make sure it's something that should be added.

## License
This project is released under the GNU General Public License v3.0. See LICENSE.txt for more information.
