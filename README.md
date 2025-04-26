# AI assistants

# Requirements
- OS: Debian
    - Currently only validated to work with Linux Mint Cinnamon 22, but it could work elsewhere
- Installations
    - bash
    - python3.12

- 
- All python requirements are in a requirements.txt file and they should be downloaded automatically

- ollama installation

<!-- This is used for listening to both speakers and microphone -->
- sudo apt-get install pulseaudio pulseaudio-utils

<!-- The program sets up the audio and input loopback using something like this -->
- pactl load-module module-null-sink sink_name=ai_agents_combined_sink sink_properties=device.description=Both-mic-and-speakers

sudo apt install ffmpeg

ADD A DOWNLOAD WISPER WHEN SETTING UP FEATURE

NOTE: For Debian12 and Linux Mint users, an automatic install feature is available by default. 
    For Debian 12, you can follow the instructions https://wiki.debian.org/sudo/ to add sudo, or if you know how to work with root, work with root. The program will prompt you to run with sude priviliges if it thinks it needs it.




