#!/usr/bin/env python3
# update_client_for_testing.py - Aktualizuje klienta CLI dla obsługi testów

import sys
import os
import re

# Ścieżka do pliku klienta CLI
CLI_CLIENT_PATH = "cli_client_extended.py"


# Funkcja dodająca obsługę trybu nieinteraktywnego
def add_non_interactive_mode():
    if not os.path.exists(CLI_CLIENT_PATH):
        print(f"Błąd: Plik {CLI_CLIENT_PATH} nie istnieje.")
        return False

    # Przeczytaj zawartość pliku
    with open(CLI_CLIENT_PATH, 'r') as file:
        content = file.read()

    # Sprawdź, czy tryb nieinteraktywny jest już obsługiwany
    if "--non-interactive" in content:
        print("Tryb nieinteraktywny jest już obsługiwany.")
        return True

    # Znajdź definicję funkcji main()
    main_pattern = r"def main\(\):"
    main_match = re.search(main_pattern, content)
    if not main_match:
        print("Nie znaleziono definicji funkcji main().")
        return False

    # Znajdź pozycję funkcji argparse.ArgumentParser()
    parser_pattern = r"parser = argparse\.ArgumentParser\("
    parser_match = re.search(parser_pattern, content)
    if not parser_match:
        print("Nie znaleziono definicji ArgumentParser.")
        return False

    # Znajdź linię, w której dodawane są argumenty
    args_pattern = r"parser\.add_argument\("
    args_matches = list(re.finditer(args_pattern, content))
    if not args_matches:
        print("Nie znaleziono dodawania argumentów.")
        return False

    # Dodaj argument dla trybu nieinteraktywnego po ostatnim wywołaniu add_argument
    last_args_match = args_matches[-1]
    last_args_pos = content.find("\n", last_args_match.end())

    # Nowa linia do dodania
    new_arg_line = """    parser.add_argument('--non-interactive', action='store_true', help='Run in non-interactive mode')\n"""

    # Zaktualizuj zawartość
    updated_content = content[:last_args_pos] + "\n" + new_arg_line + content[last_args_pos:]

    # Znajdź funkcję run_shell
    run_shell_pattern = r"def run_shell\(self\):"
    run_shell_match = re.search(run_shell_pattern, updated_content)
    if not run_shell_match:
        print("Nie znaleziono metody run_shell().")
        return False

    # Znajdź początek pętli while w run_shell
    while_pattern = r"\s+while True:"
    while_match = re.search(while_pattern, updated_content[run_shell_match.end():])
    if not while_match:
        print("Nie znaleziono pętli while w metodzie run_shell().")
        return False

    # Pozycja początku pętli while
    while_pos = run_shell_match.end() + while_match.start()

    # Dodaj kod obsługi trybu nieinteraktywnego przed pętlą while
    non_interactive_code = """        # Obsługa trybu nieinteraktywnego
        if hasattr(self, 'non_interactive') and self.non_interactive:
            # Pobierz zapytanie ze standardowego wejścia
            query = sys.stdin.read().strip()
            if query:
                result = self.process_query(query)
                self.display_results(result)
            return\n
"""

    # Zaktualizuj zawartość
    updated_content = updated_content[:while_pos] + non_interactive_code + updated_content[while_pos:]

    # Zaktualizuj konstruktor klasy, aby przyjmował parametr non_interactive
    init_pattern = r"def __init__\(self, db_path=\"text2sql\.db\", llm_url=None, use_local_llm=True\):"
    init_match = re.search(init_pattern, updated_content)
    if not init_match:
        # Spróbuj znaleźć dowolny konstruktor __init__
        init_pattern = r"def __init__\(self[^)]*\):"
        init_match = re.search(init_pattern, updated_content)
        if not init_match:
            print("Nie znaleziono konstruktora __init__.")
            return False

    # Znajdź koniec deklaracji konstruktora
    init_end = updated_content.find(":", init_match.end())

    # Zaktualizuj deklarację konstruktora
    updated_init = updated_content[init_match.start():init_end] + ", non_interactive=False" + updated_content[init_end:]

    # Znajdź pierwsze przypisanie w konstruktorze
    first_assignment = re.search(r"\n\s+self\.[a-zA-Z_]+ =", updated_init[init_match.end():])
    if not first_assignment:
        print("Nie znaleziono przypisania w konstruktorze.")
        return False

    # Pozycja pierwszego przypisania
    assignment_pos = init_match.end() + first_assignment.start()

    # Dodaj inicjalizację parametru non_interactive
    init_code = "\n        self.non_interactive = non_interactive"
    updated_init = updated_init[:assignment_pos] + init_code + updated_init[assignment_pos:]

    # Zaktualizuj wywołanie konstruktora w main()
    main_end = updated_init.find("main()")
    if main_end == -1:
        print("Nie znaleziono wywołania main().")
        return False

    # Znajdź tworzenie obiektu shell w main()
    shell_creation_pattern = r"shell = Text2SQLShell\("
    shell_creation_match = re.search(shell_creation_pattern, updated_init)
    if not shell_creation_match:
        print("Nie znaleziono tworzenia obiektu shell w main().")
        return False

    # Znajdź koniec tworzenia obiektu shell
    shell_creation_end = updated_init.find(")", shell_creation_match.end())
    if shell_creation_end == -1:
        print("Nie znaleziono końca tworzenia obiektu shell.")
        return False

    # Dodaj parametr non_interactive do tworzenia obiektu shell
    updated_shell_creation = updated_init[
                             :shell_creation_end] + ",\n        non_interactive=args.non_interactive" + updated_init[
                                                                                                        shell_creation_end:]

    # Zapisz zaktualizowaną zawartość
    with open(CLI_CLIENT_PATH, 'w') as file:
        file.write(updated_shell_creation)

    print(f"Plik {CLI_CLIENT_PATH} został zaktualizowany do obsługi trybu nieinteraktywnego.")
    return True


if __name__ == "__main__":
    print("Aktualizowanie klienta CLI dla trybu nieinteraktywnego...")
    if add_non_interactive_mode():
        print("Aktualizacja zakończona pomyślnie.")
        sys.exit(0)
    else:
        print("Aktualizacja nie powiodła się.")
        sys.exit(1)