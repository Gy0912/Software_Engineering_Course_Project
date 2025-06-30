1. Setup the Environment 
python 3.10+
pip install pyzmq

2. Code Structure
/YourCodeExample/NetClient.py - This file is responsible for communicating with the server in the test cases.
/YourCodeExample/main.py - This file contains a sample student code, which you can modify to be the main file of your own designed system.
/TestCase/main.py - This file is responsible for sending test cases to your system and will interact based on the data sent by your system, including a very simple test case.
/TestCase/Server.py - This file is responsible for communicating with the client in the student code.

3.How to Run the Code
First, run /TestCase/main.py in Terminal to setup the judger.
Then, run /YourCodeExample/main.py in ANOTHER Terminal.
Finally, input 'y' to run the naive testcase.


4.available operation/event
//available user operation
Set the format of the chessboard：set@format 
	// E.g. set@9#82#112611530753044 means Set the chessboard to the following format
	[9, '#', 8, 2]
	['#', 1, 1, 2]
	[6 , 1 , 1, 5]
	[3 , 0 , 7, 5]
	[3 , 0 , 4, 4]

piece movement: move@name#direction
	// E.g. move@Zu4#Down means moving the Zu4 piece down one square

undo: undo Roll back the previous step

Each time the client receives an instruction, it returns the format of the chessboard and then a description of the completed operation (E.g."Initialization complete!" , "Valid move!").
See answer.txt and testcase.txt for details.




