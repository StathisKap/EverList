CC = gcc
CFLAGS = -lcurl
EverList: Scrapper.c
	$(CC) -o $@ $< $(CFLAGS)	
