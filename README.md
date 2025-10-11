# QuantSim-Toolkit

**A Python-based quantitative simulation and analysis toolkit that integrates probability simulations, stock return analysis, portfolio risk calculations, and Monte Carlo methods. Designed for aspiring Quant Developers to demonstrate applied mathematics, numerical simulations, and CLI-based financial utilities.**

---

## Overview

QuantSim-Toolkit consolidates multiple quantitative and programming concepts into a single, **modular CLI project**. It bridges math, Python, 
and finance by allowing users to:

- Simulate probabilities and random events
- Analyze stock returns and risk
- Perform Monte Carlo simulations for stock price paths
- Interact with a unified CLI interface

This project focuses on **Quant Development**, emphasizing **code structure, applied math, and system-level thinking**.

---

## Features / Modules

### 1. Probability Simulator
- Simulates dice rolls, coin tosses, and random events
- Estimates probabilities using Monte Carlo simulations
- Demonstrates applied probability concepts

### 2. Stock Return Analyzer
- Reads historical stock price CSVs
- Computes returns, mean, variance, and standard deviation
- Plots return distributions and moving averages for visualization

### 3. Portfolio Risk Calculator
- Computes portfolio variance using covariance matrices
- Estimates volatility and risk metrics
- Prepares for portfolio optimization tasks

### 4. Monte Carlo Stock Price Simulator
- Simulates stock price paths using Geometric Brownian Motion
- Calculates expected payoffs for hypothetical trading scenarios
- Demonstrates applied Monte Carlo simulations

### 5. CLI Interface
- Unified command-line interface using `argparse`
- Subcommands: `simulate`, `analyze`, `risk`
- Modular and easy-to-use workflow

---

Assumptions made: 
1. OS used - Debian (Ubuntu)
2. Dependency management - uv (it needs to be installed in your local)

To start working on the project, fork the repo and clone it in your local. Once the cloning is complete, you can easily reproduce the 
environment by running the following commands in order:

1. Navigate to the root directory of the project using 'cd' command from the terminal (root directory is the one where the Readme.md is stored)
2. To install all declared dependencies (including main and dev dependencies by default) into a virtual environment managed by uv, 
you can use the 'uv sync' command
3. Activate the virtual environment and start working using command: source .venv/bin/activate (.venv can also be .env or env)

---

Trying out the commands(all commands should be entered in the terminal from the src directory):

1. Enter the command: **python3 main.py simulation -tries 100** to test the probability of each side of the dice after 100 rolls. Replace 100 with any other integer number to change the number of rolls 

2. Enter command: **python3 main.py simulation -type coin -tries 100** to test the probability of each side of the coin after 100 tosses. Replace 100 with any other integer number to change the number of tosses 

![Single coin or dice after n tries](screenshots/single_coin_or_dice.png)
