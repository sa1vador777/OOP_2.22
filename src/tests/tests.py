#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import sqlite3
import mock
import json
import os, sys
from pathlib import Path
sys.path.insert(1,os.path.join(sys.path[0], '..'))
from main import create_db, add_student, main_func

s = []

class TestStudentDatabase(unittest.TestCase):

    def setUp(self):
        """Создаем тестовую базу данных перед каждым тестом"""
        self.db_path = Path("test_database.db")
        create_db(self.db_path)

    def tearDown(self):
        """Удаляем тестовую базу данных после каждого теста"""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_create_db(self):
        """Проверяем, что база данных и таблицы созданы"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Проверяем, существует ли таблица marks
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='marks'")
        self.assertIsNotNone(cursor.fetchone(), "Таблица marks не создана")

        # Проверяем, существует ли таблица students
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students'")
        self.assertIsNotNone(cursor.fetchone(), "Таблица students не создана")

        conn.close()

    def test_add_student(self):
        """Проверяем, что студент добавляется в базу данных"""
        add_student(self.db_path, name="Иван Иванов", group=101, marks=[5, 4, 3, 5, 4])

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Проверяем, что студент добавлен
        cursor.execute("SELECT name, group_num FROM students WHERE name=?", ("Иван Иванов",))
        student = cursor.fetchone()
        self.assertIsNotNone(student, "Студент не добавлен")
        self.assertEqual(student[0], "Иван Иванов")
        self.assertEqual(student[1], 101)

        # Проверяем, что оценки добавлены
        cursor.execute("SELECT marks_list FROM marks WHERE marks_id=?", (1,))
        marks = cursor.fetchone()
        self.assertEqual(marks[0], str([5, 4, 3, 5, 4]), "Оценки добавлены неправильно")

        conn.close()

class TestStudentMainFunction(unittest.TestCase):

    def test_main_without_json(self):
        """Проверяем, что функция main работает корректно без JSON"""
        # Подаем 3 студента с разной успеваемостью
        input_data = ["Иван Иванов", "101", "5 5 5 5 5", 
                      "Петр Петров", "102", "4 4 4 4 4", 
                      "Сидор Сидоров", "101", "3 3 3 3 3"]

        with mock.patch('builtins.input', side_effect=input_data):
            result = main_func(database_path="main.db", 
                               count=3, read_from_json=False, write_to_json=False)
        
        # Ожидаем, что вернется только Иван Иванов, так как у него средняя оценка > 4.0
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ФИО"], "Иван Иванов")
        self.assertEqual(result[0]["Группа"], 101)

    def test_main_with_json(self):
        """Проверяем, что функция main правильно считывает данные из JSON"""
        students_data = [
            {"ФИО": "Иван Иванов", "Группа": 101, "Успеваемость": [5, 5, 5, 5, 5]},
            {"ФИО": "Петр Петров", "Группа": 102, "Успеваемость": [4, 4, 4, 4, 4]}
        ]

        with open("students.json", 'w', encoding='utf-8') as file:
            json.dump(students_data, file)

        result = main_func(database_path="main.db", count=None, read_from_json=True,
                            write_to_json=False)

        # Проверяем, что вернется только Иван Иванов, так как у него средняя оценка > 4.0
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["ФИО"], "Иван Иванов")
        self.assertEqual(result[0]["Группа"], 101)

        os.remove("students.json")

if __name__ == "__main__":
    unittest.main()
