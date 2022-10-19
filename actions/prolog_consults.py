from time import sleep
from swiplserver import PrologMQI, PrologThread, create_posix_path

class PrologConsult():

    def __init__(self) -> None:
        self.path = create_posix_path("F:/rasa_chat/actions/Practico.pl")

    def consultAgenda(self, day, hour):
        return self.makeConsult(f"consultar_agenda({day}, {hour}, Actividad).")

    def consultCourses(self):
        return self.makeConsult("cursadas(X).")

    def makeConsult(self, query, allResults = True):
        with PrologMQI(port=8000) as mqi:
            with mqi.create_thread() as prolog_thread:
                prolog_thread.query_async(f'consult("{self.path}").', find_all=False)
                prolog_thread.query_async_result()

                prolog_thread.query_async(f"{query}", find_all = allResults)
                sleep(0.1)

                result = prolog_thread.query_async_result()

                return result
