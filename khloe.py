import numpy
import random 
import math

"""
  1 2 3 4
A _ _ _ _
B _ _ _ _
C _ _ _ _
D _ _ _ _
In order to have 3 lines, you NEED to have
One, and only one, row
One, and only one, column
One, and only one, diagonal


OUTEROUTER:
Outer row, outer column. 
  1 2 3 4
A X X X X
B X _ _ _
C X _ _ _
D X _ _ _
This can only accept ONE diagonal (the one that completes the triangle)
  1 2 3 4
A X X X X
B X _ X _
C X X _ _
D X _ _ _ 
Four such triangles. Proof left as exercise to reader.

INNERINNER:
Inner row, Inner column. 
  1 2 3 4
A _ X _ _
B X X X X
C _ X _ _
D _ X _ _
This can also only accept ONE diagonal (the one that completes the triangle)
  1 2 3 4
A _ X _ X
B X X X X
C _ X _ _
D X X _ _
Four such triangles. Proof left as exercise to reader.

InnerOuter:
Inner row, Outer column (or vice versa)
  1 2 3 4
A X X X X
B _ X _ _
C _ X _ _
D _ X _ _
This can actually accept both diagonals
  1 2 3 4      1 2 3 4
A X X X X    A X X X X
B _ X X _    B _ X _ _    
C _ X _ _    C _ X X _    
D X X _ _    D _ X _ X    
This one has sixteen such solutions.
RowA can be matched with Col2, Col3. Each of these can be matched with PositiveDiag, NegativeDiag.
So four solutions with RowA.
Likewise four different solutions with RowD.

Same logic derives eight additional solutions for having outer column + inner row.

"""


"""
Grid is represented as 16bit binary where 0000111100010011b is matrix
0000
1111
0001
0011
and vice versa.

We can construct binary from the grid by going through each element of the grid and:
1. add the element to the binary
2. bitshift left 1

Likewise we construct grid from binary by going digit-by-digit from end to start. So for
0101, we'd:
1. add the last digit to current matrix slot (just check for even parity)
2. bitshift right 1
"""

zero = 0b0000000000000000
ones = 0b1111111111111111
rowA, rowB, rowC, rowD = 0b1111000000000000, 0b0000111100000000, 0b0000000011110000, 0b0000000000001111
col1, col2, col3, col4 = 0b1000100010001000, 0b0100010001000100, 0b0010001000100010, 0b0001000100010001
posDiag = 0b0001001001001000
negDiag = 0b1000010000100001

def gridToBinary(grid):
	binOutput=0
	for row in grid:
		for j in row:			
			binOutput<<=1
			binOutput+=j
	return binOutput

def binaryToGrid(binInput):
	grid = [[0 for i in range(4)] for i in range(4)]
	for i in reversed(range(16)):
		grid[i//4][i%4] = binInput%2
		binInput >>= 1
	return numpy.array(grid)


#n should be grid as a binary num
def isValidSolution(n):	
	has9Stickers = bin(n).count('1')==9
	# to check if a matrix contains a row [1, 1, 1, 1], we just ANDWISE with the value for that row.
	# the result will equal the mask if and only if the matrix contains that row

	hasRow = (n&rowA==rowA) or (n&rowB==rowB) or (n&rowC==rowC) or (n&rowD==rowD)
	hasCol = (n&col1==col1) or (n&col2==col2) or (n&col3==col3) or (n&col4==col4)
	hasDiag = (n&negDiag==negDiag) or (n&posDiag==posDiag)
	
	return has9Stickers and hasRow and hasCol and hasDiag



# as shown in comment, outer/outer has four solutions: 
# (rowA, col1, posDiag), (rowD, col4, posDiag), (rowA, col4, negDiag), (rowD, col1, negDiag)
outerOuterSolutions = [rowA|col1|posDiag, rowD|col4|posDiag, rowA|col4|negDiag, rowD|col1|negDiag]


# inner/inner also has four solutions:
# (rowB, col2, posDiag), (rowC, col3, posDiag), (rowB, col3, negDiag), (rowC, col2, negDiag)
innerInnerSolutions = [rowB|col2|posDiag, rowC|col3|posDiag, rowB|col3|negDiag, rowC|col2|negDiag]


# and outer/inner has sixteen solutions (each outer can match both inners and both diags):
#{{rowA x {col2, col3} x {negDiag, posDiag}, 
# {rowD x {col2, col3} x {negDiag, posDiag},
# {col1 x {rowB, rowC} x {negDiag, posDiag}, 
# {col4 x {rowB, rowC} x {negDiag, posDiag}}
innerOuterSolutions = []
for row in [rowA, rowD]:
	for col in [col2, col3]:
		for diag in [negDiag, posDiag]:
			innerOuterSolutions.append(row|col|diag)
for col in [col1, col4]:
	for row in [rowB, rowC]:
		for diag in [negDiag, posDiag]:
			innerOuterSolutions.append(row|col|diag)

allSolutions = outerOuterSolutions + innerInnerSolutions + innerOuterSolutions

"""
We want to find the set of all 7-sticker solutions that can turn into a valid 3-row 9-sticker grid.
We can brute force all numbers from 0-65535. If a 7-sticker solution x can turn into a valid 9-sticker y, then x & y = x.

There are (9 choose 2)=36 ways to create 7-stickers from each solution. Since we have 24 solutions, this gives us 864 potential 7-stickers. But it may be that multiple 9-stickers can turn into the same 7-sticker. I'll keep a dictionary for each 7-sticker mapping to the corresponding 9-sticker to track this. 
"""

# find all 7-stickers
stickers7 = []
for i in range(65536):
	if bin(i).count('1')==7:
		stickers7.append(i)

mapping7to9 = {}
for i in stickers7:
	for sol in allSolutions:
		if i & sol == i:
			curMappings = mapping7to9.get(i,[])
			curMappings.append(sol)
			mapping7to9[i]=curMappings

singleMapSolutions = []
doubleMapSolutions = []
tripleMapSolutions = []
beyondSolutions = []
for key in mapping7to9:
	if len(mapping7to9[key]) == 1:
		singleMapSolutions.append(key)
	elif len(mapping7to9[key]) == 2:
		doubleMapSolutions.append(key)	
	elif len(mapping7to9[key]) == 3:
		tripleMapSolutions.append(key)
	else:
		beyondSolutions.append(key)

print('Number of singly mapped 7-stars: ' + str(len(singleMapSolutions)))
print('Number of doubly mapped 7-stars: ' + str(len(doubleMapSolutions)))
print('Number of triply mapped 7-stars: ' + str(len(tripleMapSolutions)))
print('Number of quadruple+ mapped 7-stars: ' + str(len(beyondSolutions))+'\n')

#[print(binaryToGrid(x)) for x in singleMapSolutions]
#[print(binaryToGrid(x)) for x in doubleMapSolutions]
#[print(binaryToGrid(x)) for x in tripleMapSolutions]

"""
16 choose 7 = 11440 ways to fill out 7 stickers.
total 824 7-sticker boards which can lead to a 3-line. So 824/11440=0.07202797202 probability of getting a good 7-sticker.
Chances of hitting valid 7-sticker within x rerolls is inverse of NOT hitting after x rolls which is:
1 - (1-0.07202797202)^x
1 reroll: 0.07202797202
2 reroll: 0.13886791528
3 reroll: 0.20089351299
5 reroll: 0.31186376493
6 reroll: 0.36142882241
7 reroll: 0.40742380933
8 reroll: 0.45010587061
9 reroll: 0.48971362957
10 reroll: 0.52646852198

Rolling 9 times every week would give you a chance of (1-0.07202797202)^9 = 0.51028637042 of NOT hitting a valid 7-sticker
10+ times makes your odds better than 1 in 2.


From a 7-sticker, there are 9 choose 2 = 36 ways of filling out the remaining two stickers.
For single-mapped solutions, there is only one outcome out of those 36 ways which allows you to hit 3-line.
For double-mapped, there are two.
For triple-mapped, there are three.
So the chance of moving on is: (chance that 7-sticker is single-mapped * 1/36) + (chance that 7-sticker is double-mapped * 2/36) + (chance that 7-sticker is triple-mapped * 3/36)
= (800/824 * 1/36) + (8/824 * 2/36) + (6/824 * 3/36) = 0.02811488673 = 2.8%
"""

def runSim(numRerolls, numSimulations):
	print("Running simulation with {a} rerolls per week over {b} weeks.".format(a=numRerolls, b=numSimulations))
	numSingleMaps=0
	numSingleMapsSuccess=0
	numDoubleMaps=0
	numDoubleMapsSuccess=0
	numTripleMaps=0
	numTripleMapsSuccess=0
	emptyStickers=[0, 1, 2, 3, 4, 5, 6, 7, 8]
	for sim in range(numSimulations):
		for i in range(numRerolls):
			board = random.choice(stickers7)
			if board in singleMapSolutions:				
				numSingleMaps += 1
				break
			elif board in doubleMapSolutions:
				numDoubleMaps += 1
				break
			elif board in tripleMapSolutions:
				numTripleMaps += 1
				break

		# consider some 7-board 0b0000111100111000. 
		# get set of all 0s (empty stickers). We can just bitwise check. 
		# For example if 0b0000111100111000 & 4 is 0, this means the 3rd digit from right is 0 and we add to list of 0s.
		# then we sample two and add to the original board
		zeroSet = []
		bitwiseChecker = 1
		for i in range(16):
			if board & bitwiseChecker != bitwiseChecker:
				zeroSet.append(bitwiseChecker)
			bitwiseChecker <<= 1

		new9Board = board + sum(random.sample(zeroSet, 2))

		if isValidSolution(new9Board):

			if board in singleMapSolutions:				
				numSingleMapsSuccess += 1
			elif board in doubleMapSolutions:
				numDoubleMapsSuccess += 1
			elif board in tripleMapSolutions:
				numTripleMapsSuccess += 1
	print("3-line was hit {a} times!!!!".format(a=numSingleMapsSuccess+numDoubleMapsSuccess+numTripleMapsSuccess))
	print("Average {a} weeks per 3-line.\n".format(a=numSimulations/(numSingleMapsSuccess+numDoubleMapsSuccess+numTripleMapsSuccess)))

	if False:
		print("Valid single map hit {a} times, led to {b} 3-lines.".format(a=numSingleMaps,b=numSingleMapsSuccess))	
		print("Valid double map hit {a} times, led to {b} 3-lines.".format(a=numDoubleMaps,b=numDoubleMapsSuccess))	
		print("Valid triple map hit {a} times, led to {b} 3-lines.".format(a=numTripleMaps,b=numTripleMapsSuccess))

		numValid7Boards = numSingleMaps+numDoubleMaps+numTripleMaps
		print("Valid 7board rate: {a} vs. Theoretical: {b}".format(a=numValid7Boards/numSimulations, b = (1-math.pow(1-0.07202797202,numRerolls))))
		if numSingleMaps > 0:
			print("SingleMap to success rate: {a} vs. Theoretical: {b}".format(a=numSingleMapsSuccess/numSingleMaps, b = 1/36))
		if numDoubleMaps > 0:
			print("DoubleMap to success rate: {a} vs. Theoretical: {b}".format(a=numDoubleMapsSuccess/numDoubleMaps, b = 2/36))
		if numTripleMaps > 0:
			print("TripleMap to success rate: {a} vs. Theoretical: {b}".format(a=numTripleMapsSuccess/numTripleMaps, b = 3/36))


for i in range(4, 10):
	runSim(i, 30000)

# functions for external use
def printSinglyMapped():
	print(singleMapSolutions)
def printDoublyMapped():
	print(doubleMapSolutions)
def printTriplyMapped():
	print(tripleMapSolutions)


def sanityChecks():
	if False: #TestConversions
		gridBinary = 0b0000111100111100
		convertedGrid = binaryToGrid(gridBinary)
		reconvertedBinary = gridToBinary(convertedGrid)
		print(gridBinary)
		print(convertedGrid)
		print(reconvertedBinary)


	if False: #test solution set
		for sol in allSolutions:
			print(binaryToGrid(sol))

	#UNIT TESTS. ALWAYS KEEP ON.

	#test validity checker
	for sol in allSolutions:
		assert isValidSolution(sol)

	#test that our 24 solutions comprise ALL KNOWN SOLUTIONS.
	for i in range(65536):
		if isValidSolution(i):
			assert i in allSolutions

sanityChecks()