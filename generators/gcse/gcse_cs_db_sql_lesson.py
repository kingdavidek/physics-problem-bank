"""
GCSE Computer Science – Relational Databases & SQL
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Each variant returns (question, solution, hint, marks).
"""
import random
from generators.shared.utils import make_problem
from generators.shared.variant_utils import pick_named_variant


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _db_f1_database():
    q = "What is a <strong>database</strong>?"
    s = (
        "An organised collection of <strong>structured data</strong> stored electronically "
        "so it can be searched, updated and managed efficiently."
    )
    return q, s, "Think: school pupil records, shop stock.", 1


def _db_f2_relational():
    q = "What is a <strong>relational database</strong>?"
    s = (
        "Data is stored in <strong>related tables</strong> (rows and columns) linked by "
        "<strong>keys</strong>, rather than one giant flat file."
    )
    return q, s, "Tables + relationships.", 2


def _db_f3_table_record_field():
    q = "Define <strong>table</strong>, <strong>record</strong>, and <strong>field</strong>."
    s = (
        "<strong>Table</strong> — collection of data about one type of thing (e.g. Pupil). "
        "<strong>Record</strong> — one row (one pupil). "
        "<strong>Field</strong> — one column (e.g. Surname)."
    )
    return q, s, "Table = sheet; record = row; field = column.", 2


def _db_f4_primary_key():
    q = "What is a <strong>primary key</strong>?"
    s = (
        "A field that <strong>uniquely identifies</strong> each record in a table "
        "(e.g. PupilID). No two rows share the same value."
    )
    return q, s, "Unique ID for each row.", 2


def _db_f5_foreign_key():
    q = "What is a <strong>foreign key</strong>?"
    s = (
        "A field that <strong>links to the primary key</strong> in another table "
        "(e.g. ClassID in Pupil table links to Class table)."
    )
    return q, s, "Creates a relationship between tables.", 2


def _db_f6_redundancy():
    q = "What is <strong>data redundancy</strong>?"
    s = (
        "The same data stored <strong>more than once</strong> in different places, "
        "which can cause inconsistency when one copy is updated and another is not."
    )
    return q, s, "Duplicate data = redundancy.", 2


def _db_f7_select():
    q = "What does <code>SELECT</code> do in SQL?"
    s = (
        "<code>SELECT</code> chooses <strong>which columns</strong> to return from a query "
        "(e.g. <code>SELECT FirstName, Surname</code>)."
    )
    return q, s, "SELECT = which fields to show.", 1


def _db_f8_from():
    q = "What does <code>FROM</code> do in SQL?"
    s = (
        "<code>FROM</code> names the <strong>table</strong> to read data from "
        "(e.g. <code>FROM Pupil</code>)."
    )
    return q, s, "FROM = which table.", 1


def _db_f9_where():
    q = "What does <code>WHERE</code> do in SQL?"
    s = (
        "<code>WHERE</code> <strong>filters</strong> records — only rows matching the "
        "condition are returned (e.g. <code>WHERE YearGroup = 11</code>)."
    )
    return q, s, "WHERE = filter rows.", 2


def _db_f10_data_type():
    q = "Give <strong>two data types</strong> used for database fields."
    s = (
        "Examples: <strong>INTEGER</strong> (whole numbers), <strong>TEXT/VARCHAR</strong> "
        "(strings), <strong>BOOLEAN</strong>, <strong>REAL</strong> (decimals), <strong>DATE</strong>."
    )
    return q, s, "Match type to the data stored.", 2


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _db_i1_select_star():
    q = "Write SQL to list <strong>all columns</strong> from table <code>Pupil</code>."
    s = "<pre>SELECT * FROM Pupil;</pre>"
    return q, s, "<code>*</code> means all fields.", 2


def _db_i2_where_example():
    q = "Write SQL to show surnames of pupils in <strong>Year 11</strong> from <code>Pupil</code>."
    s = (
        "<pre>SELECT Surname FROM Pupil WHERE YearGroup = 11;</pre>"
    )
    return q, s, "SELECT columns FROM table WHERE condition.", 2


def _db_i3_order_by():
    q = "What does <code>ORDER BY Surname ASC</code> do?"
    s = (
        "Sorts results <strong>alphabetically by Surname</strong> ascending (A→Z). "
        "<code>DESC</code> would sort descending (Z→A)."
    )
    return q, s, "ORDER BY = sort results.", 2


def _db_i4_insert():
    q = "Write SQL to <strong>insert</strong> a new pupil: ID 42, name Ali, year 10."
    s = (
        "<pre>INSERT INTO Pupil (PupilID, FirstName, YearGroup)\n"
        "VALUES (42, 'Ali', 10);</pre>"
    )
    return q, s, "INSERT INTO … VALUES …", 3


def _db_i5_update():
    q = "Write SQL to change pupil <strong>42</strong> to Year <strong>11</strong>."
    s = (
        "<pre>UPDATE Pupil SET YearGroup = 11 WHERE PupilID = 42;</pre>"
    )
    return q, s, "UPDATE … SET … WHERE …", 3


def _db_i6_delete():
    q = "Write SQL to <strong>delete</strong> the pupil with ID 99."
    s = "<pre>DELETE FROM Pupil WHERE PupilID = 99;</pre>"
    return q, s, "DELETE FROM … WHERE … — WHERE avoids deleting all rows.", 2


def _db_i7_consistency():
    q = "How do relational databases help <strong>data consistency</strong>?"
    s = (
        "Each fact is stored <strong>once</strong> in the correct table; linked by keys. "
        "Updating the teacher in <code>Class</code> updates it for all linked pupils automatically."
    )
    return q, s, "Less duplication = fewer conflicting copies.", 2


def _db_i8_two_tables():
    q = (
        "Tables: <code>Pupil(PupilID, ClassID, Surname)</code> and "
        "<code>Class(ClassID, ClassName)</code>. Write SQL to list "
        "<strong>surnames</strong> and <strong>class names</strong>."
    )
    s = (
        "<pre>SELECT Pupil.Surname, Class.ClassName\n"
        "FROM Pupil, Class\n"
        "WHERE Pupil.ClassID = Class.ClassID;</pre>"
    )
    return q, s, "Link tables with WHERE on matching keys.", 4


def _db_i9_count():
    q = "Write SQL to count how many pupils are in <code>Pupil</code>."
    s = "<pre>SELECT COUNT(*) FROM Pupil;</pre>"
    return q, s, "COUNT(*) counts rows.", 2


def _db_i10_validation():
    q = "Why should a <strong>primary key</strong> never be empty (NULL)?"
    s = (
        "Every record must be <strong>uniquely identifiable</strong>; NULL would mean "
        "you cannot reliably link or update that row."
    )
    return q, s, "PK must be unique and present.", 2


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _db_d1_flat_vs_relational():
    q = "Give <strong>two disadvantages</strong> of storing all school data in one spreadsheet column per fact duplicated."
    s = (
        "<strong>Redundancy</strong> — class teacher name repeated for every pupil. "
        "<strong>Inconsistency</strong> — change one cell, others may stay wrong."
    )
    return q, s, "Relational design splits data into linked tables.", 3


def _db_d2_order_desc():
    q = "Write SQL: top 5 highest <code>Score</code> values from <code>Grade</code>, highest first."
    s = (
        "<pre>SELECT Score FROM Grade ORDER BY Score DESC LIMIT 5;</pre>"
        " (LIMIT optional at GCSE — check paper wording.)"
    )
    return q, s, "ORDER BY … DESC = largest first.", 3


def _db_d3_update_multiple():
    q = "Write SQL to set <code>Teacher</code> to <code>'Ms Lee'</code> for <code>ClassID</code> 7."
    s = "<pre>UPDATE Class SET Teacher = 'Ms Lee' WHERE ClassID = 7;</pre>"
    return q, s, "One UPDATE fixes all records matching WHERE.", 3


def _db_d4_delete_care():
    q = "Why is <code>DELETE FROM Pupil;</code> without <code>WHERE</code> dangerous?"
    s = (
        "It deletes <strong>every record</strong> in the table. Always use "
        "<code>WHERE</code> unless you truly intend to remove all rows."
    )
    return q, s, "Missing WHERE = all rows affected.", 2


def _db_d5_trace_query():
    q = (
        "What does this return?<br>"
        "<code>SELECT FirstName FROM Pupil WHERE YearGroup &gt; 10 ORDER BY FirstName ASC;</code>"
    )
    s = (
        "<strong>First names</strong> of pupils in years <strong>11 and above</strong>, "
        "sorted A→Z by first name."
    )
    return q, s, "Read SELECT, FROM (implied Pupil), WHERE, ORDER BY in order.", 3


def _db_d6_fk_integrity():
    q = "A pupil has <code>ClassID = 99</code> but no class 99 exists. What problem is this?"
    s = (
        "<strong>Referential integrity</strong> failure — foreign key points to a "
        "non-existent primary key; the link is invalid."
    )
    return q, s, "FK must match an existing PK.", 3


def _db_d7_insert_columns():
    q = "Why list column names in <code>INSERT INTO Pupil (FirstName, YearGroup) VALUES (...)</code>?"
    s = (
        "You control <strong>which fields</strong> receive values; other columns can use "
        "defaults or NULL. Order of values must match column list."
    )
    return q, s, "Column list maps to VALUES list.", 3


def _db_d8_entity_diagram():
    q = "Explain how an <strong>entity-relationship diagram (ERD)</strong> helps before creating tables."
    s = (
        "Shows <strong>entities</strong> (tables), <strong>attributes</strong> (fields), and "
        "<strong>relationships</strong> (keys) — plan structure before writing SQL."
    )
    return q, s, "Design first, implement in SQL second.", 3


def _db_d9_sql_injection_link():
    q = "How does poor SQL input handling relate to <strong>SQL injection</strong>?"
    s = (
        "If user input is pasted straight into a query, attackers can add malicious SQL "
        "(e.g. <code>' OR '1'='1</code>). Use <strong>parameterised queries</strong> and validation."
    )
    return q, s, "Never trust raw user input in SQL strings.", 3


def _db_d10_exam_reading():
    q = (
        "Table <code>Book(BookID, Title, AuthorID)</code> and "
        "<code>Author(AuthorID, Name)</code>. Write SQL to list "
        "<strong>book titles</strong> by author <strong>'Rowling'</strong>."
    )
    s = (
        "<pre>SELECT Book.Title\n"
        "FROM Book, Author\n"
        "WHERE Book.AuthorID = Author.AuthorID\n"
        "AND Author.Name = 'Rowling';</pre>"
    )
    return q, s, "AQA: max two tables in one query — link with WHERE.", 4


def _db_d11_count_group():
    q = (
        "Table <code>Pupil(PupilID, FirstName, YearGroup)</code>. "
        "Write SQL to show how many pupils are in <strong>each</strong> year group."
    )
    s = (
        "<pre>SELECT YearGroup, COUNT(PupilID)\n"
        "FROM Pupil\n"
        "GROUP BY YearGroup;</pre>"
    )
    return q, s, "COUNT with GROUP BY — one row per year group.", 4


def _db_d12_update_scenario():
    q = (
        "All pupils in <code>YearGroup 11</code> move up to year <code>12</code>. "
        "Write the <code>UPDATE</code> statement."
    )
    s = (
        "<pre>UPDATE Pupil\n"
        "SET YearGroup = 12\n"
        "WHERE YearGroup = 11;</pre>"
    )
    return q, s, "UPDATE … SET … WHERE limits which rows change.", 3


# ── Multi-part difficult questions (a, b, c) ──────────────────────────────────

def _db_d13_multipart_query_writing():
    q = (
        "A table called <code>Member</code> stores: <code>MemberID</code>, "
        "<code>FirstName</code>, <code>Surname</code>, <code>Town</code>, "
        "<code>Age</code>.<br><br>"
        "<strong>a)</strong> Write an SQL query to display the <code>FirstName</code> and "
        "<code>Surname</code> of all members who live in <code>'Leeds'</code>. [2]<br>"
        "<strong>b)</strong> Write an SQL query to display <strong>all details</strong> of "
        "members aged <strong>18 or over</strong>, sorted by <code>Surname</code> in "
        "ascending order. [3]<br>"
        "<strong>c)</strong> State which field is the most suitable <strong>primary key</strong> "
        "and explain why. [2]"
    )
    s = (
        "<strong>a)</strong>"
        "<pre>SELECT FirstName, Surname\n"
        "FROM Member\n"
        "WHERE Town = 'Leeds';</pre>"
        "<strong>b)</strong>"
        "<pre>SELECT *\n"
        "FROM Member\n"
        "WHERE Age &gt;= 18\n"
        "ORDER BY Surname ASC;</pre>"
        "<strong>c)</strong> <code>MemberID</code>, because it is "
        "<strong>unique</strong> for every member, so it can identify each record with no "
        "duplicates (names or towns could be shared by different members)."
    )
    return q, s, "SELECT fields FROM table WHERE condition ORDER BY field; PK must be unique.", 7


def _db_d14_multipart_relational_design():
    q = (
        "A school currently stores all data in a <strong>single flat-file table</strong> that "
        "repeats the teacher's name on every pupil's row.<br><br>"
        "<strong>a)</strong> State <strong>one</strong> problem caused by storing the data "
        "this way. [1]<br>"
        "<strong>b)</strong> The school splits the data into a <code>Pupil</code> table and a "
        "<code>Teacher</code> table. Explain how a <strong>foreign key</strong> is used to "
        "link them. [2]<br>"
        "<strong>c)</strong> Give <strong>two</strong> benefits of using a relational "
        "database instead of the flat file. [2]"
    )
    s = (
        "<strong>a)</strong> Any one: <strong>data redundancy</strong> (the same teacher "
        "name is stored many times, wasting space); risk of <strong>inconsistency</strong> "
        "(if a teacher's name is updated in one row but not others).<br><br>"
        "<strong>b)</strong> The <code>Pupil</code> table stores a "
        "<strong>foreign key</strong> (e.g. <code>TeacherID</code>) that matches the "
        "<strong>primary key</strong> of the <code>Teacher</code> table. This links each "
        "pupil to one teacher without repeating the teacher's full details.<br><br>"
        "<strong>c)</strong> Any two: <strong>less data redundancy</strong>; "
        "<strong>easier to update</strong> data consistently in one place; "
        "<strong>better data integrity</strong>; data can be queried and combined "
        "flexibly."
    )
    return q, s, "Flat files repeat data; relational design links tables with keys.", 5


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (17)
# ══════════════════════════════════════════════════════════════════════════════

_DB_MCQ_BANK = [
    {"q": "A row in a database table is called a:",
     "opts": ["A  field", "B  record", "C  primary key", "D  query"],
     "ans": "B", "marks": 1,
     "sol": "One <strong>record</strong> = one row. Answer: B",
     "hint": "Row = record."},
    {"q": "A primary key must be:",
     "opts": ["A  the same for every record", "B  unique for each record",
              "C  always text", "D  optional"],
     "ans": "B", "marks": 1,
     "sol": "<strong>Unique</strong> per record. Answer: B",
     "hint": "Identifies each row."},
    {"q": "SELECT * FROM Pupil means:",
     "opts": ["A  delete all pupils", "B  show all columns from Pupil",
              "C  insert a pupil", "D  update pupils"],
     "ans": "B", "marks": 2,
     "sol": "<code>*</code> = all columns. Answer: B",
     "hint": "SELECT reads data."},
    {"q": "WHERE YearGroup = 10 filters:",
     "opts": ["A  columns", "B  rows matching the condition",
              "C  tables", "D  databases"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Filters rows</strong>. Answer: B",
     "hint": "WHERE = row filter."},
    {"q": "ORDER BY Score DESC sorts:",
     "opts": ["A  lowest scores first", "B  highest scores first",
              "C  alphabetically A–Z", "D  random order"],
     "ans": "B", "marks": 2,
     "sol": "<strong>DESC</strong> = descending. Answer: B",
     "hint": "DESC = high to low."},
    {"q": "A foreign key:",
     "opts": ["A  links to a primary key in another table",
              "B  must be text only", "C  deletes records",
              "D  encrypts data"],
     "ans": "A", "marks": 2,
     "sol": "Links tables together. Answer: A",
     "hint": "FK = link between tables."},
    {"q": "Data redundancy means:",
     "opts": ["A  data stored only once", "B  duplicate data in multiple places",
              "C  no keys used", "D  encrypted data"],
     "ans": "B", "marks": 2,
     "sol": "<strong>Duplicate</strong> storage. Answer: B",
     "hint": "Redundant = repeated."},
    {"q": "INSERT INTO is used to:",
     "opts": ["A  add new records", "B  remove records",
              "C  sort records", "D  rename tables"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Add</strong> new rows. Answer: A",
     "hint": "INSERT = add."},
    {"q": "UPDATE … SET … WHERE is used to:",
     "opts": ["A  change existing data", "B  create tables",
              "C  list databases", "D  only delete data"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Modify</strong> existing rows. Answer: A",
     "hint": "UPDATE = edit."},
    {"q": "DELETE FROM Pupil WHERE PupilID = 3:",
     "opts": ["A  deletes pupil 3 only", "B  deletes all pupils",
              "C  shows pupil 3", "D  adds pupil 3"],
     "ans": "A", "marks": 2,
     "sol": "<strong>WHERE</strong> limits delete. Answer: A",
     "hint": "WHERE targets one row."},
    {"q": "Relational databases reduce inconsistency by:",
     "opts": ["A  storing everything in one cell",
              "B  linking related data in separate tables",
              "C  removing primary keys", "D  using only one table"],
     "ans": "B", "marks": 2,
     "sol": "Normalised <strong>linked tables</strong>. Answer: B",
     "hint": "Split data logically."},
    {"q": "FROM Pupil in a query specifies:",
     "opts": ["A  the table", "B  the sort order", "C  the primary key only",
              "D  the password"],
     "ans": "A", "marks": 1,
     "sol": "Names the <strong>table</strong>. Answer: A",
     "hint": "FROM = table name."},
    {"q": "INTEGER is a suitable type for:",
     "opts": ["A  a pupil's year group number", "B  a long essay",
              "C  a photo file", "D  today's date only"],
     "ans": "A", "marks": 2,
     "sol": "Whole numbers → <strong>INTEGER</strong>. Answer: A",
     "hint": "Match type to data."},
    {"q": "OCR GCSE SQL for searching mainly requires:",
     "opts": ["A  SELECT, FROM, WHERE only", "B  only DELETE",
              "C  only CREATE TABLE", "D  HTML tags"],
     "ans": "A", "marks": 2,
     "sol": "OCR focuses on <strong>querying</strong>. Answer: A",
     "hint": "Read data commands."},
    {"q": "AQA allows SQL to modify data using:",
     "opts": ["A  INSERT, UPDATE, DELETE", "B  only SELECT",
              "C  only PRINT", "D  only JOIN"],
     "ans": "A", "marks": 2,
     "sol": "Full <strong>CRUD</strong> on AQA. Answer: A",
     "hint": "Add, change, remove."},
    {"q": "COUNT(*) in a SELECT query:",
     "opts": ["A  counts rows matching the query", "B  deletes duplicate tables",
              "C  sorts columns alphabetically", "D  encrypts the database"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Counts records</strong> returned. Answer: A",
     "hint": "Aggregate function."},
    {"q": "VARCHAR is suitable for:",
     "opts": ["A  a pupil's first name", "B  a whole photo file",
              "C  the number of cores in a CPU", "D  today's date only"],
     "ans": "A", "marks": 2,
     "sol": "<strong>Variable-length text</strong>. Answer: A",
     "hint": "Text field type."},
    {"q": "A column in a database table is also called a:",
     "opts": ["A  record", "B  field", "C  query", "D  report"],
     "ans": "B", "marks": 1,
     "sol": "One <strong>field</strong> = one column. Answer: B",
     "hint": "Row = record, column = field."},
    {"q": "SELECT Name, Score FROM Pupil returns:",
     "opts": ["A  only the Name and Score columns", "B  every column in the table",
              "C  no data", "D  only primary keys"],
     "ans": "A", "marks": 2,
     "sol": "Lists <strong>named columns only</strong>. Answer: A",
     "hint": "Contrast with SELECT *."},
    {"q": "A composite primary key means:",
     "opts": ["A  one column identifies each record alone",
              "B  two or more columns together uniquely identify a record",
              "C  no key is used", "D  every field is text"],
     "ans": "B", "marks": 2,
     "sol": "Combination of fields is <strong>unique</strong>. Answer: B",
     "hint": "Common in link tables."},
    {"q": "Flat-file storage compared with a relational database often causes:",
     "opts": ["A  less duplication", "B  more data redundancy and inconsistency",
              "C  automatic encryption", "D  faster networks"],
     "ans": "B", "marks": 2,
     "sol": "Repeating data in one file → <strong>redundancy</strong>. Answer: B",
     "hint": "Same customer address stored many times."},
    {"q": "SELECT AVG(Score) FROM Pupil calculates:",
     "opts": ["A  the average score", "B  the highest score only",
              "C  the number of tables", "D  the primary key"],
     "ans": "A", "marks": 2,
     "sol": "<strong>AVG</strong> returns the mean value. Answer: A",
     "hint": "Another aggregate like COUNT and MAX."},
]


def db_sql_mcq():
    item = random.choice(_DB_MCQ_BANK)
    return item["q"], item["sol"], item["hint"], item["marks"], item["opts"], item["ans"]


# ══════════════════════════════════════════════════════════════════════════════
# VARIANTS & MAIN ENTRY
# ══════════════════════════════════════════════════════════════════════════════

_FOUNDATIONAL = [
    _db_f1_database, _db_f2_relational, _db_f3_table_record_field,
    _db_f4_primary_key, _db_f5_foreign_key, _db_f6_redundancy,
    _db_f7_select, _db_f8_from, _db_f9_where, _db_f10_data_type,
]

_INTERMEDIATE = [
    _db_i1_select_star, _db_i2_where_example, _db_i3_order_by,
    _db_i4_insert, _db_i5_update, _db_i6_delete, _db_i7_consistency,
    _db_i8_two_tables, _db_i9_count, _db_i10_validation,
]

_DIFFICULT = [
    _db_d1_flat_vs_relational, _db_d2_order_desc, _db_d3_update_multiple,
    _db_d4_delete_care, _db_d5_trace_query, _db_d6_fk_integrity,
    _db_d7_insert_columns, _db_d8_entity_diagram, _db_d9_sql_injection_link,
    _db_d10_exam_reading, _db_d11_count_group, _db_d12_update_scenario,
    _db_d13_multipart_query_writing, _db_d14_multipart_relational_design,
]


def gcse_db_sql_variants(difficulty, mode="practice"):
    if mode == "mcq":
        return [db_sql_mcq] * 10

    pools = {
        "foundational": _FOUNDATIONAL,
        "intermediate": _INTERMEDIATE,
        "difficult": _DIFFICULT,
    }
    if difficulty not in pools:
        return random.sample(_FOUNDATIONAL + _INTERMEDIATE + _DIFFICULT, 10)

    pool = pools[difficulty]
    return random.sample(pool, len(pool))


def gcse_db_sql(difficulty, mode, variant_name=None):
    if mode == "mcq":
        q_mcq, s_mcq, hint_mcq, marks_mcq, opts_mcq, correct_mcq = db_sql_mcq()
        return make_problem(
            q_mcq, s_mcq, hint_mcq, difficulty, marks_mcq,
            "gcse", "cs", "db_sql",
            options=opts_mcq, correct_answer=correct_mcq,
        )

    variants = gcse_db_sql_variants(difficulty, mode)
    variant = pick_named_variant(variants, variant_name)

    q, s, hint, marks = variant()
    return make_problem(
        q, s, hint, difficulty, marks,
        "gcse", "cs", "db_sql",
    )
