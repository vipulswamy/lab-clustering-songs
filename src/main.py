from functions import *



if __name__ == '__main__':

	while True:

		try:
			song = get_user_song()
		except KeyboardInterrupt:
			print("\nQuitting ...\n")
			break

		cluster = get_user_song_cluster(song)

		if cluster == -1:
			continue

		#print(f"\033[1;32mCluster\033[0m: {cluster}")
		recommend_song(song, cluster, 3)
