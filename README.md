<p align="center"><img src="http://i.imgur.com/vJshMwW.png" /></p>
<p align="center"><img src="https://travis-ci.com/stevenleeg/geemusic.svg?branch=master" /></p>

GeeMusic is an Alexa skill which bridges Google Music and Amazon's Alexa. It hopes to rescue all of those who want an Echo/Dot but don't want to switch off of Google Music or pay extra for an Amazon Music Unlimited subscription.

This project is still in its early phases and subject to a bit of change, however it is functional and ready for use! The only catch is that you'll need to run it on your own server for the time being (ideally I'll eventually release this on the Alexa Skills marketplace, but there's a lot of work to do before then). This means that you should be familiar with how to set up your own HTTPS web server for now.

### Notes

**This Skill is not made by nor endorsed by Google.** That being said, it is based off of the wonderful [gmusicapi](https://github.com/simon-weber/gmusicapi) by [Simon Weber](https://simon.codes), which has been around since 2012, so this should work as long as Google doesn't decide to lock down its APIs in a major way.

**The use of 2FA (2-Factory Authentication) and an app-specific password are highly recommended.** If you fail to use an app-specifc password and 2FA, Google may ask you to reset your password until you use one. There have been multiple reports of logins failed bacause of the failure to follow this step. More info about app-specific passwords [here](https://support.google.com/accounts/answer/185833) and 2FA [here](https://support.google.com/accounts/answer/185839).

### Supported Echo languages

**This Skill was developed to only work on devices (Echo, Dot, Tap etc) using English(US) on a Amazon US account**
This is due to the Skill using features from the [Developer Preview of the ASK Built-in Library](https://developer.amazon.com/blogs/post/Tx2EWC85F6H422/Introducing-the-ASK-Built-in-Library-Developer-Preview-Pre-Built-Models-for-Hund). Which frustratingly has only been made available to developers in the US (edit: six months later and there is still no access for UK/DE).

There is a workaround for English(UK) and Japanese users if they setup the Skill slightly differently, instructions are included below.

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

# Debug mode: Set to True or False
DEBUG_MODE=False
DEBUG_FORCE_LIBRARY=False  # Forces a subscribed user to use local library playback, rather than the default Store
```

I would *highly reccomend* that you enable 2-factor authentication on your Google account and only insert an application specific password into this file. Remember that it is stored in plaintext on your local computer! (TODO: fix this!)

Once you have your `.env` file ready to go, let's start the server. I personally use [Foreman](https://github.com/ddollar/foreman) to run the server, as it will automatically load the `.env` file into my environment and boot up the webserver. There are surely other ways of doing this, but if you'd like to follow my lead you can run `gem install foreman`.

Once `foreman` is ready to go, simply run

```bash
$ foreman start
```

and you should see your web server start at http://localhost:5000 (although it won't do much if you visit it with your browser).

For alternatives on setting up your server, see the optional sections, notably the Heroku section if you're not familiar with configuring your own HTTPS server.

## Create the development Skill on Amazon

Open up the [Alexa Dashboard](https://developer.amazon.com/edw/home.html), click "Get Started" in the **Alexa Skills Kit** box. Then click on the yellow "Add a New Skill" button in the top right corner.

Going through the various sections

### Skill Information

| Field | Value |
| ----- | ----- |
| Skill Type | Custom Interaction Model |
| Language | Select US English, UK English or Japanese |
| Name | Gee Music |
| Invocation Name | gee music |
| Audio Player | Yes |

### Interaction model

This setup varies depending on the language settings your Echo device is using.

See the note at the top about supported languages. 

#### US English users

On the "Interaction Model" step, paste in the contents of `speech_assets/interactionModel.json` to the JSON Editor.

#### Other language users

On the "Interaction Model" step, paste in the contents of `speech_assets/non_us_custom_slot_version/interactionModel.json` to the JSON Editor.


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

Setting up an instance on Heroku may be an easier option for you, and these instructions detail how to accomplish this. The following steps replace the need to setup a local server.

First, we need to deploy a copy of this code to Heroku. To do that, simply click the Deploy to Heroku button below.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/stevenleeg/geemusic/tree/master)

Once you've named your app and the code has been deployed, the next step is to configure the app to work with your Google account. To do this click on the settings tab of Heroku's site. After the tab has loaded, click the button labeled Reveal Config Vars and update the variables below replacing each temporary value with your own values.

| Variable Name  | Value |
| ------------- | ------------- |
| GOOGLE_EMAIL  | YOUR_EMAIL |
| GOOGLE_PASSWORD  | YOUR_PASSWORD  |
| APP_URL | https://[heroku_app_name].herokuapp.com |
| DEBUG_MODE | false |

At this point, your server should by live and ready to start accepting requests at `https://[heroku_app_name].herokuapp.com/alexa.` Note, that while using the free tier, you may experience timeout errors when you server has received no requests for over 30 minutes. However, you can use a service, such as [Kaffeine](http://kaffeine.herokuapp.com/) to minimize your downtime.

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
-e APP_URL=http://alexa-geemusic.stevegattuso.me -p 5000:5000 geemusic
```

At this point you're set up and ready.

## (Optional) Use AWS Lambda
*Note this costs about $0.30-$1.00 per month based on usage*

Setting this up for AWS Lambda actually isn't that bad. You need to create an AWS account first though, [AWS](https://aws.amazon.com), and click "Create an AWS Account" and follow the instructions to create the account.

We are also going to need a few more dependencies, so while you are in your virtualenv type the following: `pip install zappa awscli` and then `pip freeze > requirements.txt` if you wish to overwrite the base requirements.txt file with the proper requirements to deploy to AWS.

### Deployment Part 1. Setting up IAM Account.

Once your account is created:
  1. Open the [IAM Console](https://console.aws.amazon.com/iam/home#/home), and sign in with your account that you should have by now. 
  2. In the navigation pane, choose Users. 
  3. Click the `Add User` button. 
  4. Name the user zappa-deploy, choose `Programmatic` access for the Access type, then click the `Next: Permissions` button. 
  5. On the permissions page, click the Attach existing policies directly option. 
  6. A large list of policies is diplayed. Locate the AdministratorAccess policy, click its checkbox, then click the `Next: Review` button.
  7. Finally, review the information that displays with the steps above and then click the `Create User` button.
  8. Once the user is created, its `Access key ID` and `Secret access key` are displayed (click the `Show` link next to the Secret access to show it). 
  9. Keep that tab open or copy them to a safe place because we will need those later. Treat those keys like you would your password because they have the same privileges.

### Deployment Part 2. Configure IAM credentials locally.

Type aws configure to begin the local setup.

Follow the propts to input your `Access key ID` and `Secret access key`. For Default region name, type: `us-east-1` (it must be a valid region) For Default output format, accept the default by hitting the Enter key.

The `aws configure` command installs credentials and config in an .aws directory inside your home directoy. Zappa knows how to use this figuration to create the AWS resources it needs to deploy Flask-Ask skills to Lambda.

We're now almost ready to deploy our skill with Zappa.

### Deployment Part 3. Deploy the skill with Zappa.

In the terminal, create a zappa configuration file by typing: `zappa init` or by typing `mv gmusic_zappa_settings.json zappa_settings.json` to copy this skeleton file and update all the `redacted` fields with your own values.

*Note: After a while you might have to grab an old valid working device ID from your account using the `Mobileclient.get_registered_devices()`. You'll have to login via a python shell using the `gmusicapi` on a computer that has a valid device id as Lambda functions don't have a MAC address.*

Once the initialization is complete, deploy the skill by typing: `zappa deploy dev`

Edit the zappa_settings.json file and fill in the `redacted` information with your own personal information specific to your deployment

Then type the following: `zappa update dev`

Finally you have to update your Alexa Skills Configuration tab to use this URL + /alexa. For example it looks like this, `https://[random-stuff].execute-api.us-east-1.amazonaws.com/dev/alexa`. Everything else for the configuration is the same as the heroku setup. 

It still uses a wildcard SSL cert and doesn't use Account linking or list read/writes.



## (Optional) Last.fm support
*Only attempt this if you have significant technical expertise.* To scrobble all played tracks to [Last.fm](http://www.last.fm) follow the instructions at [this repo](https://github.com/huberf/lastfm-scrobbler) to get auth tokens.

Then add them as environement variables to your setup (e.g. `LAST_FM_API`, `LAST_FM_API_SECRET`, `LAST_FM_SESSION_KEY`). To finish enabling create a `LAST_FM_ACTIVE` environement variable and set it to `True`.

## (Optional) Language support
If your desired language is listed below you can simply set your `LANGUAGE` environment variable to the 2 character country code specified below:

```
# English
LANGUAGE=en

# German
LANGUAGE=de

# French
LANGUAGE=fr
```

If you want to add a language submit a PR to this repository and add translations for the language you want to support in `geemusic/templates/` dir with the global two character country code + `yaml`. For example, the English the file is `geemusic/templates/en.yaml`.

## Troubleshooting
### Pausing/resuming skips to the beginning of the song.
Flask Ask used to have a bug that would not resume the song from the correct offset. Make sure it, and the rest of your pip modules are up to date.

### Music won't start playing
Issues where Alexa responds to your requests but doesn't play music are generally caused by the `APP_URL` environment variable being set improperly. Be sure that it is set to something like `APP_URL=https://ff9b5cce.ngrok.io` **without a trailing slash or `/alexa`**.

## Contributing
Please feel free to open an issue or PR if you've found a bug. If you're looking to implement a feature, please open an issue before creating a PR so I can review it and make sure it's something that should be added.

## License
This project is released under the GNU General Public License v3.0. See LICENSE.txt for more information.
