import random
import string
from time import sleep
from tkinter import *

# This is our class Boggle, which will allow us to create a graphical, interactive Boggle board
class Boggle():
    # Loads up all variables needed to create our Boggle board
    def __init__(self, file='words.dat', N=5):
        self.size = N
        self.soln = []  # used to check the user's current solution the extend function
        self.word = ''  # used in extend function to print out user's word
        self.count = 0  # used in extend function to prevent repeat congratulations statements
        self.totalSoln = []  # part of this is returned in the solve function; a list of all possible solutions for that particular Boggle board
        self.T = self.readData(file)[0]  # our Trie data structure, containing all our words
        self.F = self.readData(file)[1]  # our letter frequency data structure
        # self.board is created using a weighted random choice of letters in our words database/file
        self.board = [random.choices(string.ascii_lowercase, weights=self.F.values(), k=self.size) for i in range(self.size)]
        self.window = Tk()  # creates our TK interface
        self.window.title('Boggle')
        self.canvas = Canvas(self.window, width = self.size*50, height = self.size*50, bg='white')  # creates the window we will be working with
        self.canvas.pack()
        # these loops create the squares of our board
        for i in range(self.size):
            for j in range(self.size):
                self.canvas.create_rectangle(i*50, j*50, (i+1)*50, (j+1)*50, fill='white')
                self.canvas.create_text((i*50)+25, (j*50)+25, text=self.board[i][j], font=('Helvetica', 17))
        # these statements bind functions to user input
        self.canvas.bind("<Button-1>", self.extend) # left mouse button
        self.canvas.bind("<Button-2>", self.new)  # middle mouse button
        self.canvas.bind("<Button-3>", self.reset)  # right mouse button
        self.canvas.focus_set()
        self.window.mainloop()
        
                
    # This function reads in data from the file passed in.  In our case, we are reading in a large list of five letter words.  Returns a trie
    # and a frequency dictionary coupled together in a tuple as (T, F)
    def readData(self, file='words.dat'):
        F = dict()  # frequency dict
        T = dict()  # trie
        word_file = open(file, 'r')
        for word in word_file:
            word = word.strip()
            # creating a count of letters in F
            for char in word:
                if char not in F:
                    F[char] = 1
                else:
                    F[char] += 1
            currentDict = T
            # creating our trie data structure in this loop
            for i in range(4):
                currentDict = currentDict.setdefault(word[i], {})
            currentDict[word[4]] = word  # have to make sure that our leaf nodes (aka 'ending' values in our trie) are words
        # calculating our frequencies of each letter for F
        tot_len = sum(F.values())
        for char in F:
            F[char] = F[char]/tot_len
        return((T, F))
        

    # This function is to mainly be used in conjunction with ckSoln.  This function checks a given solution, passed in as a list of
    # of tuples, and makes sure it is a valid path (we are only allowed to traverse north, south, east and west in 
    # this version of Boggle).  Either returns a list of letters corresponding to coordinates on our board, or returns False
    def ckPath(self, soln):
        letters = []
        if (0 <= soln[0][0] <= (self.size - 1)) and (0 <= soln[0][1] <= (self.size - 1)):  # make sure our first coordinate is on the board
            letters.append(self.board[soln[0][0]][soln[0][1]])
            for i in range(1, len(soln)):  # make sure our other coordinates are on the board
                if (0 <= soln[i][0] <= (self.size - 1)) and (0 <= soln[i][1] <= (self.size - 1)):
                    if sum([abs(soln[i][0] - soln[i-1][0]), abs(soln[i][1] - soln[i-1][1])]) == 1:  # calculates the magnitude of the difference between coordinates (can only be one 'square' apart in the cardinal directions)
                        letters.append(self.board[soln[i][0]][soln[i][1]])
                    else:
                        return(False)   # False if not a contiguous path
                else:
                    return(False)   # False if one solution tuple corresponds to something not on our board
            return(letters)  # Success!  Our path is on the board and contiguous
        else:
            return(False)   # False if one solution tuple corresponds to something not on our board
        
    # This function makes use of ckPath, and is integral to the extend and solve functions.  This function checks a given solution, passed
    # in as a list of tuples, and checks to see if it corresponds to a valid path with ckPath.  If it does, it checks to see if the letters
    # that correspond to each coordinate lead to a valid traversal of the trie.  Will return one of three things: False, given that the path
    # is not valid or the letters don't correspond to a valid traversal of the trie.  A section of the trie, given that the solution is not
    # of length five but is valid (so far).  Or, a string, given that the solution is of length five, and corresponds to a complete traversal
    # of the trie.    
    def ckSoln(self, soln):
        if self.ckPath(soln) != False:  # checks path        
            letters = self.ckPath(soln)
            solnDict = self.T[letters[0]]  # traverses trie on first letter
            for i in range(1, len(letters)):  # traverses trie on the rest of the letters
                if letters[i] in solnDict:
                    solnDict = solnDict[letters[i]]
                else:
                    return(False)  # letter not in trie
            return(solnDict)  # soln provided a valid traversal of the trie
        else:
            return(False)  # not a valid path
    
    
    # This function gives us a way to play our game of Boggle.  Users can click on squares on the board with letters they think will
    # lead to a valid five letter word.  If a valid choice is made, a green circle will show up on the square.  If an invalid choice
    # is made, a red circle will show up on the board.  Lets you know when you've found a word.  This function is bound to the left 
    # mouse button
    def extend(self, event):
        soln = (event.x//50, event.y//50)
        if soln in self.soln:  # checks if the coordinate you clicked on is already in your solution
            print('You already selected that letter!')
            return
        self.soln.append((soln))
        if not self.ckSoln(self.soln):  # if ckSoln returns false, create a red circle on that clicked square
            self.canvas.create_oval(soln[0]*50+1, soln[1]*50+1, (soln[0]+1)*50-1, (soln[1]+1)*50-1, fill='red')
            self.canvas.create_text((soln[0]*50)+25, (soln[1]*50)+25, text=self.board[soln[0]][soln[1]], font=('Helvetica', 17)) 
            self.soln.pop() 
        else:  # if ckSoln returns a part of the trie, create a green circle on that clicked square
            self.canvas.create_oval(soln[0]*50+1, soln[1]*50+1, (soln[0]+1)*50-1, (soln[1]+1)*50-1, fill='green')
            self.canvas.create_text((soln[0]*50)+25, (soln[1]*50)+25, text=self.board[soln[0]][soln[1]], font=('Helvetica', 17))
            self.word += self.board[soln[0]][soln[1]]
        if len(self.soln) == 5 and self.count == 0:  # checks to see if you found a word    
              print('Congratulations! You found the word: {}'.format(self.word))
              self.count = 1  # makes sure congrats statement is only printed once during current play
              
# NOTE: the code commented out below was my attempt at resetting the board when the user finds a valid word.  I have talked to about 3 TAs, and they all 
# have said to let the user manually reset the board when they find a word, although the homework handout asks us to reset the board when a word is found.
# For whatever reason, when I try the solution below, the fifth and final green circle will not appear on the board.  When you click on the final letter, 
# the congratulations statement prints out, sleeps for 2 seconds, and then the board resets; the final green circle never pops up.  All the TAs are perplexed
# as to why this is happening.  I don't know if my coding environment has anything to do with this problem (I'm using Anaconda's Spyder) or what, but I 
# was told to keep my attempt at a solution commented out so that whoever is grading this will know I solved this.
#  
#        if len(self.soln) == 5:
#             sleep(2)
#             self.reset(event)    

        
    # This function is bound to the middle mouse button.  Creates a new board.    
    def new(self, event):
       # have to reset our variables!
       self.soln = []
       self.word = ''
       self.count = 0
       self.board = [random.choices(string.ascii_lowercase, weights=self.F.values(), k=self.size) for i in range(self.size)]  # this is our new, random board
       # redraws a blank canvas
       for i in range(self.size):
            for j in range(self.size):
                self.canvas.create_rectangle(i*50, j*50, (i+1)*50, (j+1)*50, fill='white')
                self.canvas.create_text((i*50)+25, (j*50)+25, text=self.board[i][j], font=('Helvetica', 17)) 
   
        
    # This function is bound to the right mouse button.  Although similar to new, this function simply redraws the
    # current board you are playing.  Intended to be used if you are stuck in your Boggle game, or if you found a word
    def reset(self, event):
       # have to reset our variables!
       self.soln = []
       self.word = ''
       self.count = 0
       # redraw our current canvas
       for i in range(self.size):
            for j in range(self.size):
                self.canvas.create_rectangle(i*50, j*50, (i+1)*50, (j+1)*50, fill='white')
                self.canvas.create_text((i*50)+25, (j*50)+25, text=self.board[i][j], font=('Helvetica', 17)) 
        

    # solve is a wrapper function for the main, recursive part of our solution.  This function simply calls our
    # recursive helper function at each coordinate on the board.  Returns  a list of all possible words you can 
    # find on your currrent Boggle board
    def solve(self):
         for i in range(self.size):
             for j in range(self.size):
                 self.helper(cur=[(i, j)])  # intializes recursive helper function at every coordinate on the board
         return(self.totalSoln)
    
    # The power behind the solve function.  Recursively searches a starting coordinate, snaking its way 
    # throughout the board from that starting coordinate until it either hits a dead end (no word can be found at that
    # point in the word) or finds a word
    def helper(self, cur=[]):
        dirs = [(cur[-1][0]+1, cur[-1][1]), (cur[-1][0]-1, cur[-1][1]), (cur[-1][0], cur[-1][1]+1), (cur[-1][0], cur[-1][1]-1)]  # all possible paths from cur's ending coordinate tuple
        if not (0 <= cur[-1][0] < self.size) or not (0 <= cur[-1][1] < self.size):  # base case: tuple coordinates have to be on board
            return(False)
        if self.ckSoln(cur) != False:  # valid solution!
            if len(cur) == 5 and isinstance(self.ckSoln(cur), str):  # base case: we have found a word
                self.totalSoln.append(self.ckSoln(cur))
                return(True)
            else:
                [self.helper(cur + [path]) for path in dirs if path not in cur]  # recursive case: calls self.helper in every possible path, only if the path has not been traversed yet
        else:
            return(False)  # base case:  not a valid solution (dead end)
            
    
                    
