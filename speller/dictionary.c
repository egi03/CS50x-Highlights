// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include "dictionary.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>


// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 26;
unsigned int c = 0;

// Hash table
node *table[N];

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // TODO
    int number = hash(word);
    node *temp = table[number];

    //Go trought words and see if they are the same
    while (temp != NULL)
    {
        if (strcasecmp(temp->word, word) != 0)
        {
            temp = temp->next;
        }
        else
        {
            return true;
        }

    }
    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // TODO: Improve this hash function
    long sum = 0;
    for (int i = 0; i < strlen(word); i++)
    {
        sum = sum + tolower(word[i]);
    }
    int result = sum % N;
    return result;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    //Open selected dictionary
    FILE *f = fopen(dictionary, "r");

    if (f == NULL)
    {
        printf("Cannot open the dictionary");
        return false;
    }

    //Read every word from dictionary
    char s[LENGTH + 1];
    int number;

    while (fscanf(f, "%s", s) != EOF)
    {
        node *new = malloc(sizeof(node));
        if (new == NULL)
        {
            free(new);
            return false;
        }
        strcpy(new->word, s);
        number = hash(s);
        if (table[number] == NULL)
        {
            new->next = NULL;
        }
        else
        {
            new->next = table[number];
        }
        table[number] = new;
        c++;
    }
    free(new);
    fclose(f);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    // C count words from load function and it's set to 0 as default
    return c;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // Free memory
    for (int i = 0; i < N; i++)
    {
        node *cursor = table[i];
        while (cursor)
        {
            node *temp = cursor;
            cursor = cursor->next;
            free(temp);
        }
        if (cursor == NULL)
        {
            return true;
        }
    }
    return false;
}