"""
curriculum_manager.py - نظام إدارة الدورات التعليمية الشاملة

يدير سلسلات منظمة من الفيديوهات (دورات كاملة) لكل لغة برمجة و تخصص
مثل Python من البداية للنهاية (Part 1, 2, 3...)، JavaScript، SQL، الخ.
كل دورة تحتوي على 15-25 جزء منظم بعناية، مع هاشتاج موحد لكل سلسلة.

المجموع: 100+ موضوع منظم في دورات متسلسلة.
"""

import json
import os
import random
from typing import List, Dict, Optional, Tuple
from src.config import Config
from src.logger import Logger


class CurriculumManager:
    """إدارة الدورات والمواضيع المنظمة"""
    
    # ============================================================
    # PYTHON - Complete Series (25 Parts)
    # ============================================================
    PYTHON_CURRICULUM = {
        "language": "python",
        "series_name": "Python Mastery Complete Series",
        "series_hashtag": "#PythonMastery",
        "total_parts": 25,
        "description": "Learn Python from absolute beginner to advanced developer",
        "parts": [
            # BASICS (Part 1-5)
            {"part": 1, "title": "Python Installation & Your First Program", "keywords": "setup, IDE, hello world", "difficulty": "beginner"},
            {"part": 2, "title": "Variables, Data Types & Type Conversion", "keywords": "int, str, float, bool, conversion", "difficulty": "beginner"},
            {"part": 3, "title": "String Operations & String Methods", "keywords": "concatenation, formatting, f-strings", "difficulty": "beginner"},
            {"part": 4, "title": "Numbers & Math Operations", "keywords": "arithmetic, operators, math module", "difficulty": "beginner"},
            {"part": 5, "title": "User Input & Output", "keywords": "input, print, formatting output", "difficulty": "beginner"},
            
            # CONTROL FLOW (Part 6-9)
            {"part": 6, "title": "If, Elif, Else Statements", "keywords": "conditionals, boolean logic", "difficulty": "beginner"},
            {"part": 7, "title": "For Loops Explained", "keywords": "iteration, range, break, continue", "difficulty": "beginner"},
            {"part": 8, "title": "While Loops & Loop Control", "keywords": "while, infinite loops, loop conditions", "difficulty": "beginner"},
            {"part": 9, "title": "Nested Loops & Complex Flow", "keywords": "nested loops, pattern printing", "difficulty": "intermediate"},
            
            # FUNCTIONS (Part 10-12)
            {"part": 10, "title": "Functions Basics & Parameters", "keywords": "def, parameters, return values", "difficulty": "intermediate"},
            {"part": 11, "title": "Default Arguments & *args, **kwargs", "keywords": "variable arguments, flexibility", "difficulty": "intermediate"},
            {"part": 12, "title": "Scope & Variable Lifetime", "keywords": "local, global, nonlocal, scope rules", "difficulty": "intermediate"},
            
            # DATA STRUCTURES (Part 13-17)
            {"part": 13, "title": "Lists: Create, Access, Modify", "keywords": "lists, indexing, slicing, methods", "difficulty": "intermediate"},
            {"part": 14, "title": "Tuples & Unpacking", "keywords": "immutable, tuples, unpacking", "difficulty": "intermediate"},
            {"part": 15, "title": "Dictionaries & Key-Value Pairs", "keywords": "dict, keys, values, operations", "difficulty": "intermediate"},
            {"part": 16, "title": "Sets & Set Operations", "keywords": "sets, unique values, union, intersection", "difficulty": "intermediate"},
            {"part": 17, "title": "List Comprehensions & Generators", "keywords": "comprehensions, generators, yield", "difficulty": "advanced"},
            
            # OOP (Part 18-21)
            {"part": 18, "title": "Classes & Objects Fundamentals", "keywords": "class, object, attributes, methods", "difficulty": "intermediate"},
            {"part": 19, "title": "Inheritance & Method Overriding", "keywords": "inheritance, super, overriding", "difficulty": "advanced"},
            {"part": 20, "title": "Polymorphism & Abstract Classes", "keywords": "polymorphism, ABC, abstract methods", "difficulty": "advanced"},
            {"part": 21, "title": "Magic Methods & Dunder Methods", "keywords": "__init__, __str__, __add__", "difficulty": "advanced"},
            
            # ADVANCED (Part 22-25)
            {"part": 22, "title": "Decorators & Function Wrappers", "keywords": "decorators, wrappers, functools", "difficulty": "advanced"},
            {"part": 23, "title": "Context Managers & With Statement", "keywords": "context manager, __enter__, __exit__", "difficulty": "advanced"},
            {"part": 24, "title": "Async/Await & Asynchronous Programming", "keywords": "async, await, asyncio", "difficulty": "advanced"},
            {"part": 25, "title": "Testing & Best Practices", "keywords": "pytest, unittest, TDD, best practices", "difficulty": "advanced"},
        ]
    }
    
    # ============================================================
    # JAVASCRIPT - Complete Series (22 Parts)
    # ============================================================
    JAVASCRIPT_CURRICULUM = {
        "language": "javascript",
        "series_name": "JavaScript Mastery Complete Series",
        "series_hashtag": "#JavaScriptMastery",
        "total_parts": 22,
        "description": "Master JavaScript from basics to advanced patterns",
        "parts": [
            # BASICS (Part 1-4)
            {"part": 1, "title": "JavaScript Setup & Hello World", "keywords": "node, browser, first program", "difficulty": "beginner"},
            {"part": 2, "title": "Variables: var, let, const", "keywords": "declaration, scope, const safety", "difficulty": "beginner"},
            {"part": 3, "title": "Data Types & Type Coercion", "keywords": "primitives, typeof, coercion", "difficulty": "beginner"},
            {"part": 4, "title": "Operators & Expressions", "keywords": "arithmetic, comparison, logical", "difficulty": "beginner"},
            
            # CONTROL FLOW (Part 5-7)
            {"part": 5, "title": "Conditional Statements", "keywords": "if, else, switch, ternary", "difficulty": "beginner"},
            {"part": 6, "title": "Loops: for, while, forEach", "keywords": "for, while, do-while, break", "difficulty": "beginner"},
            {"part": 7, "title": "Array Methods Deep Dive", "keywords": "map, filter, reduce, find", "difficulty": "intermediate"},
            
            # FUNCTIONS (Part 8-10)
            {"part": 8, "title": "Functions: Declaration & Expression", "keywords": "function, arrow functions", "difficulty": "beginner"},
            {"part": 9, "title": "Closures & Scope", "keywords": "closure, scope chain, lexical scope", "difficulty": "intermediate"},
            {"part": 10, "title": "Higher-Order Functions", "keywords": "HOF, callbacks, function returning", "difficulty": "intermediate"},
            
            # OBJECTS & THIS (Part 11-13)
            {"part": 11, "title": "Objects & Object Literals", "keywords": "object, properties, methods", "difficulty": "intermediate"},
            {"part": 12, "title": "The 'this' Keyword Explained", "keywords": "this binding, context, call/apply", "difficulty": "intermediate"},
            {"part": 13, "title": "Prototypes & Inheritance", "keywords": "prototype, prototype chain, inheritance", "difficulty": "advanced"},
            
            # ASYNC (Part 14-16)
            {"part": 14, "title": "Callbacks & Event Loop", "keywords": "callbacks, event loop, async", "difficulty": "intermediate"},
            {"part": 15, "title": "Promises Explained", "keywords": "promise, .then, .catch, .finally", "difficulty": "intermediate"},
            {"part": 16, "title": "Async/Await Mastery", "keywords": "async, await, error handling", "difficulty": "advanced"},
            
            # ES6+ (Part 17-19)
            {"part": 17, "title": "Destructuring & Spread Operator", "keywords": "destructuring, spread, rest", "difficulty": "intermediate"},
            {"part": 18, "title": "Template Literals & String Methods", "keywords": "template literals, string interpolation", "difficulty": "beginner"},
            {"part": 19, "title": "Classes & Constructors", "keywords": "class, constructor, static", "difficulty": "intermediate"},
            
            # ADVANCED (Part 20-22)
            {"part": 20, "title": "DOM Manipulation", "keywords": "querySelector, addEventListener, innerHTML", "difficulty": "intermediate"},
            {"part": 21, "title": "Error Handling & Debugging", "keywords": "try-catch, finally, debugging", "difficulty": "intermediate"},
            {"part": 22, "title": "Modern Patterns & Best Practices", "keywords": "patterns, best practices, performance", "difficulty": "advanced"},
        ]
    }
    
    # ============================================================
    # SQL & DATABASES - Complete Series (18 Parts)
    # ============================================================
    SQL_CURRICULUM = {
        "language": "sql",
        "series_name": "SQL & Database Mastery",
        "series_hashtag": "#SQLMastery",
        "total_parts": 18,
        "description": "Learn SQL from basics to advanced database optimization",
        "parts": [
            # BASICS (Part 1-3)
            {"part": 1, "title": "Database Basics & SQL Introduction", "keywords": "database, tables, SQL overview", "difficulty": "beginner"},
            {"part": 2, "title": "SELECT Queries & Basic Filtering", "keywords": "SELECT, WHERE, column selection", "difficulty": "beginner"},
            {"part": 3, "title": "WHERE Conditions & Operators", "keywords": "WHERE, AND, OR, NOT, LIKE", "difficulty": "beginner"},
            
            # INTERMEDIATE (Part 4-8)
            {"part": 4, "title": "JOINS: INNER, LEFT, RIGHT, FULL", "keywords": "INNER JOIN, LEFT JOIN, joins", "difficulty": "intermediate"},
            {"part": 5, "title": "Aggregation & GROUP BY", "keywords": "COUNT, SUM, AVG, GROUP BY, HAVING", "difficulty": "intermediate"},
            {"part": 6, "title": "Subqueries & Nested Queries", "keywords": "subquery, nested SELECT, IN", "difficulty": "intermediate"},
            {"part": 7, "title": "INSERT, UPDATE, DELETE Operations", "keywords": "INSERT, UPDATE, DELETE, data modification", "difficulty": "intermediate"},
            {"part": 8, "title": "Transactions & ACID Properties", "keywords": "transaction, COMMIT, ROLLBACK", "difficulty": "intermediate"},
            
            # ADVANCED (Part 9-13)
            {"part": 9, "title": "Indexes & Query Optimization", "keywords": "index, EXPLAIN, optimization", "difficulty": "advanced"},
            {"part": 10, "title": "Views & Virtual Tables", "keywords": "VIEW, materialized view, abstraction", "difficulty": "advanced"},
            {"part": 11, "title": "Stored Procedures & Functions", "keywords": "stored procedure, function, trigger", "difficulty": "advanced"},
            {"part": 12, "title": "Window Functions & Analytics", "keywords": "OVER, PARTITION BY, ROW_NUMBER", "difficulty": "advanced"},
            {"part": 13, "title": "Common Table Expressions (CTE)", "keywords": "WITH, CTE, recursive CTE", "difficulty": "advanced"},
            
            # EXPERT (Part 14-18)
            {"part": 14, "title": "Database Design & Normalization", "keywords": "normalization, 1NF, 2NF, 3NF", "difficulty": "advanced"},
            {"part": 15, "title": "Foreign Keys & Relationships", "keywords": "foreign key, one-to-many, many-to-many", "difficulty": "intermediate"},
            {"part": 16, "title": "Performance Tuning & Scaling", "keywords": "performance, tuning, scaling", "difficulty": "expert"},
            {"part": 17, "title": "Backup & Recovery Strategies", "keywords": "backup, recovery, disaster recovery", "difficulty": "expert"},
            {"part": 18, "title": "Security & Best Practices", "keywords": "security, SQL injection, permissions", "difficulty": "expert"},
        ]
    }
    
    # ============================================================
    # WEB DEVELOPMENT - Complete Series (20 Parts)
    # ============================================================
    WEB_DEVELOPMENT_CURRICULUM = {
        "language": "javascript",
        "series_name": "Web Development Complete Series",
        "series_hashtag": "#WebDevMastery",
        "total_parts": 20,
        "description": "Build modern web applications from frontend to backend",
        "parts": [
            # HTML & CSS (Part 1-4)
            {"part": 1, "title": "HTML5 Fundamentals & Semantic Elements", "keywords": "HTML5, semantic, structure", "difficulty": "beginner"},
            {"part": 2, "title": "CSS Basics & Styling", "keywords": "CSS, selectors, properties", "difficulty": "beginner"},
            {"part": 3, "title": "Flexbox & CSS Grid", "keywords": "flexbox, grid, layout", "difficulty": "intermediate"},
            {"part": 4, "title": "Responsive Design & Media Queries", "keywords": "responsive, mobile-first, media queries", "difficulty": "intermediate"},
            
            # JAVASCRIPT DOM (Part 5-7)
            {"part": 5, "title": "DOM Manipulation & Event Listeners", "keywords": "DOM, querySelector, addEventListener", "difficulty": "intermediate"},
            {"part": 6, "title": "Form Validation & Input Handling", "keywords": "forms, validation, input", "difficulty": "intermediate"},
            {"part": 7, "title": "AJAX & Fetch API", "keywords": "AJAX, fetch, async requests", "difficulty": "intermediate"},
            
            # FRAMEWORKS (Part 8-12)
            {"part": 8, "title": "React Basics & Components", "keywords": "React, JSX, components", "difficulty": "intermediate"},
            {"part": 9, "title": "React Hooks & State Management", "keywords": "hooks, useState, useEffect", "difficulty": "intermediate"},
            {"part": 10, "title": "React Router & Navigation", "keywords": "React Router, routing, navigation", "difficulty": "intermediate"},
            {"part": 11, "title": "State Management with Redux", "keywords": "Redux, state, actions", "difficulty": "advanced"},
            {"part": 12, "title": "Vue.js Alternative", "keywords": "Vue, components, Vue Router", "difficulty": "intermediate"},
            
            # BACKEND (Part 13-16)
            {"part": 13, "title": "Node.js & Express Basics", "keywords": "Node.js, Express, server", "difficulty": "intermediate"},
            {"part": 14, "title": "REST API Design & Building", "keywords": "REST, API, endpoints", "difficulty": "intermediate"},
            {"part": 15, "title": "Database Integration", "keywords": "database, MongoDB, MySQL", "difficulty": "intermediate"},
            {"part": 16, "title": "Authentication & Authorization", "keywords": "auth, JWT, sessions", "difficulty": "advanced"},
            
            # DEPLOYMENT & TOOLS (Part 17-20)
            {"part": 17, "title": "Git & Version Control", "keywords": "git, GitHub, branching", "difficulty": "beginner"},
            {"part": 18, "title": "Webpack & Build Tools", "keywords": "webpack, bundling, build", "difficulty": "advanced"},
            {"part": 19, "title": "Testing Web Applications", "keywords": "testing, Jest, Cypress", "difficulty": "intermediate"},
            {"part": 20, "title": "Deployment & DevOps Basics", "keywords": "deployment, Heroku, Docker", "difficulty": "advanced"},
        ]
    }
    
    # ============================================================
    # DATA SCIENCE & PYTHON - Complete Series (17 Parts)
    # ============================================================
    DATA_SCIENCE_CURRICULUM = {
        "language": "python",
        "series_name": "Data Science with Python",
        "series_hashtag": "#DataScienceMastery",
        "total_parts": 17,
        "description": "Master data science tools and techniques with Python",
        "parts": [
            {"part": 1, "title": "NumPy Fundamentals", "keywords": "numpy, arrays, matrix", "difficulty": "beginner"},
            {"part": 2, "title": "Pandas Data Manipulation", "keywords": "pandas, DataFrame, Series", "difficulty": "beginner"},
            {"part": 3, "title": "Data Cleaning & Preprocessing", "keywords": "cleaning, missing data, outliers", "difficulty": "intermediate"},
            {"part": 4, "title": "Exploratory Data Analysis (EDA)", "keywords": "EDA, visualization, insights", "difficulty": "intermediate"},
            {"part": 5, "title": "Matplotlib & Data Visualization", "keywords": "matplotlib, plotting, graphs", "difficulty": "intermediate"},
            {"part": 6, "title": "Seaborn Advanced Plotting", "keywords": "seaborn, heatmap, statistical plots", "difficulty": "intermediate"},
            {"part": 7, "title": "Statistics Fundamentals", "keywords": "statistics, distributions, hypothesis", "difficulty": "intermediate"},
            {"part": 8, "title": "Linear Regression", "keywords": "regression, linear model, prediction", "difficulty": "intermediate"},
            {"part": 9, "title": "Classification Algorithms", "keywords": "classification, logistic regression, SVM", "difficulty": "advanced"},
            {"part": 10, "title": "Clustering Techniques", "keywords": "clustering, K-means, hierarchical", "difficulty": "advanced"},
            {"part": 11, "title": "Dimensionality Reduction", "keywords": "PCA, reduction, feature extraction", "difficulty": "advanced"},
            {"part": 12, "title": "Scikit-Learn Deep Dive", "keywords": "scikit-learn, pipeline, preprocessing", "difficulty": "advanced"},
            {"part": 13, "title": "Neural Networks Basics", "keywords": "neural networks, deep learning, TensorFlow", "difficulty": "advanced"},
            {"part": 14, "title": "Model Evaluation & Validation", "keywords": "evaluation, cross-validation, metrics", "difficulty": "intermediate"},
            {"part": 15, "title": "Feature Engineering Strategies", "keywords": "feature engineering, selection, creation", "difficulty": "advanced"},
            {"part": 16, "title": "Time Series Analysis", "keywords": "time series, forecasting, ARIMA", "difficulty": "advanced"},
            {"part": 17, "title": "Real-World Project Walkthrough", "keywords": "project, real data, end-to-end", "difficulty": "advanced"},
        ]
    }
    
    # ============================================================
    # ALGORITHMS & DATA STRUCTURES - Complete Series (16 Parts)
    # ============================================================
    ALGORITHMS_CURRICULUM = {
        "language": "python",
        "series_name": "Algorithms & Data Structures Mastery",
        "series_hashtag": "#AlgorithmsMastery",
        "total_parts": 16,
        "description": "Master essential algorithms and data structures for interviews and optimization",
        "parts": [
            {"part": 1, "title": "Big O Notation & Complexity Analysis", "keywords": "Big O, time complexity, space complexity", "difficulty": "intermediate"},
            {"part": 2, "title": "Arrays & Linked Lists", "keywords": "array, linked list, operations", "difficulty": "beginner"},
            {"part": 3, "title": "Stacks & Queues", "keywords": "stack, queue, LIFO, FIFO", "difficulty": "beginner"},
            {"part": 4, "title": "Trees & Binary Trees", "keywords": "tree, binary tree, traversal", "difficulty": "intermediate"},
            {"part": 5, "title": "Binary Search Trees (BST)", "keywords": "BST, search, insertion, deletion", "difficulty": "intermediate"},
            {"part": 6, "title": "Graphs & Graph Traversal", "keywords": "graph, DFS, BFS, traversal", "difficulty": "intermediate"},
            {"part": 7, "title": "Sorting Algorithms Compared", "keywords": "sort, bubble sort, merge sort, quick sort", "difficulty": "intermediate"},
            {"part": 8, "title": "Search Algorithms", "keywords": "binary search, linear search", "difficulty": "beginner"},
            {"part": 9, "title": "Dynamic Programming Basics", "keywords": "DP, memoization, optimization", "difficulty": "advanced"},
            {"part": 10, "title": "Greedy Algorithms", "keywords": "greedy, optimization, problem solving", "difficulty": "advanced"},
            {"part": 11, "title": "Hash Tables & Hash Functions", "keywords": "hash table, hash function, collision", "difficulty": "intermediate"},
            {"part": 12, "title": "Heaps & Priority Queues", "keywords": "heap, priority queue, min-heap", "difficulty": "intermediate"},
            {"part": 13, "title": "String Algorithms", "keywords": "string, pattern matching, KMP", "difficulty": "advanced"},
            {"part": 14, "title": "Divide & Conquer Algorithms", "keywords": "divide conquer, merge sort, quick sort", "difficulty": "advanced"},
            {"part": 15, "title": "Backtracking & Recursion", "keywords": "backtracking, recursion, N-queens", "difficulty": "advanced"},
            {"part": 16, "title": "Interview Questions Walkthrough", "keywords": "interview, coding challenges, practice", "difficulty": "advanced"},
        ]
    }
    
    # Merge all curricula
    ALL_CURRICULA = [
        PYTHON_CURRICULUM,
        JAVASCRIPT_CURRICULUM,
        SQL_CURRICULUM,
        WEB_DEVELOPMENT_CURRICULUM,
        DATA_SCIENCE_CURRICULUM,
        ALGORITHMS_CURRICULUM,
    ]
    
    @classmethod
    def get_all_topics(cls) -> List[Dict]:
        """الحصول على قائمة كاملة بجميع المواضيع"""
        all_topics = []
        for curriculum in cls.ALL_CURRICULA:
            for part in curriculum["parts"]:
                topic = {
                    "language": curriculum.get("language", "unknown"),
                    "series": curriculum.get("series_name", ""),
                    "series_hashtag": curriculum.get("series_hashtag", ""),
                    "part": part["part"],
                    "title": part["title"],
                    "keywords": part["keywords"],
                    "difficulty": part["difficulty"],
                    "full_topic": f"{curriculum['series_name']} - Part {part['part']}: {part['title']}"
                }
                all_topics.append(topic)
        return all_topics
    
    @classmethod
    def get_curriculum_by_series(cls, series_name: str) -> Optional[Dict]:
        """الحصول على دورة كاملة بناءً على اسمها"""
        for curriculum in cls.ALL_CURRICULA:
            if curriculum["series_name"].lower() == series_name.lower():
                return curriculum
        return None
    
    @classmethod
    def get_next_topic_in_series(cls, series_name: str, current_part: int) -> Optional[Dict]:
        """الحصول على الموضوع التالي في نفس السلسلة"""
        curriculum = cls.get_curriculum_by_series(series_name)
        if not curriculum:
            return None
        
        for part in curriculum["parts"]:
            if part["part"] == current_part + 1:
                return {
                    "language": curriculum.get("language"),
                    "series": series_name,
                    "series_hashtag": curriculum.get("series_hashtag"),
                    "part": part["part"],
                    "title": part["title"],
                    "full_topic": f"{series_name} - Part {part['part']}: {part['title']}"
                }
        return None
    
    @classmethod
    def get_random_topic(cls) -> Dict:
        """اختيار موضوع عشوائي من جميع المواضيع"""
        all_topics = cls.get_all_topics()
        return random.choice(all_topics) if all_topics else {}
    
    @classmethod
    def get_topics_by_difficulty(cls, difficulty: str) -> List[Dict]:
        """الحصول على جميع المواضيع حسب مستوى الصعوبة"""
        all_topics = cls.get_all_topics()
        return [t for t in all_topics if t["difficulty"] == difficulty]
    
    @classmethod
    def get_topics_by_language(cls, language: str) -> List[Dict]:
        """الحصول على جميع المواضيع حسب لغة البرمجة"""
        all_topics = cls.get_all_topics()
        return [t for t in all_topics if t["language"].lower() == language.lower()]
    
    @classmethod
    def export_topics_to_file(cls, filepath: str = None):
        """تصدير جميع المواضيع إلى ملف نصي"""
        if filepath is None:
            filepath = os.path.join(Config.BASE_DIR, "topics_curriculum.txt")
        
        all_topics = cls.get_all_topics()
        
        with open(filepath, "w", encoding="utf-8") as f:
            for topic in all_topics:
                f.write(f"{topic['full_topic']}\n")
        
        Logger.success(f"Exported {len(all_topics)} topics to {filepath}")
        return filepath
    
    @classmethod
    def get_series_summary(cls) -> str:
        """الحصول على ملخص جميع السلاسل المتاحة"""
        summary = "📚 Available Programming Series:\n\n"
        
        total_parts = 0
        for curriculum in cls.ALL_CURRICULA:
            parts_count = curriculum["total_parts"]
            total_parts += parts_count
            summary += f"✅ {curriculum['series_name']}\n"
            summary += f"   🏷️  Hashtag: {curriculum['series_hashtag']}\n"
            summary += f"   📝 Parts: {parts_count}\n"
            summary += f"   🗣️  Language: {curriculum['language'].upper()}\n"
            summary += f"   📖 {curriculum['description']}\n\n"
        
        summary += f"=" * 60 + "\n"
        summary += f"🎯 TOTAL: {total_parts} parts across {len(cls.ALL_CURRICULA)} series\n"
        summary += f"💡 100+ programming topics organized in complete courses\n"
        
        return summary
