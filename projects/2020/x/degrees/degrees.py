

import csv
import sys
import random

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def list_people(sample=False):
    """
    Print a sample of the actor names as a mnemonic to help the user!
    The 'sample' parameter either prints all the names or a random
    sample of 20 names.
    """
    print("Loaded %d actors."%(len(people)))
    if sample:
        pkeys = list(people.keys())
        psamp = list()
        if len(pkeys) > 20:
            while len(psamp) < 20:
                item = pkeys[random.randint(0,(len(pkeys)-1))]
                if item not in psamp:
                    psamp.append(item)
        else:
            psamp = pkeys

        for person in psamp:
            print(people[person]['name'])
    else:
        for person in people:
            print(people[person]['name'])


# Interesting pairs:
# Easy - Relatively short running
#   Kevin Bacon --> Tom Hanks               1 degree        92 states
#   Dwayne Johnson --> Susan Sarandon       1 degree        69 states
#   Kevin Bacon --> Harrison Ford           2 degrees       4250 states
#
# Hard - Long running
#   Emma Watson --> William Shatner         3 degrees       7483 states
#   Harrison Ford --> Molly Ringwald        3 degrees       26121 states
#
# Extra long running ...
#   Sylvester Stallone --> Judy Garland     ? degrees       over 305000 states explored
#       > This search is really bad - likely because of the use of list()
#       > modifying large list() structures in Python is wildly expensive
#

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    list_people(sample=True)

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    Inputs:
        source - person id of source
        target - person id of target

    If no possible path, returns None.
    """

    # set up some scratch variables
    states_explored = 0
    found = None
    path = list()
    candidates = QueueFrontier()
    explored = list()

    # initialize Node objects for the source and target
    target_node = Node(get_person(target),None,None)
    source_node = Node(get_person(source),None,None)

    # check - is the source and target already the same?
    if is_goal_node(source_node,target_node):
        path.append(source_node)
        return path

    # add the initial node to the 'frontier' to be explored
    candidates.add(source_node)
    while not candidates.empty():
        n = candidates.remove()

        # check to see if this is the goal node
        if is_goal_node(n,target_node):
            # if goal, exit loop
            found = n
            break

        # mark this node as explored
        explored.append(n.state)
        states_explored += 1

        # a little tracking and output
        if (states_explored%1000) == 0:
            print("Explored %d states."%(states_explored))
            print("\tHave %d states in 'explored' list."%len(explored))
            print("\tCurrently have %d states in the frontier"%len(candidates.frontier))
            sys.stdout.flush()
            sys.stderr.flush()

        # not the goal, so we need to expand (explore) the states from n
        # in this case we first find all of the neighbors of n (states)
        neighbors = neighbors_as_people(n)
        for state in neighbors:
            # for each of the states in the neighbors list
            #   if the state is not already an explored state
            #       and the state is not already a candidate state
            #           add the state to the candidates queue/stack
            if state in explored :
                continue
            if not candidates.contains_state(state):
                p = Node(state,n,"traverse_edge")
                candidates.add(p)

    # prepare the list
    n = found
    # cursor through the list and build the reversed list of 'states'
    while n:
        path.append(n.state)
        n = n.parent
    print("Explored %d total states!"%(states_explored))
    if len(path) > 0:
        path.reverse()
        # remove start node to fix path list for output code assumptions
        path = path[1:]
        return path
    return None


def is_goal_node(node,target):
    """
    Checks to see if we reached a goal state
    """
    if node.state[1] == target.state[1]:
        return True
    return False


def get_person(person_id):
    """
    returns a tuple of (movie_id,person_id,person) given either a
    (movie_id,person_id) tuple or
    just a person_id
    """
    pid = person_id
    mid = -1
    if isinstance(person_id,tuple):
        mid = person_id[0]
        pid = person_id[1]
    if pid in people:
        p = people[pid]
        p['id'] = pid
        return (mid,pid,p)
    return tuple()


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_as_people(node):
    """
    Return a list of neighbors as person_id,movie_id,person tuples
    """
    people_neighbors = list()
    neighbors = neighbors_for_person(node.state[1])
    for n in neighbors:
        people_neighbors.append(get_person(n))
    return people_neighbors


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
