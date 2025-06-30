# Software Engineering Projects Summary

## Overview

This repository contains three course projects developed during a Software Engineering curriculum:

- **Smart Vending Machine**  
  A finalized and fully-tested project, including real-time UI, API integration, and comprehensive testing.

- **Elevator System**  
  A finalized and fully-tested project, including real-time UI, API integration, and comprehensive testing. This may be not the final release since I am not the main developer.

- **Sliding Puzzle (Huarongdao)**  
  An in-progress project. I did not contribute to this part directly. Execution and maintenance details are not available in this repository.

This repository is provided for academic learning and review only. **Plagiarism or copying without permission is strictly prohibited.**  
If you require the latest version or intend to reuse this project in any way, please contact me directly.

---

## Project Status

| Project             | Status       | Notes                                                                 |
|---------------------|--------------|-----------------------------------------------------------------------|
| Smart Vending Machine | Final Version | Complete development, API support, model verification, all tests and documentation included |
| Elevator System       | Final Version?  | Complete development, API support, model verification, all tests and documentation included  |
| Sliding Puzzle        | Unverified   | Not developed by me. Please reach out for support if needed            |

---

## Responsibilities

I was responsible for the following parts of the course projects:

- Complete code development of the **Smart Vending Machine**, including frontend, backend, and API bridging
- Designing and writing all **unit tests**, **integration tests**, and **API testing scripts**
- Requirement analysis and UML modeling for the **Elevator System**
- Building UPPAAL models for verifying the correctness of the elevator scheduling logic

If you have questions related to the above responsibilities, feel free to contact me.

---

## How to Run

To run the projects:

- For the **Smart Vending Machine**, navigate to the `code/system` directory inside the `vending_machine` subfolder and run the main application file `run.py`.
- To run test scripts, go to the `code/testing` directory and execute any file that contains "test" in the name, except `API_test`.
- For **API testing**, prepare your input test cases in the `TestCase/testcase/` folder and expected outputs in the `TestCase/answer/` folder. Then run the main script in `TestCase/` and the `API_test` file from the parent testing directory (execution order does not matter).
- For the **Elevator Project**, open the `elevator_UI.py` file in the `code/system` directory and uncomment the final main function call to start the program.
- The **Sliding Puzzle** project is not maintained by me. Please contact me if you need assistance running it.

---

## Development Notes

Only the vending machine project represents the finalized version with full features.  
The other two (Elevator and Sliding Puzzle) are intermediate or incomplete versions.

The source code is organized under:

- `code/system` for project logic and UI
- `code/testing` for unit, integration, and API tests
- `document/validation.pdf` for environment and library dependencies

---

## Compatibility & Usage

- Python 3.10+ is required for full compatibility
- Required libraries are listed in `document/validation.pdf`

---

## Disclaimer

This project is published for academic reference and learning purposes only.  
Do **not** reuse or submit any part of this work for academic credit without explicit permission.  
Violation may be treated as plagiarism.

