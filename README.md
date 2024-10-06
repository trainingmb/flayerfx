# flayerfx

flayerfx is a small personal project designed to scrape product prices from various stores and store them in a database. This project aims to provide a simple and efficient way to track price changes over time.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

To get started with flayerfx, follow these steps:

1. Clone the repository:
	```bash
	git clone https://github.com/yourusername/flayerfx.git
	```

2. Navigate to the project directory:
	```bash
	cd flayerfx
	```

3. Install the required dependencies:
	```bash
	pip install -r requirements.txt
	```

## Usage

To run the scraper and store the data in the database, use the following command:
python run.py


## Project Structure
The project is organized as follows:

- [`api`](./api): Contains the logic for scraping prices and storing them in the database.
- [`app`](./app): The visual entry point of the app, including the user interface and related components.
- [`logging`](./logging): Handles application logging, ensuring that all events are recorded for debugging and monitoring purposes.
- [`models`](./models): Defines the database models for the project, including the schema and relationships between different entities.
- [`flask_app.py`](./flask_app.py): The main entry point for running the Flask application, initializing the server and routing requests.
- [`requirements.txt`](./requirements.txt): Lists the dependencies required for the project, ensuring that all necessary packages are installed.
- [`README.md`](./README.md): This file, providing an overview of the project and instructions for setup and usage.

## Contributing
Contributions are welcome! If you have any suggestions or improvements, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License. See the [`License`]LICENSE file for details.

Feel free to customize the content as per your project's specifics.