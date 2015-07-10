import pyaudio
import pygame
import math
import matplotlib.pyplot as plt
import numpy as np
import time
import wave
import sys
import numpy as np
import os
from scipy.io.wavfile import write

speaker_type =  2#0 for headphone, 1 for PC speaker,2 for external speaker
graph = 0
volume = 0
MIN_VOLUME = 0.4
CHUNK = 1024 
FORMAT = pyaudio.paInt16 #paInt8
CHANNELS = 1 
RATE = 44100 #sample rate
RECORD_SECONDS = .5
FALL_TIME = 2
WAVE_OUTPUT_FILENAME = "output.wav"
#WAVE_INPUT_FILENAME = "music/eminem.wav"
#WAVE_INPUT_FILENAME = "music/baris.wav"
#WAVE_INPUT_FILENAME = "music/alizee.wav"
WAVE_INPUT_FILENAME = "music/self_control.wav"
RATIO = .67
delay = 0
VOLUME_LEVELS = 14
FALL_COUNTER = FALL_TIME/RECORD_SECONDS



if (speaker_type == 0):
	treshold1=60000000 * RECORD_SECONDS
	treshold2=120000000 * RECORD_SECONDS
else:
	treshold1=10000000 * RECORD_SECONDS
	treshold2=23000000 * RECORD_SECONDS


ratio = 3 * 1.5
treshold 	 = 1
true=1
ex_volume = 0
down_counter = 0
volume_range = treshold2 - treshold1



def play_init_mono():
	pygame.mixer.pre_init(frequency=RATE,channels=CHANNELS)
	pygame.init()
	
def play_from_signal(signal):
	sound = pygame.sndarray.make_sound(signal)
	pygame.mixer.Sound.play(sound)

def record(second,volume):
	p = pyaudio.PyAudio()
	os.system("clear")
	if volume <= 0:
		print("VOlume level is 1/16   (-               )\n")
	elif volume > VOLUME_LEVELS :
		print("VOlume level is 16/16   (----------------)\n")
	else:
		vol_str = str(int(volume +1))
		print("VOlume level is " + vol_str + "/16   (" +"-"*(volume+1) + " "*(VOLUME_LEVELS+1-volume) + ")\n")



	stream = p.open(format=FORMAT,
		        channels=CHANNELS,
		        rate=RATE,
		        input=True,
		        frames_per_buffer=CHUNK) #buffer


	frames = []
	delay = pygame.mixer.music.get_pos()
	for i in range(0, int(RATE / CHUNK * second)):
	    data = stream.read(CHUNK)
	    frames.append(data) # 2 bytes(16 bits) per channel



	stream.stop_stream()
	stream.close()
	p.terminate()

	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(b''.join(frames))

	wf.close()
	return delay


def wav2signal(filename):
	spf = wave.open(filename,'rb')
	#Extract Raw Audio from Wav File
	signal = spf.readframes(-1)
	signal = np.fromstring(signal, 'Int16')
	return signal

def playwav(filename):

	pygame.init()
	pygame.mixer.music.load(filename)
	pygame.mixer.music.set_volume(.3)
	pygame.mixer.music.play()

	#pygame.event.wait()

def createwav(signal,filename):
	#signal = np.random.uniform(-1,1,44100) # 44100 random samples between -1 and 1
	scaled = np.int16(signal)
	write(filename, 44100, scaled)

def printwav(filename):
	spf = wave.open(filename,'rb')
	#Extract Raw Audio from Wav File
	signal = spf.readframes(-1)
	signal = np.fromstring(signal, 'Int16')
	print signal


def plot(figure, title , i):

	plt.figure(i)
	plt.title(title)
	plt.plot(figure)

def filter(signal):
	fft = np.fft.fft(signal)
	fft[:(20*len(fft)/RATE)] = 0
	fft[len(fft)-(20*len(fft)/RATE):] = 0
	fft[(3000*len(fft)/RATE):(len(fft)-(3000*len(fft)/RATE))] = 0
	return np.fft.ifft(fft)

def find_delay(music,record): 
	cuttedmusic = music[50000:100000] 
	searchingrecord = record[50000:250000]
	#print("Min value: " , np.amin(cuttedmusic))

	min_diff = 3000000000
	min_index = 0
	for i in range(0,100000):
		difference = searchingrecord[i:len(cuttedmusic)+i] - cuttedmusic
		sum_diff = np.abs(np.sum(difference))
		if(sum_diff < min_diff):
			min_diff = sum_diff
			min_index = i
		#samples [i] = difference
	print(min_diff)
	print("Delay = " + str(min_index) + " samples")
	return min_index

def findratio():

	time.sleep(2)
	music = wav2signal(WAVE_INPUT_FILENAME)	
	#play_init_mono()
	#play_from_signal(music)
	playwav(WAVE_INPUT_FILENAME)

	#record(10)
	delay = math.ceil(record(15) *44.1)
	print("Delay is " + str(math.ceil(delay/10000))	 + " samples.\n")
	rec = wav2signal(WAVE_OUTPUT_FILENAME)
	rec_lowpass = filter(rec);
	ratio = float(np.sum(np.absolute(music[44100*5:44100*12])))/float(np.sum(np.absolute(rec_lowpass[delay + 44100*5:delay + 44100*12])))
	speaker = os.popen("amixer -D pulse sget Master| tail -2|head -1").read()
	mic = os.popen("amixer get Capture|tail -2|head -1").read()
	with open("ratio.txt", "a") as myfile:
		myfile.write(WAVE_INPUT_FILENAME + " Speaker: " + speaker[29:34] +" Mic: " + mic[25:30] + " Ratio: " + str(1/ratio) + "\n") 
	
	pygame.mixer.music.stop()





	


"""""""""""""""""""""""""""""""""""
MAIN
"""""""""""""""""""""""""""""""""""

#findratio()
"""for x in xrange(1,5):
	findratio()"""



playwav(WAVE_INPUT_FILENAME)
music = wav2signal(WAVE_INPUT_FILENAME)


if graph==1:
	fig = plt.figure()
	ax = fig.add_subplot(111)


	x = np.arange(0,float(44100*15))
	x = x/44100
	y = music[:15*44100]
	y[0] = -100000
	y[1] = 100000
	li, = ax.plot(x, y)
	fig.canvas.draw()

	plt.show(block=False)





while true:
	try:

		delay =	int(math.ceil(record(RECORD_SECONDS,volume)*44.1))
		recorded = wav2signal(WAVE_OUTPUT_FILENAME)
		recorded_lowpass = filter(recorded)


		#x = np.linspace(1000*delay/44.1,1000*delay/44.1+5,44100*5)
		x = np.arange(float(delay),float(delay + 44100*15))
		x = x/44100
		
		if(graph == 1):	
			#y=music[delay:delay+44100*15]
			if(len(music) > delay+44100*15 ):
				y=music[delay:delay+44100*15]
			else:
				y =np.append(music[delay:],np.zeros(44100*15+delay -len(music)))
			if(len(y) != len(x)):
				y = np.zeros(44100*15)
			#else:
			#	y = np.zeros(44100*15)
			#	print("length y" + str(len(y)))
		
			li.set_ydata(y)
			li.set_xdata(x)
			ax.relim()
			ax.autoscale_view(True,True,False)
			fig.canvas.draw()



		if (speaker_type == 1):
			recordenergy = np.sum(np.absolute(recorded_lowpass))/ratio
			#recordenergy = np.sum(np.absolute(recorded_lowpass))/ratio
			musicenergy = np.sum(np.absolute(music[delay:delay + len(recorded_lowpass)]))
		elif(speaker_type == 2):
			recordenergy = np.sum(np.absolute(recorded_lowpass))
			#recordenergy = np.sum(np.absolute(recorded_lowpass))/ratio
			musicenergy = np.sum(np.absolute(music[delay:delay + len(recorded_lowpass)]))


		magabs = np.absolute(recorded)

		if(speaker_type == 0):
			magnitudesum = np.sum(np.absolute(recorded_lowpass))			
		elif(speaker_type == 1):
			magnitudesum = recordenergy - musicenergy*pygame.mixer.music.get_volume()
		else:	
			magnitudesum = recordenergy

		with open("noise.txt", "a") as myfile:
			myfile.write(str(magnitudesum)+'\n')


		volume = math.ceil((magnitudesum-treshold1)/volume_range * VOLUME_LEVELS)

		if volume > ex_volume:
			down_counter = 0
			volume = ex_volume+1
		elif volume == ex_volume:
			volume =ex_volume
		else:
			down_counter = down_counter +1
			if(down_counter >= FALL_COUNTER):
				down_counter = FALL_COUNTER
				volume = ex_volume-1
			else:
				volume =ex_volume


		if volume < 0:
			pygame.mixer.music.set_volume(MIN_VOLUME)
		elif volume > VOLUME_LEVELS :
			pygame.mixer.music.set_volume(1)

		else:
			pygame.mixer.music.set_volume(MIN_VOLUME + volume*(1-MIN_VOLUME)/VOLUME_LEVELS)


		ex_volume = volume


		


	except KeyboardInterrupt:
		break























