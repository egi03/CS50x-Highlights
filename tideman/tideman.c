#include <cs50.h>
#include <stdio.h>
#include <string.h>

// Max number of candidates
#define MAX 9

// preferences[i][j] is number of voters who prefer i over j
int preferences[MAX][MAX];

// locked[i][j] means i is locked in over j
bool locked[MAX][MAX];

// Each pair has a winner, loser
typedef struct
{
    int winner;
    int loser;
}
pair;

// Array of candidates
string candidates[MAX];
pair pairs[MAX * (MAX - 1) / 2];

int pair_count;
int candidate_count;

// Function prototypes
bool vote(int rank, string name, int ranks[]);
bool cycle(int winner, int loser);
void record_preferences(int ranks[]);
void add_pairs(void);
void sort_pairs(void);
void lock_pairs(void);
void print_winner(void);
int main(int argc, string argv[])
{
    // Check for invalid usage
    if (argc < 2)
    {
        printf("Usage: tideman [candidate ...]\n");
        return 1;
    }

    // Populate array of candidates
    candidate_count = argc - 1;
    if (candidate_count > MAX)
    {
        printf("Maximum number of candidates is %i\n", MAX);
        return 2;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        candidates[i] = argv[i + 1];
    }

    // Clear graph of locked in pairs
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = 0; j < candidate_count; j++)
        {
            locked[i][j] = false;
        }
    }

    pair_count = 0;
    int voter_count = get_int("Number of voters: ");

    // Query for votes
    for (int i = 0; i < voter_count; i++)
    {
        // ranks[i] is voter's ith preference
        int ranks[candidate_count];

        // Query for each rank
        for (int j = 0; j < candidate_count; j++)
        {
            string name = get_string("Rank %i: ", j + 1);

            if (!vote(j, name, ranks))
            {
                printf("Invalid vote.\n");
                return 3;
            }
        }

        record_preferences(ranks);

        printf("\n");
    }

    add_pairs();
    sort_pairs();
    lock_pairs();
    print_winner();
    return 0;
}

// Update ranks given a new vote
bool vote(int rank, string name, int ranks[])
{
    // Check if user entered on of candidates' names and update ranks array
    for (int i = 0; i < candidate_count; i++)
    {
        if (strcmp(name, candidates[i]) == 0)
        {
            ranks[rank] = i;
            return true;
        }
    }
    return false;
}
// Update preferences given one voter's ranks
void record_preferences(int ranks[])
{
    //Update preferences array for each vote
    for (int i = 0; i < candidate_count; i++)
    {
        for (int j = i; j < candidate_count; j++)
        {
            //Condition -> if both number are the same don't change (preferences[1][1], [0][0]...)
            if (ranks[i] != ranks[j])
            {
                preferences[ranks[i]][ranks[j]]++;
            }
        }
    }
    return;
}

// Record pairs of candidates where one is preferred over the other
void add_pairs(void)
{
    //Check which candidate has more votes and update pairs winner and loser
    int c = 0;
    pair_count = 0;
    for (int i = 0; i < candidate_count; i++)
    {
        //No case if both are the same
        for (int j = i; j < candidate_count; j++)
        {
            if (preferences[i][j] > preferences[j][i])
            {
                pairs[c].winner = i;
                pairs[c].loser = j;
                pair_count++;
                c++;
            }
            else if (preferences[i][j] < preferences[j][i])
            {
                pairs[c].winner = j;
                pairs[c].loser = i;
                pair_count++;
                c++;
            }
        }
    }
    return;
}

// Sort pairs in decreasing order by strength of victory
void sort_pairs(void)
{
    for (int i = 0; i < pair_count; i++)
    {
        for (int j = i; j < pair_count; j++)
        {
            if (((preferences[pairs[j].winner][pairs[j].loser]) - (preferences[pairs[j].loser][pairs[j].winner]))  >= ((
                        preferences[pairs[i].winner][pairs[i].loser]) - (preferences[pairs[i].loser][pairs[i].winner])))
            {
                int tempw = pairs[i].winner;
                int templ = pairs[i].loser;
                pairs[i].winner = pairs[j].winner;
                pairs[i].loser = pairs[j].loser;
                pairs[j].winner = tempw;
                pairs[j].loser = templ;
            }
        }
    }
    return;
}

bool cycle(int winner, int loser)
{
    if (locked[loser][winner] == true)
    {
        return true;
    }
    for (int i = 0; i < candidate_count; i++)
    {
        if (locked[loser][i] == true && cycle(winner, i))
        {
            return true;
        }
    }
    return false;
}

void lock_pairs(void)
{

    for (int i = 0; i < pair_count; i++)
    {
        locked[i][i] = false;
        if (cycle(pairs[i].winner, pairs[i].loser) == false)
        {
            locked[pairs[i].winner][pairs[i].loser] = true;
            locked[pairs[i].loser][pairs[i].winner] = false;
        }
    }
    return;
}

void print_winner(void)
{
    // Print winner
    int c = 0;
    int temp;
    for (int i = 0; i < candidate_count; i++)
    {
        c = i;
        temp = 1;
        for (int j = 0; j < candidate_count; j++)
        {
            if (locked[j][i] == true)
            {
                temp = 0;
            }
        }
        if (temp == 1)
        {
            break;
        }
    }
    printf("%s\n", candidates[c]);
    return;
}
