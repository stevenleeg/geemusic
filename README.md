# Gee, Music!
GeeMusic is an Alexa skill which bridges Google Music and Amazon's Alexa.
It hopes to rescue all of those who want an Echo/Dot but don't want to switch
off of Google Music or pay extra for an Amazon Music Unlimited subscription.

This project is still in its early phases and subject to a bit of change, 
however it is functional and ready for use! The only catch is that you'll need
to run it on your own server for the time being (ideally I'll eventually
release this on the Alexa Skills marketplace, but there's a lot of work to do
before then).

**Note: This skill is not made by nor endorsed by Google.** That being said, it
is based off of the wonderful [gmusicapi](https://github.com/simon-weber/gmusicapi)
by [Simon Weber](https://simon.codes), which has been around since 2012, so this
should work as long as Google doesn't decide to lock down its APIs in a major
way.

## Features
What can this puppy do, you might ask? Here's a list of example phrases that
you can try once you get GeeMusic up and running. Remember that each of these
phrases needs to be prefixed with "Alexa, tell Geemusic to..." in order for
Alexa to know that you're requesting music from GeeMusic, not the built-in
music services.


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
```

### Roadmap
```
Like this song
Dislike this song
Thumbs-up this song
Thumbs-down this song
Play the latest album by Run The Jewels
Skip to the 3rd song in this album
Play the third track off of In Rainbows
Play Kanye West radio
Play some music (for the I'm Feeling Lucky station)
Play a station for bedtime
Play a station for partying
```

### Known bugs:
* Pausing/resuming currently skips to the beginning of the song. Trust me, I
  know how annoying this is an I'm actively working on fixing it.

## Setup
Let's cut right to the chase: how can you enable this skill on your own
Dot/Echo? Unfortunately the process is a bit finicky, but I'll try to make it
as simple as I can.

The following instructions have been tested on UNIXy environments, namely OS X,
Arch, and Ubuntu. It's great if you are able to get this running on Windows,
but if not please do not open an issue, as it is an unsupported environment.

### Start a local development server
Let's start out by getting the GeeMusic server running on your machine. Before
you get started, please note that this server must be running at all times and
be publicly accessible to the internet in order for this skill to run. If the
server shuts down the party stops.

First things first, clone this repository to your server:

```bash
$ git clone https://github.com/stevenleeg/geemusic.git
```

Next, `cd` in and install the dependencies, ideally within a `virtualenv` if
you have it installed, but otherwise you can omit those steps and just run the
`pip install` line. Note that some of the dependencies require Python's C
headers (on Ubuntu these can be installed by running `sudo apt-get install
python-dev`).

```bash
# Run this if you have virtualenv installed:
$ virtualenv .venv
$ source .venv/bin/activate

# Continue on if you have virtualenv or start here if you don't:
$ pip install -r requirements.txt
```

Once the requirements are installed we'll need to create a file, `.env` to
store our credentials. Here's an example:

```
# Google credentials
GOOGLE_EMAIL=steve@stevegattuso.me
GOOGLE_PASSWORD=[password]

# Publicly accessible URL to your server, WITHOUT trailing slash
APP_URL=https://alexa-geemusic.stevegattuso.me
```

I would *highly reccomend* that you enable 2-factor authentication on your
Google account and only insert an application specific password into this file.
Remember that it is stored in plaintext on your local computer! (TODO: fix
this!)

Once you have your `.env` file ready to go, let's start the server. I
personally use [Foreman](https://github.com/ddollar/foreman) to run the server,
as it will automatically load the `.env` file into my environment and boot up
the webserver. There are surely other ways of doing this, but if you'd like to
follow my lead you can run `gem install foreman`.

Once `foreman` is ready to go, simply run

```bash
$ foreman start
```

and you should see your web server start at http://localhost:4000 (although it
won't do much if you visit it with your browser).

### Create a development skill on Amazon
Open up the [Alexa Dashboard](https://developer.amazon.com/edw/home.html) and
click on the yellow "Add a New Skill" button in the top right corner.

Set the parameters on the "Skill Information" step as follows:

| Field | Value |
| ----- | ----- |
| Skill Type | Custom Interaction Model |
| Name | Gee Music |
| Invocation Name | gee music |
| Audio Player | Yes |

On the "Interaction Model" step, paste in the contents of
`speech_assets/intentSchema.json` to the intent schema field and the contents
of `speech_assets/sampleUtterances.txt` to the sample utterances field.

In the "configuration step" we'll point our skill at the URL for our
development server. Select HTTPS as the endpoint type and enter your server's
URL in the corresponding box. Remember that your development server must be
publicly accessible AND using HTTPS in order for Amazon to be able to
connect/interact with it.

If your development server is running on a server that is already available on
the internet, type its URL (such as `https://geemusic.example.com/alexa`). Make
sure you include the `/alexa`, otherwise this won't work!

If you are running the server on a computer behind a firewall we'll need to
expose the server via a tunnel in order for this to work. I usually use
[ngrok](https://ngrok.com/) for these situations and have used it to develop
this project. To start a tunnel run `ngrok http 4000` in a console window. You
should then see a few URLs, one of which being a publicly accessible HTTPS link
to your development server. Copy this URL, being sure to append `/alexa` so the
final result looks something like `https://[some-code].ngrok.io/alexa`.
**Important:** Make sure you update your `.env` file's `APP_URL` to this new
URL, otherwise Alexa will not be able to stream music!

You'll also want to select "No" for the "Account Linking" field before moving
on.

Now that your skill is set up, you should be able to skip the SSL step and move
right into "Test". Once there, scroll down to the "Service Simulator" section,
enter some text like `Play album In Rainbows by Radiohead`, click "Ask Gee
Music", and you'll ideally see some resulting JSON in the Service Response box.

If all goes well the skill should also be up and running on your Echo/Dot! Take
a look at the features section of this Readme to get an idea of what you can
tell it to do. 

Enjoy streaming Google Music via Alexa!

## Contributing
Please feel free to open an issue or PR if you've found a bug. If you're
looking to implement a feature, please open an issue before creating a PR so I
can review it and make sure it's something that should be added.

## License
This project is released under the GNU General Public License v3.0. See
LICENSE.txt for more information.
