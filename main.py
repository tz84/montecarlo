import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

class BettingStrategy:
    def __init__(self, initial_bankroll, initial_bet, rounds_per_game):
        self.initial_bankroll = initial_bankroll
        self.initial_bet = initial_bet
        self.rounds_per_game = rounds_per_game
        self.bankroll_progressions = LinkedList()

    def run_game(self):
        self._run_game_recursive(self.initial_bankroll, self.initial_bet, 0)

    def _run_game_recursive(self, bankroll, bet, current_round):
        if bankroll <= 0 or current_round >= self.rounds_per_game:
            self.bankroll_progressions.append(bankroll)
            return
        win = self.simulate_bet()
        if win:
            bankroll += bet
            bet = self.initial_bet
        else:
            bankroll -= bet
            bet = min(bet * 2, bankroll)
        self._run_game_recursive(bankroll, bet, current_round + 1)

    def simulate_bet(self):
        return np.random.choice([True, False], p=[18/37, 19/37])

    def run_simulation(self, number_of_games):
        for _ in range(number_of_games):
            self.run_game()
        # convert linked list to list
        return self.bankroll_progressions.to_list()
class MartingaleSimulation(BettingStrategy):
    def run_game(self):
        bankroll = self.initial_bankroll
        bet = self.initial_bet
        bankroll_progression = [bankroll]

        for _ in range(self.rounds_per_game):
            if bankroll <= 0:
                break

            win = self.simulate_bet()  # simulate_bet method from BettingStrategy
            if win:
                bankroll += bet
                bet = self.initial_bet  # reset bet to initial value after win
            else:
                bankroll -= bet
                bet = min(bet * 2, bankroll)  # double  bet after loss, cant exceed bankroll

            bankroll_progression.append(bankroll)

        self.bankroll_progressions.append(bankroll_progression)
class OscarsGrindSimulation(BettingStrategy):
    def run_game(self):
        bankroll = self.initial_bankroll
        bet = self.initial_bet
        bankroll_progression = [bankroll]
        session_profit = 0  # track profit for the current session
        target_profit = 3  # target unit profit for each cycle

        for _ in range(self.rounds_per_game):
            if bankroll <= 0:
                break

            win = self.simulate_bet()  # simulate_bet method from BettingStrategy
            if win:
                bankroll += bet
                session_profit += bet
                if session_profit < target_profit:
                    bet = min(bet + 1, bankroll)  # increase bet by one unit if profit does not = one unit
                else:
                    session_profit = 0  # reset session profit if target is reached or exceeded
                    bet = self.initial_bet  # reset bet to initial value
            else:
                bankroll -= bet
                session_profit -= bet
                # bet remains same after loss

            bankroll_progression.append(bankroll)

            # reset the cycle if profit target is reached or exceeded
            if session_profit >= target_profit:
                session_profit = 0  # reset session profit for a new cycle
                bet = self.initial_bet  # reset bet to initial value for the new cycle

        self.bankroll_progressions.append(bankroll_progression)

class ParoliSimulation(BettingStrategy):
    def run_game(self):
        bankroll = self.initial_bankroll
        bet = self.initial_bet
        bankroll_progression = [bankroll]
        consecutive_wins = 0  # tracker for consecutive wins

        for _ in range(self.rounds_per_game):
            if bankroll <= 0:
                break

            win = self.simulate_bet()  # simulate_bet method from BettingStrategy
            if win:
                bankroll += bet
                consecutive_wins += 1
                if consecutive_wins < 3:  # double bet after a win (if less than 3 consecutive wins)
                    bet = min(bet * 2, bankroll)
                else:  # reset bet after 3 consecutive wins
                    bet = self.initial_bet
                    consecutive_wins = 0  # reset consecutive wins
            else:
                bankroll -= bet
                bet = self.initial_bet  # reset bet to initial value after a loss
                consecutive_wins = 0  # reset consecutive wins

            bankroll_progression.append(bankroll)

        self.bankroll_progressions.append(bankroll_progression)

class FibonacciSimulation(BettingStrategy):
    def run_game(self):
        bankroll = self.initial_bankroll
        bet_index = 0  # start at the beginning of fibonacci sequence
        fib_sequence = [1, 1]  # initial fibonacci sequence (generated dynamically as needed)
        bankroll_progression = [bankroll]

        for _ in range(self.rounds_per_game):
            if bankroll <= 0 or bet_index < 0:
                break

            bet = fib_sequence[bet_index]
            win = self.simulate_bet()
            if win:
                bankroll += bet
                bet_index = max(0, bet_index - 2)  # move back two places in the sequence
            else:
                bankroll -= bet
                bet_index += 1  # move to next number in the sequence
                if bet_index >= len(fib_sequence):  # extend fibonacci sequence if necessary (if bet needs it)
                    fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])

            bankroll_progression.append(bankroll)

        self.bankroll_progressions.append(bankroll_progression)
class DAlembertSimulation(BettingStrategy):
    def run_game(self):
        bankroll = self.initial_bankroll
        current_bet = self.initial_bet 
        bankroll_progression = [bankroll]
        unit_value = 10  # 1 unit = 10

        for _ in range(self.rounds_per_game):
            if bankroll <= 0:
                break

            win = self.simulate_bet()
            if win:
                bankroll += current_bet
                # make sure bet does not go below the initial bet amount
                current_bet = max(self.initial_bet, current_bet - unit_value)
            else:
                bankroll -= current_bet
                # increase bet by the unit value (cant exceed bankroll)
                if (current_bet + unit_value) <= bankroll:
                    current_bet += unit_value
                else:
                    current_bet = bankroll

            bankroll_progression.append(bankroll)

        self.bankroll_progressions.append(bankroll_progression)
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None  #track last node

    def append(self, data):
        new_node = Node(data)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def to_list(self):
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result

class RouletteSimulationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('MonteCarlo Roulette Simulation')
        
        # launch into full-screen mode for any device 
        self.attributes('-fullscreen', True)

        self.start_page()

    def start_page(self):
        self.title_label = ttk.Label(self, text="MonteCarlo Roulette Simulation", font=("Arial", 20))
        self.title_label.pack(pady=20)

        self.strategy_label = ttk.Label(self, text="Select Betting Strategy:")
        self.strategy_label.pack()

        strategy_options = ["Martingale", "Oscar's Grind", "Paroli", "Fibonacci", "D'Alembert"]
        self.selected_strategy = tk.StringVar()
        strategy_dropdown = ttk.Combobox(self, textvariable=self.selected_strategy, values=strategy_options)
        strategy_dropdown.pack()

        self.n_label = ttk.Label(self, text="Number of Bets (n):")
        self.n_label.pack()

        self.n_entry = ttk.Entry(self)
        self.n_entry.pack()
        
        self.n_info_label = ttk.Label(self, text="Enter number between 10-1000, default is 100")
        self.n_info_label.pack()

        self.games_label = ttk.Label(self, text="Number of Games:")
        self.games_label.pack()

        self.games_entry = ttk.Entry(self)
        self.games_entry.pack()

        self.games_info_label = ttk.Label(self, text="Enter number between 10-50, default is 25")
        self.games_info_label.pack()

        self.info_button = ttk.Button(self, text='Info', command=self.launch_info_page)
        self.info_button.pack(pady=(5, 10)) 

        self.start_button = ttk.Button(self, text='Start Simulation', command=self.run_montecarlo)
        self.start_button.pack(expand=True)

    def launch_info_page(self):
        class SinglePageHandler(SimpleHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(INFO_HTML.encode('utf-8'))

        # starting the server in a new thread to avoid blocking
        def start_server():
            with TCPServer(("127.0.0.1", 0), SinglePageHandler) as httpd:
                # port assigned by the OS or open web browser directly
                port = httpd.server_address[1]
                print(f"Server started at http://127.0.0.1:{port}")
                webbrowser.open(f'http://127.0.0.1:{port}')
                httpd.serve_forever()

        # initiate the thread to run the server
        threading.Thread(target=start_server, daemon=True).start()

    def run_montecarlo(self):
        self.start_button.pack_forget()
        self.loading_label = ttk.Label(self, text='Simulation running, please wait...')
        self.loading_label.pack(expand=True)

        # validate number of games from user input 
        try:
            number_of_games = int(self.games_entry.get())
            if number_of_games < 10 or number_of_games > 50:
                number_of_games = 25
        except ValueError:
            number_of_games = 25

        # validate rounds per game from user input 
        try:
            rounds_per_game = int(self.n_entry.get())
            if not 10 <= rounds_per_game <= 1000:
                rounds_per_game = 100
        except ValueError:
            rounds_per_game = 100

        # pass rounds_per_game to the simulation thread
        self.simulation_thread = threading.Thread(target=self.montecarlo_simulation, args=(number_of_games, rounds_per_game), daemon=True)
        self.simulation_thread.start()

        selected_strategy = self.selected_strategy.get()

        if selected_strategy == "Martingale":
            simulation = MartingaleSimulation(1000, 10, rounds_per_game)
        elif selected_strategy == "Oscar's Grind":
            simulation = OscarsGrindSimulation(1000, 10, rounds_per_game)
        elif selected_strategy == "Paroli":
            simulation = ParoliSimulation(1000, 10, rounds_per_game)
        elif selected_strategy == "Fibonacci":
            simulation = FibonacciSimulation(1000, 10, rounds_per_game)
        elif selected_strategy == "D'Alembert":
            simulation = DAlembertSimulation(1000, 10, rounds_per_game)
        else:
            simulation = MartingaleSimulation(1000, 10, rounds_per_game)

        self.simulation_thread = threading.Thread(target=self.montecarlo_simulation, args=(number_of_games,), daemon=True)
        self.simulation_thread.start()

    def montecarlo_simulation(self, number_of_games, rounds_per_game):
         # start simulation with rounds_per_game from user input (post validation)
        initial_bankroll = 1000
        initial_bet = 10
        selected_strategy = self.selected_strategy.get()

        # simulation based on the strategy
        if selected_strategy == "Martingale":
            simulation = MartingaleSimulation(initial_bankroll, initial_bet, rounds_per_game)
        elif selected_strategy == "Oscar's Grind":
            simulation = OscarsGrindSimulation(initial_bankroll, initial_bet, rounds_per_game)
        elif selected_strategy == "Paroli":
            simulation = ParoliSimulation(initial_bankroll, initial_bet, rounds_per_game)
        elif selected_strategy == "Fibonacci":
            simulation = FibonacciSimulation(initial_bankroll, initial_bet, rounds_per_game)
        elif selected_strategy == "D'Alembert":
            simulation = DAlembertSimulation(initial_bankroll, initial_bet, rounds_per_game)
        else:
            simulation = MartingaleSimulation(initial_bankroll, initial_bet, rounds_per_game)

        bankroll_progressions = simulation.run_simulation(number_of_games)
        self.visualize_outcomes(bankroll_progressions, selected_strategy, number_of_games)

    def visualize_outcomes(self, bankroll_progressions, selected_strategy, number_of_games):
        for widget in self.winfo_children():
            widget.pack_forget()

        graph_frame = ttk.Frame(self)
        graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(self)
        table_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

        fig, ax = plt.subplots()
        for progression in bankroll_progressions:
            ax.plot(progression, marker='o', markersize=3, alpha=0.6)

        ax.set_title('Bankroll vs Number of Bets')
        ax.set_xlabel('Number of Bets')
        ax.set_ylabel('Bankroll')

        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        final_bankrolls = [progression[-1] for progression in bankroll_progressions]
        busts = sum(bankroll <= 0 for bankroll in final_bankrolls)
        non_bust_bankrolls = [bankroll for bankroll in final_bankrolls if bankroll > 0]

        number_of_games = len(bankroll_progressions)
        initial_bankroll = 1000
        net_profits = [bankroll - initial_bankroll for bankroll in final_bankrolls]
        total_profit = sum(net_profits)

        stats_data = [
            ['Number of Games', number_of_games],  # use the passed variable from user input 
            ['Total Profit', round(total_profit, 3)],
            ['Busts', busts],
            ['Average Non-Bust Bankroll', round(np.mean(non_bust_bankrolls), 3) if non_bust_bankrolls else 0],
            ['Mean', round(np.mean(final_bankrolls), 3)],
            ['Median', round(np.median(final_bankrolls), 3)],
            ['Mode', round(pd.Series(final_bankrolls).mode()[0], 3)],
            ['Standard Deviation', round(np.std(final_bankrolls), 3)]
        ]   

        stats_df = pd.DataFrame(stats_data, columns=['Statistic', 'Value'])

        stats_text = tk.Text(table_frame, height=10, width=40)
        stats_text.insert(tk.END, stats_df.to_string(index=False))
        stats_text.config(state=tk.DISABLED)
        stats_text.pack(side=tk.TOP)

        ev_single_bet = calculate_expected_value(selected_strategy)

        ev_label = tk.Label(table_frame, text=f'Expected Value for a Single Bet: {ev_single_bet:.3f}')
        ev_label.pack(side=tk.TOP)

        self.restart_button = ttk.Button(self, text='Restart Game', command=self.refresh_simulation)
        self.restart_button.pack(expand=True, pady=20)

    def refresh_simulation(self):
        for widget in self.winfo_children():
            widget.pack_forget()
        self.start_page()

def calculate_expected_value(selected_strategy):
    p_win = 18/37
    p_loss = 19/37

    if selected_strategy == "Martingale":
        ev_single_bet = (p_win * 1) - (p_loss * 1)
    elif selected_strategy == "Oscar's Grind":
        ev_single_bet = (p_win * 1) - (p_loss * 1)  
    elif selected_strategy == "Paroli":
        ev_single_bet = (p_win * 1) - (p_loss * 1)  
    elif selected_strategy == "Fibonacci":
        ev_single_bet = (p_win * 1) - (p_loss * 1)  
    elif selected_strategy == "D'Alembert":
        ev_single_bet = (p_win * 1) - (p_loss * 1)  
    else:
        ev_single_bet = -0.027

    return ev_single_bet

INFO_HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Info</title>
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 20px;
        padding: 0;
        background-color: #f0f0f0;
    }

    h2 {
        color: #333;
    }

    p {
        font-size: 16px;
        color: #666;
    }

    .container {
        width: 80%;
        margin: auto;
        background: white;
        padding: 20px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
</style>
</head>
<body>

<div class="container">
    <h2>Martingale</h2>
    <p>The Martingale strategy involves doubling the bet after every loss, with the idea that a win will recover all previous losses plus win a profit equal to the original bet. The simulation starts with an initial bankroll and bet, doubling the bet on a loss and resetting it on a win.</p>

    <h2>Oscar's Grind</h2>
    <p>Oscar's Grind aims to make a profit of one unit per series of bets. After a win, if the profit is not yet one unit, the bet is increased by one unit. The simulation uses a counter for consecutive wins and adjusts the bet based on the outcome of each round, attempting to achieve a small, steady profit.</p>

    <h2>Paroli</h2>
    <p>The Paroli strategy is a positive progression betting system, which means increasing the bet after a win and starting with the initial bet after a loss. The aim is to capitalize on winning streaks while minimizing losses. The bet is doubled after a win, up to three consecutive wins, before resetting.</p>

    <h2>Fibonacci</h2>
    <p>This strategy uses the Fibonacci sequence to determine bet sizes. After a loss, the next bet is the next number in the Fibonacci sequence. After a win, the player moves back two places in the sequence. This allows for a more measured approach to increasing and decreasing bets based on the outcome of each round.</p>

    <h2>D'Alembert</h2>
    <p>The D'Alembert strategy involves increasing the bet by one unit after a loss and decreasing it by one unit after a win, under the assumption that wins and losses will eventually balance out. This is a more conservative approach compared to the Martingale system.</p>
</div>

</body>
</html>
"""

if __name__ == '__main__':
    app = RouletteSimulationApp()
    app.mainloop()
