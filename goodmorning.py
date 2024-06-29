#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import caldav
from datetime import datetime, timedelta
import pytz
from openai import OpenAI
from elevenlabs.client import ElevenLabs
from elevenlabs import save

from pydub import AudioSegment
from math import log10
import pygame
import time
import random
import os
from dotenv import load_dotenv
load_dotenv()

elevenclient = ElevenLabs(
	api_key="ELEVENLABS_API_KEY" 
)

client = OpenAI()

def create_wakeup_call(filename, weather, news, calendar):
	setups = [
		{
			"voice_id": "lje26CmCiDS96gwa1RBG",
			"messages": [
				{
					"role": "user",
					"content": "You embody FBI Special Agent Dale Cooper from the TV series Twin Peaks, known for his keen investigative skills, profound fascination with the mystical aspects of the town, and his love for its charming quirks. Your speech is peppered with references to the enigmatic owls, your undying admiration for the town's exceptional cherry pie and black coffee, and other iconic elements from Twin Peaks. Whether it's drawing parallels between the mysteries you encounter and the peculiar events of Twin Peaks, or simply expressing your delight in small-town comforts, your dialogue naturally weaves in these elements, highlighting your deep connection to the series' lore and atmosphere. Always reply in english."
				}
			]
		},
		
		{
			"voice_id": "bSModmOcbBUB9xDlJDqX",
			"messages": [
				{
					"role": "user",
					"content": "You embody the mystical essence of the Log Lady from Twin Peaks, a character enshrouded in mystery and known for her profound connection to her log, which she believes communicates with her. In your dialogue, you deliver messages from your log, intertwining them with references to the haunting owls, the dense forests, and other ethereal elements that define the eerie atmosphere of Twin Peaks. Through your speech, you capture the Log Lady's unique blend of wisdom and eccentricity, offering cryptic insights and observations about the town and its mysteries. Your reverence for the natural world and the secrets it holds mirrors the Log Lady's role as a bridge between the tangible and the mystical, inviting others to look beyond the surface and explore the deeper connections that bind us all. Always reply in english."
				}
			]
		},
		{
			"voice_id": "HG12HSqz42nHnBmOYE1D",
			"messages": [
				{
					"role": "user",
					"content": "You adopt the persona of FBI Agent Albert Rosenfield from Twin Peaks, known for his razor-sharp wit and somewhat caustic demeanor. Despite your outward skepticism and biting commentary, your dialogue cleverly weaves in references to Twin Peaks' signature elements— the cryptic owls, the irresistible cherry pie, and the iconic, deeply satisfying coffee. Through your interactions, you balance Albert's distinctive blend of cynicism with a genuine, if grudging, appreciation for the town's peculiar charms. Your references to Twin Peaks not only serve as a nod to its unique culture but also add layers to your character, showcasing Albert's complex relationship with the town and its inhabitants, revealing a depth of character that goes beyond his initial facade. Always reply in english."
				}
			]
		},
		{
			"voice_id": "PfUGWeo6fUQGuxfEmkQL",
			"messages": [
				{
					"role": "user",
					"content": "You channel the exuberant spirit of FBI Agent Gordon Cole from Twin Peaks, a character celebrated for his larger-than-life personality and partial deafness, which leads to his distinctively loud speech. Your dialogue bursts with enthusiasm for the show's iconic elements, like the mysterious owls, delectable cherry pie, and the unparalleled black coffee of Twin Peaks. Along with these references, you might also mimic Gordon's habit of speaking in a booming voice, his penchant for poetic musings on the beauty of everyday life, and his deep admiration for the strange and wonderful aspects of Twin Peaks. Through your words, you echo Gordon Cole's infectious optimism and his delight in the small town's quirks, all while navigating the complex web of mysteries that Twin Peaks embodies. Only reply with what he says, nothing else. Always reply in english."
				}
			]
		},
		{
			"voice_id": "zdUFXgsZFbjJTMu3xg7s",
			"messages": [
				{
					"role": "user",
					"content": "You assume the ethereal presence of The Giant from Twin Peaks, a figure shrouded in mystery and known for his cryptic messages. In your dialogue, you intertwine subtle references to the enigmatic owls and the many mysteries of Twin Peaks, speaking in riddles and profound statements that hint at deeper truths. Your manner of communication is both intriguing and elusive, capturing The Giant's essence as a guide from another realm. Through your words, you invite others to ponder the mysteries of Twin Peaks, offering clues wrapped in mystique, much like The Giant himself, who serves as a pivotal beacon in the show's otherworldly narrative. Always reply in english."
				}
			]
		},
		{
			"voice_id": "lMYyDtSlAQIA15cDORkd",
			"messages": [
				{
					"role": "user",
					"content": "You take on the persona of Major Garland Briggs, a character revered for his wisdom and deep connection to the mysteries within the TV series Twin Peaks. Your dialogue elegantly incorporates references to the cryptic owls, the town's famously delicious cherry pie and robust coffee, among other quintessential elements of Twin Peaks. Through your speech, you convey a profound understanding of the show's intricate narrative and the mystical underpinnings of the small town. Your references not only demonstrate your affection for Twin Peaks' unique culture but also reflect Major Briggs' philosophical outlook and his pivotal role in unraveling the town's deepest secrets. Always reply in english."
				}
			]
		},
		# Add the rest of the setups here following the same structure
	]
	
	# Randomly select one setup
	selected_setup = random.choice(setups)
	# Accessing the selected setup
	voice_id = selected_setup["voice_id"]
	messages = selected_setup["messages"]

	now = datetime.now()
	
	# Extract date, weekday, and time
	current_date = now.date()
	weekday = now.strftime("%A")  # This gives the full weekday name
	current_time = now.time()
	
	# Combine into a single variable (as a string for example)
	date_weekday_time = f"Date: {current_date}, Weekday: {weekday}, Time: {current_time}"
	
	messages.append(
		{
			"role": "user",
			"content": f"Stay in character and wake Anders up based on this:\n\n\
Date and time:{date_weekday_time}\n\n\
Todays weather:{weather}\n\n\
Todays Calendar:```{calendar}```\n\n\
Todays News:```{news}```	\n\n\
Don't forget to include the time, day, month and weekday, the weather and the news. Only reply with the wake up call."
		}
	)
	print (messages)
	response = client.chat.completions.create(
		model="gpt-4o",
		messages=messages,
		temperature=1,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0
	)
	print (response.choices[0].message.content)
	print ("render audio")
	render_audio(filename, response.choices[0].message.content, voice_id)
	print ("render audio done")
	return response.choices[0].message.content
	
def summarize_news(content):
	print ("summarize news")
	response = client.chat.completions.create(
		model="gpt-4o",
		messages=[
			{
				"role": "user",
				"content": f"The content below is from extracting text from a webpage. Summarize the top news for me: \n\n{content}"
			}
		],
		temperature=1,
		max_tokens=256,
		top_p=1,
		frequency_penalty=0,
		presence_penalty=0
	)
	print ("summarize news done")
	return response.choices[0].message.content

def render_audio(filepath, text, voice_id):
	# Split the text into paragraphs
	paragraphs = text.split('\n\n')
	
	temp_files = []
	
	try:
		for i, paragraph in enumerate(paragraphs):
			if paragraph.strip():  # Skip empty paragraphs
				# Generate audio for each paragraph
				print (f"Generates partial audio for: {paragraph}")
				audio = elevenclient.generate(text=paragraph, voice=voice_id, model='eleven_multilingual_v2')
			
				# Save temporary file
				temp_filepath = f"temp_audio_{i}.mp3"
				save(audio, temp_filepath)
				temp_files.append(temp_filepath)
			
		# Combine all audio files
		combined = AudioSegment.empty()
		for temp_file in temp_files:
			segment = AudioSegment.from_mp3(temp_file)
			combined += segment
			
		# Export the final audio file
		combined.export(filepath, format="mp3")
		
	finally:
		# Clean up temporary files
		for temp_file in temp_files:
			if os.path.exists(temp_file):
				os.remove(temp_file)

def fetch_webpage_text(url):
	print (f"fetching news ({url})")
	try:
		response = requests.get(url)
		response.raise_for_status()  # This will raise an exception for HTTP errors
		
		# Parse the content with BeautifulSoup
		soup = BeautifulSoup(response.content, 'html.parser')
		print ("fetching news done")
		return soup.get_text(separator='\n', strip=True)
	except requests.RequestException as e:
		print ("fetching news error")
		return str(e)

def get_weather(location):
	print ("fetching weather")
	base_url = f"http://wttr.in/{location}?M"
	# Updated format string to include wind speed in m/s
	params = {
		'format': 'Location: %l\nWeather: %C\nTemperature: %t (feels like: %f)\nWind: %w\nPressure: %P\nHumidity: %h'
	}
	
	try:
		response = requests.get(base_url, params=params, timeout=30)
		response.raise_for_status()  # Raises an exception for HTTP errors
		print ("fetching weather done")
		return response.text.strip()
	except requests.RequestException as e:
		print ("fetching weather error")
		return str(e)

def get_todays_icloud_events(username, app_specific_password):
	
	print ("fetching calendar")
	
	# iCloud CalDAV URL
	url = 'https://caldav.icloud.com/'
	
	# Connect to the CalDAV server
	client = caldav.DAVClient(url, username=username, password=app_specific_password)
	principal = client.principal()
	calendars = principal.calendars()
	summary = ""
	if calendars:
		print("1")
		# Assuming you want to check the first calendar
		calendar = calendars[4]
#		print(calendars)
		# Define the time range for today
		now = datetime.now(pytz.utc)
		start = datetime(now.year, now.month, now.day, tzinfo=pytz.utc)
		end = start + timedelta(days=1)
		
		# Fetch events for today
		events = calendar.date_search(start, end)
		
		for event in events:
			#print(event.instance.vevent.summary.value, event.instance.vevent.dtstart.value)
			summary = f"{summary}\n{event.instance.vevent.summary.value}, {event.instance.vevent.dtstart.value}"
		print (summary)
		print ("fetching calendar done")
		return summary
	
	else:
		print("No calendars found.")
		return []

def fade_audio_add_clip(main_file_path, additional_clip_path, start_fade_time, fade_duration, new_volume_percentage, overlay_start_time):
	# Load the main audio file
	audio = AudioSegment.from_mp3(main_file_path)
	
	# Load the additional audio clip
	additional_clip = AudioSegment.from_mp3(additional_clip_path)
	
	# Convert times to milliseconds
	start_fade_time_ms = start_fade_time * 1000
	fade_duration_ms = fade_duration * 1000
	overlay_start_time_ms = overlay_start_time * 1000
	
	# Split the audio into two parts
	before_fade = audio[:start_fade_time_ms]
	after_fade = audio[start_fade_time_ms:]
	
	# Calculate the target volume in dBFS
	target_volume_dbfs = audio.dBFS + 20 * log10(new_volume_percentage / 100)
	
	# Apply fade effect to the beginning of the after_fade section
	after_fade_start = after_fade[:fade_duration_ms].fade(to_gain=target_volume_dbfs, end=len(after_fade[:fade_duration_ms]), duration=fade_duration_ms)
	after_fade_remainder = after_fade[fade_duration_ms:]
	
	# Adjust the volume of the remainder of the after_fade section to match the target volume
	after_fade_remainder = after_fade_remainder - (after_fade_remainder.dBFS - target_volume_dbfs)
	
	# Combine the sections
	faded_audio = before_fade + after_fade_start + after_fade_remainder
	
	# Overlay the additional clip at 32 seconds
	combined_audio = faded_audio.overlay(additional_clip, position=overlay_start_time_ms)
	
	timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
	
	# Format the filename to include the timestamp
	filename = f"combined_audio_twinpeaks_{timestamp}.mp3"
	
	# Export the audio with the timestamped filename
	combined_audio.export(filename, format="mp3")
	
	return (filename)
	
def play_mp3(file_path):
	
	# Initialize pygame mixer
	pygame.mixer.init()
	
	# Load the MP3 file
	pygame.mixer.music.load(file_path)
	
	# Start playing the MP3 file
	pygame.mixer.music.play()
	
	# Wait for the music to finish playing
	while pygame.mixer.music.get_busy():
		time.sleep(1)
		

#print (calendar)
url = "http://dn.se"
location = "Kalmar"
news = summarize_news(fetch_webpage_text(url))
weather = get_weather(location)
calendar = get_todays_icloud_events('name@icloud.com', '1234-1234-1234-1234')	#https://appleid.apple.com/


current_timestamp = datetime.now()

# Format the timestamp as 'YYYYMMDD_hhmmss'
formatted_timestamp = current_timestamp.strftime("%Y%m%d_%H%M%S")

# Append .mp3 extension
filename = f"{formatted_timestamp}.mp3"

create_wakeup_call(filename, weather, news, calendar)

# Use the function on your audio files
music_folder = 'music'

# List all files in the music folder
files = os.listdir(music_folder)

# Filter for MP3 files
mp3_files = [file for file in files if file.endswith('.mp3')]
#print (mp3_files)
# Select a random MP3 file
random_mp3 = random.choice(mp3_files)
print (f"selected {random_mp3}")
# Your function call, using the randomly selected MP3 file
filepath = fade_audio_add_clip(os.path.join(music_folder, random_mp3), filename, 5, 5, 5, 10)
#
play_mp3(filepath)
