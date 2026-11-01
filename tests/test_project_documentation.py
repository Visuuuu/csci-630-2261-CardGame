import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
README = PROJECT_ROOT / "README.md"
ARCHITECTURE = PROJECT_ROOT / "docs" / "ARCHITECTURE.md"
EXPERIMENTS = PROJECT_ROOT / "docs" / "EXPERIMENTS.md"


class TestProjectDocumentation(unittest.TestCase):
    def test_all_documentation_files_exist(self):
        for path in (README, ARCHITECTURE, EXPERIMENTS):
            with self.subTest(path=path):
                self.assertTrue(path.is_file())

    def test_readme_names_primary_strategies(self):
        text = README.read_text(encoding="utf-8")
        for strategy in (
            "Random",
            "Greedy",
            "Heuristic",
            "Monte Carlo",
        ):
            with self.subTest(strategy=strategy):
                self.assertIn(strategy, text)

    def test_readme_documents_gui_command(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn(
            "python -m interface.uno_gui",
            text,
        )

    def test_readme_documents_test_command(self):
        text = README.read_text(encoding="utf-8")
        self.assertIn(
            "python -m unittest discover",
            text,
        )

    def test_architecture_documents_hidden_information(self):
        text = ARCHITECTURE.read_text(
            encoding="utf-8"
        )
        self.assertIn("AgentObservation", text)
        self.assertIn("opponent", text.lower())
        self.assertIn("Monte Carlo V2", text)

    def test_architecture_documents_both_rulesets(self):
        text = ARCHITECTURE.read_text(
            encoding="utf-8"
        ).lower()
        self.assertIn("104 cards", text)
        self.assertIn("108 cards", text)
        self.assertIn("wild draw four", text)

    def test_experiments_document_all_studies(self):
        text = EXPERIMENTS.read_text(
            encoding="utf-8"
        )
        for phrase in (
            "Four-Agent Tournament",
            "Ruleset Validation",
            "Simulation Budget Study",
            "Monte Carlo V1 vs. V2",
            "Statistical Interpretation",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_documented_experiment_modules_exist(self):
        modules = (
            "run_validation.py",
            "monte_carlo_budget.py",
            "compare_monte_carlo_versions.py",
            "final_analysis.py",
            "system_check.py",
        )
        for filename in modules:
            with self.subTest(filename=filename):
                self.assertTrue(
                    (
                        PROJECT_ROOT
                        / "experiments"
                        / filename
                    ).is_file()
                )


if __name__ == "__main__":
    unittest.main()
