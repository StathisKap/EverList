CC = gcc
CFLAGS = -lcurl
EverList: Scrapper.c
	$(CC) -o $@ $< $(CFLAGS)

Dependencies:
	sudo apt-get install libcurl4-gnutls-dev
