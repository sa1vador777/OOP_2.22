#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import sqlite3
from pathlib import Path
from pprint import pprint


def create_connection(database_path: Path) -> sqlite3.Connection | sqlite3.Cursor:
    
    connection = sqlite3.connect(database_path)
    cursor = connection.cursor()

    return connection, cursor


def create_db(database_path: Path) -> None:

    connection, cursor = create_connection(database_path)

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS marks (
        marks_id INTEGER PRIMARY KEY AUTOINCREMENT,
        marks_list TEXT NOT NULL  
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        group_num INTEGER NOT NULL,
        marks_id INTEGER NOT NULL,
        FOREIGN KEY(marks_id) REFERENCES marks(marks_id) 
        )
        """
    )

    connection.close()


def add_student(database_path: Path, name: str, group: int, marks: list[int]) -> None:

    connection, cursor = create_connection(database_path)

    cursor.execute(
        """
        INSERT INTO marks (marks_list) VALUES (?)
        """, (str(marks),)
    )
    marks_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO students (name, group_num, marks_id) VALUES (?, ?, ?)
        """, (name, group, marks_id)
    )

    connection.commit()
    connection.close()


def main_func(database_path: Path, count: int = None, read_from_json: bool = False,
        write_to_json: bool = False) -> list[dict]:
    list_smart_stud: list[dict] = []
    if read_from_json:
        with open("students.json", 'r', encoding='utf-8') as file:
            list_stud = json.load(file)
        for element in list_stud:
            if sum(element["Успеваемость"]) / len(element["Успеваемость"]) > 4.0:
                list_smart_stud.append(element)

    elif not read_from_json:
        list_stud: list[dict] = []
        i = 0

        while i < count:
            print(f"Введите данные студента {i+1}")
            name = input("Введите ФИО: ")
            group = int(input("Введите группу: "))
            marks = list(map(int, list(input("Введите 5 оценок через пробел: ").split(' '))))
            list_stud.append(dict([["ФИО", name], ["Группа", group], ["Успеваемость", marks]]))
            add_student(database_path, name, group, marks)
            i+=1

        for element in list_stud:
            if sum(element["Успеваемость"]) / len(element["Успеваемость"]) > 4.0:
                list_smart_stud.append(element)
                
    list_smart_stud = sorted(list_smart_stud, key=lambda x: x["Группа"])
    
    if write_to_json:
        with open("students.json", 'w', encoding='utf-8') as file:
                json.dump(list_smart_stud, file)
        return "Результат успешно записан в базу данных"
    
    return list_smart_stud
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--read', action='store_true', help='Считать ли данные студентов c .json файла')
    parser.add_argument('-w', '--write', action='store_true', help='Записать ли итоги расчетов в .json файл?')
    parser.add_argument('c', type=int, help='Количество студентов')
    database_path = Path("main.db")
    create_db(database_path)
    args = parser.parse_args()
    write_to_json = False
    read_from_json = False
    if args.write:
        write_to_json = True
        if args.read:
            count = None
            read_from_json = True
        else:
            count = args.c
    elif args.read:
        read_from_json = True
        count = 0
    else:
        count = args.c

    pprint(main_func(database_path=database_path, count=count, read_from_json=read_from_json,
                write_to_json=write_to_json))
