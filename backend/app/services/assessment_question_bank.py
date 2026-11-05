"""Fixed MVP assessment bank; answer keys stay on the server."""

from typing import Any

from skill_catalog import SKILLS


def _question(
    skill_id: str,
    number: int,
    difficulty: str,
    text: str,
    options: tuple[str, str, str, str],
    correct: str,
) -> dict[str, Any]:
    return {
        "id": f"{skill_id}-{number:02d}",
        "skill_id": skill_id,
        "difficulty": difficulty,
        "text": text,
        "options": [
            {"id": chr(ord("a") + index), "text": option}
            for index, option in enumerate(options)
        ],
        "correct_option_id": correct,
    }


ASSESSMENT_QUESTIONS: tuple[dict[str, Any], ...] = (
    # Python
    _question("python", 1, "basic", "What values are produced by list(range(2, 9, 3))?", ("[2, 5, 8]", "[2, 5, 8, 11]", "[3, 6, 9]", "[2, 3, 4, 5, 6, 7, 8]"), "a"),
    _question("python", 2, "basic", "After `items = [1, 2]`, `alias = items`, and `alias.append(3)`, what is `len(items)`?", ("2", "3", "4", "It raises an error"), "b"),
    _question("python", 3, "basic", "What does `profile.get('city', 'Unknown')` return when `city` is not a key in `profile`?", ("None, always", "An error", "'Unknown'", "The first key in the dictionary"), "c"),
    _question("python", 4, "intermediate", "What is the safe way to use a list as a default when a function is called many times?", ("Use `items=[]` and clear it on each call", "Use `items=None`, then create a new list inside the function", "Use a global list", "Use a tuple and append to it"), "b"),
    _question("python", 5, "intermediate", "What exception does `int('3.5')` raise?", ("TypeError", "KeyError", "IndexError", "ValueError"), "d"),
    # Machine Learning
    _question("machine-learning", 1, "basic", "A model learns from examples that include the correct output labels. What kind of learning is this?", ("Supervised learning", "Unsupervised learning", "Reinforcement learning", "Random search"), "a"),
    _question("machine-learning", 2, "basic", "Why keep a test set separate from training data?", ("To make training faster by using fewer features", "To estimate performance on data the model did not train on", "To guarantee every prediction is correct", "To remove all noisy data"), "b"),
    _question("machine-learning", 3, "basic", "A model performs very well on its training examples but poorly on new examples. What is the likely issue?", ("Underfitting", "Normalization", "Overfitting", "Clustering"), "c"),
    _question("machine-learning", 4, "intermediate", "Which task is a classification problem?", ("Predicting tomorrow's temperature", "Estimating a house price", "Predicting a delivery time", "Assigning an email to spam or not spam"), "d"),
    _question("machine-learning", 5, "intermediate", "Which situation is data leakage?", ("Scaling training data using training-set statistics", "Including information only known after the outcome in model training", "Checking model quality on held-out data", "Removing duplicate training rows"), "b"),
    # Artificial Intelligence
    _question("artificial-intelligence", 1, "basic", "In an AI problem, what is a state space?", ("The set of possible situations the system can be in", "The computer's disk capacity", "A list of programming languages", "A table of model scores"), "a"),
    _question("artificial-intelligence", 2, "basic", "What is the purpose of a heuristic in a search algorithm?", ("To estimate which option may lead closer to a goal", "To store every explored state permanently", "To encrypt the search results", "To guarantee a perfect solution for every problem"), "a"),
    _question("artificial-intelligence", 3, "basic", "An intelligent agent typically observes its environment and then what?", ("Deletes its observations", "Chooses an action", "Stops receiving input", "Changes the environment's rules"), "b"),
    _question("artificial-intelligence", 4, "intermediate", "A rule-based system contains `IF temperature is high THEN turn on fan`. What is the rule's condition?", ("Turn on fan", "The fan", "Temperature is high", "The system output"), "c"),
    _question("artificial-intelligence", 5, "intermediate", "Which statement best describes the relationship between AI and machine learning?", ("They are unrelated fields", "Machine learning is a subset of AI that learns patterns from data", "AI is a subset of machine learning in every context", "Machine learning only means writing fixed rules"), "b"),
    # SQL & Databases
    _question("sql-databases", 1, "basic", "Which SQL clause filters individual rows before grouping?", ("ORDER BY", "HAVING", "WHERE", "SELECT"), "c"),
    _question("sql-databases", 2, "basic", "What does a LEFT JOIN preserve from the left table?", ("Only rows with a match in both tables", "Every left-table row, with matching right-side data when available", "Only rows without a match", "Only the first row"), "b"),
    _question("sql-databases", 3, "basic", "What is the main purpose of a primary key?", ("To uniquely identify each row", "To sort the table automatically", "To encrypt a column", "To allow duplicate row identifiers"), "a"),
    _question("sql-databases", 4, "intermediate", "How should application code safely include a user-provided value in a SQL query?", ("Concatenate it into the SQL string", "Remove spaces and concatenate it", "Use a parameterized query", "Put it in a SQL comment"), "c"),
    _question("sql-databases", 5, "intermediate", "What does a transaction rollback do?", ("Permanently applies pending changes", "Reverses uncommitted changes in the transaction", "Deletes the database schema", "Copies data to another table"), "b"),
    # Web Development
    _question("web-development", 1, "basic", "Which HTTP method is normally used to retrieve a resource without changing it?", ("GET", "POST", "PATCH", "DELETE"), "a"),
    _question("web-development", 2, "basic", "Which HTML element best represents the main content of a page?", ("`<div>` for every section", "`<main>`", "`<style>`", "`<meta>`"), "b"),
    _question("web-development", 3, "basic", "What does a CSS media query help a page do?", ("Store data in a database", "Send an HTTP request", "Apply styles based on viewport or device conditions", "Compile JavaScript"), "c"),
    _question("web-development", 4, "intermediate", "How can JavaScript respond when a user clicks a button?", ("Attach a click event listener", "Change the file extension", "Add a database primary key", "Use an HTML comment"), "a"),
    _question("web-development", 5, "intermediate", "In React, what normally happens after a component's state changes?", ("The component can render again with the new state", "The browser database is reset", "The state is sent automatically to PostgreSQL", "Every component is removed permanently"), "a"),
    # Problem Solving & Algorithms
    _question("problem-solving-algorithms", 1, "basic", "In the worst case, how many elements may a linear search inspect in a list of n items?", ("1", "log n", "n", "n squared"), "c"),
    _question("problem-solving-algorithms", 2, "basic", "What condition does binary search require to discard half the remaining items at each step?", ("The data is sorted", "The data contains only strings", "The list has an even length", "Every value is unique"), "a"),
    _question("problem-solving-algorithms", 3, "basic", "Which data structure follows last-in, first-out order?", ("Queue", "Stack", "Graph", "Hash table"), "b"),
    _question("problem-solving-algorithms", 4, "intermediate", "A simple algorithm has two nested loops, each iterating n times. What is its typical time complexity?", ("O(1)", "O(log n)", "O(n)", "O(n²)"), "d"),
    _question("problem-solving-algorithms", 5, "intermediate", "For finding two values that sum to a target, which approach can usually achieve O(n) average time?", ("Compare every possible pair", "Sort with nested loops", "Scan once while storing seen values in a hash set/map", "Repeat a linear search for each value"), "c"),
)

SKILL_IDS = tuple(item["id"] for item in SKILLS)
SKILL_NAMES = {item["id"]: item["name"] for item in SKILLS}
QUESTION_BY_ID = {item["id"]: item for item in ASSESSMENT_QUESTIONS}

if len(QUESTION_BY_ID) != len(ASSESSMENT_QUESTIONS):
    raise ValueError("Assessment question IDs must be unique.")
if any(item["skill_id"] not in SKILL_NAMES for item in ASSESSMENT_QUESTIONS):
    raise ValueError("Assessment questions must use only official skill IDs.")
if any(
    len({option["id"] for option in item["options"]}) != len(item["options"])
    or item["correct_option_id"] not in {option["id"] for option in item["options"]}
    for item in ASSESSMENT_QUESTIONS
):
    raise ValueError("Each question must have unique options and one valid answer key.")
if any(sum(item["skill_id"] == skill_id for item in ASSESSMENT_QUESTIONS) != 5 for skill_id in SKILL_IDS):
    raise ValueError("The MVP assessment requires five questions per official skill.")


def public_questions(skill_id: str) -> list[dict[str, Any]]:
    """Return question content without server-only answer keys."""
    return [
        {
            "id": item["id"],
            "skill_id": item["skill_id"],
            "skill_name": SKILL_NAMES[item["skill_id"]],
            "difficulty": item["difficulty"],
            "text": item["text"],
            "options": item["options"],
        }
        for item in ASSESSMENT_QUESTIONS
        if item["skill_id"] == skill_id
    ]
