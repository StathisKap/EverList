CC = gcc
CFLAGS = -lcurl
EverList: Recipies.c
	$(CC) -o $@ $< $(CFLAGS)	