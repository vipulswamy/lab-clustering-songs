import pandas as pd
import numpy as np
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import json
import time

from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture

import pickle

from config import *



def get_audio_features(sp, uri):

	d = {}
	audio_feat = sp.audio_features(uri)[0]

	if audio_feat == None:
		print("! Failed to get audio features")
		return None
	else:
		d['danceability'] = audio_feat['danceability']
		d['energy'] = audio_feat['energy']
		d['key'] = audio_feat['key']
		d['loudness'] = audio_feat['loudness']
		d['mode'] = audio_feat['mode']
		d['speechiness'] = audio_feat['speechiness']
		d['acousticness'] = audio_feat['acousticness']
		d['instrumentalness'] = audio_feat['instrumentalness']
		d['liveness'] = audio_feat['liveness']
		d['valence'] = audio_feat['valence']
		d['tempo'] = audio_feat['tempo']
		d['type'] = audio_feat['type']
		d['id'] = audio_feat['id']
		d['uri'] = audio_feat['uri']
		d['track_href'] = audio_feat['track_href']
		d['analysis_url'] = audio_feat['analysis_url']
		d['duration_ms'] = audio_feat['duration_ms']
		d['time_signature'] = audio_feat['time_signature']
		return d

def cluster_song(df):

	# Load scaler
	with open('../scalers/scaler.pickle', 'rb') as file:
		scaler = pickle.load(file)

	# Load clustering model
#	with open('../models/aggl12.pickle', 'rb') as file:
#		model = pickle.load(file)

	with open('../models/kmeans_16.pickle', 'rb') as file:
		model = pickle.load(file)

	# Get features needed
	X = df.select_dtypes(np.number).drop(['mode', 'duration_ms', 'time_signature'], axis=1)

	# Scale and cluster
	X_scaled = scaler.transform(X)
	X_scaled_df = pd.DataFrame(X_scaled, columns=X.columns)
	print(X_scaled_df.T)
	print(df)


	y = model.predict(X_scaled_df)
#	y = model.fit_predict(X_scaled_df)

	return y[0]


def get_user_song():
	song = input("\nPlease enter a song: ")
	return song


def get_user_song_cluster(song):
	sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id,
			client_secret=client_secret))

	try:
		result = sp.search(q=f'track:{song}', limit=1)
		uri = result['tracks']['items'][0]['uri']
		#print(f'\nURI: {uri}')

		audio_feat = get_audio_features(sp, uri)
		if not audio_feat:
			print(f"! Can't get audio-features for song '{song}'")

	except:
		print(f"! Can't get audio-features for song '{song}'")
		return -1


	df = pd.DataFrame([audio_feat])
	cluster = cluster_song(df)
	return cluster


def recommend_song(song, cluster, n_recommend=1):


	def show_recommendation(row):
		print(f"{row['title']} - {row['artist']}")


	is_hot = False
	df = pd.read_csv('../songs_clustered.csv')

	if not df[df['title'] == song].empty:
		if df[df['title'] == song]['hot'].item() == 1:
			is_hot = True

	print("\nRecommended:")
	if is_hot:
		reco = df[(df['hot'] == 1) & (df['cluster_kmeans_16'] == cluster)].sample(n_recommend)
		reco.apply(show_recommendation, axis=1)
	else:
		reco = df[(df['hot'] == 0) & (df['cluster_kmeans_16'] == cluster)].sample(n_recommend)
		reco.apply(show_recommendation, axis=1)



