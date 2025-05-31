from competition_table import CompetitionTableCSV, CompetitionTablePickle, demo_task
from text_analyzer import TextAnalyzer, create_sample_file
from sin_calc import SinSeriesAnalyzer
from geometry import Rhombus
from numpy_analysis import NumpyAnalyzer    


class App:
    def __init__(self):
        pass

    def run_task1(self):
        # Competition Table task
        sample_data = {
            "Team Alpha": 40,
            "Team Beta": 38,
            "Team Gamma": 45
        }

        print("\n--- Task 1: Competition Table ---")
        print("Select serialization format:")
        print("1. CSV")
        print("2. Pickle")

        choice = self.safe_input("Enter 1 or 2: ", lambda x: x in ('1', '2'), "Please enter '1' or '2'.")

        if choice == '1':
            table = CompetitionTableCSV(sample_data)
            filename = "teams.csv"
            format_name = "CSV"
        else:
            table = CompetitionTablePickle(sample_data)
            filename = "teams.pkl"
            format_name = "Pickle"

        demo_task(table, filename, format_name)

    def run_task2(self):
        # Text Analysis task
        print("\n--- Task 2: Text Analysis ---")
        source = "input_text.txt"
        result = "analysis_result.txt"
        archive = "result_archive.zip"

        create_sample_file(source)

        analyzer = TextAnalyzer(source, result, archive)
        analyzer.read_text()

        output = analyzer.analyze()
        print("\nText Analysis Results:\n")
        print(output)

        analyzer.save_results(output)
        analyzer.archive_results()

    def run_task3(self):
        # Sin series task
        print("\n--- Task 3: Sin Series Analysis ---")
        analyzer = SinSeriesAnalyzer(-3.1416, 3.1416, 0.1, max_terms=20, eps=1e-8)
        analyzer.analyze()
        analyzer.print_table()
        analyzer.compute_statistics()
        analyzer.plot()

    def input_positive_float(self, prompt):
        while True:
            val = input(prompt)
            try:
                fval = float(val)
                if fval > 0:
                    return fval
                else:
                    print("Value must be positive.")
            except ValueError:
                print("Invalid number, try again.")

    def input_angle(self, prompt):
        while True:
            val = input(prompt)
            try:
                fval = float(val)
                if 0 < fval < 180:
                    return fval
                else:
                    print("Angle must be between 0 and 180 degrees.")
            except ValueError:
                print("Invalid number, try again.")

    def run_task4(self):
        print("\n--- Task 4: Geometry - Rhombus ---")
        while True:
            a = self.input_positive_float("Enter side length a (>0): ")
            R = self.input_angle("Enter acute angle R in degrees (0 < R < 180): ")
            color = input("Enter color name (e.g. blue, red): ").strip()
            label = input("Enter text label to put on the figure: ")

            rhombus = Rhombus(a, R, color)
            print("\n" + rhombus.parameters_str())
            rhombus.plot(label)

            again = self.safe_input("Run Task 4 again? (y/n): ", lambda x: x.lower() in ['y', 'n'], "Please enter 'y' or 'n'.")
            if again.lower() == 'n':
                break

    def run_task5(self):
        print("\n--- Task 5: NumPy Array Analysis ---")
        n = int(input("Enter number of rows (n): "))
        m = int(input("Enter number of columns (m): "))

        analyzer = NumpyAnalyzer(n, m)
        analyzer.demonstrate_array_creation()
        analyzer.demonstrate_indexing()
        analyzer.universal_functions()
        analyzer.statistics()
        analyzer.correlation()

        sum_abs, neg_odd_vals = analyzer.sum_mod_neg_odd()
        analyzer.std_dev_two_ways(neg_odd_vals)

    @staticmethod
    def safe_input(prompt, valid_func=None, error_msg="Invalid input. Please try again."):
        while True:
            value = input(prompt).strip()
            if valid_func is None or valid_func(value):
                return value
            print(error_msg)

    def run(self):
        # Раскомментируй нужные задачи:
        # self.run_task1()
         self.run_task2()
        # self.run_task3()
        # self.run_task4()
        # self.run_task5()

if __name__ == "__main__":
    app = App()
    app.run()
