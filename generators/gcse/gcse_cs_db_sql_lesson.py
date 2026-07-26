"""
GCSE Computer Science – Relational Databases & SQL
10 foundational · 10 intermediate · 10 difficult · 15 MCQ
Graded practice variants return (question, solution, hint, marks, raw).
SQL-writing variants use text keyword grading (required SQL clauses/values).
"""
import random
from generators.shared.utils import (
    make_problem,
    graded_answer_number_fields,
    graded_answer_sql,
    problem_extra_from_graded_answer,
    proof_steps_answer,
)
from generators.shared.variant_utils import pick_named_variant


def _db_problem_from_output(out, difficulty):
    q, s, hint, marks = out[:4]
    extra = {}
    if len(out) >= 5:
        raw = out[4]
        if isinstance(raw, dict) and raw.get('type') == 'mcq':
            return make_problem(
                q, s, hint, difficulty, marks, 'gcse', 'cs', 'db_sql',
                options=raw['options'],
                correct_answer=raw['correct'],
            )
        if isinstance(raw, dict):
            extra = problem_extra_from_graded_answer(raw)
    return make_problem(
        q, s, hint, difficulty, marks, 'gcse', 'cs', 'db_sql', **extra
    )


def _db_mcq_payload(correct_variants, distractor_groups):
    """Four-option practice MCQ; picks one phrasing per answer and shuffles."""
    variants = correct_variants if isinstance(correct_variants, (tuple, list)) else (correct_variants,)
    groups = [
        (group,) if isinstance(group, str) else tuple(group)
        for group in distractor_groups[:3]
    ]
    correct_text = random.choice(variants)
    max_distractor_len = max(len(max(g, key=len)) for g in groups) if groups else 0
    if len(correct_text) > max_distractor_len:
        shorter = [v for v in variants if len(v) <= max_distractor_len]
        if shorter:
            correct_text = random.choice(shorter)
    distractors = []
    for group in groups:
        if random.random() < 0.55:
            distractors.append(max(group, key=len))
        else:
            distractors.append(random.choice(group))
    if distractors and len(correct_text) > max(len(d) for d in distractors):
        gi = random.randrange(len(groups))
        distractors[gi] = max(groups[gi], key=len)
    pool = [correct_text] + distractors
    random.shuffle(pool)
    letters = 'ABCD'
    correct_letter = letters[pool.index(correct_text)]
    options = [f'{letters[i]}  {pool[i]}' for i in range(len(pool))]
    return {'type': 'mcq', 'options': options, 'correct': correct_letter}


def _db_mcq_options(correct_variants, distractor_groups):
    """Build shuffled MCQ options for bank items (returns opts list + correct letter)."""
    payload = _db_mcq_payload(correct_variants, distractor_groups)
    return payload['options'], payload['correct']


def _db_pick_from_bank(correct_texts, distractor_texts, pick_count, *, format_hint=None):
    """Shuffled option bank: pick exactly ``pick_count`` correct statements."""
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    return proof_steps_answer(
        correct_ids,
        bank,
        pick_count=pick_count,
        format_hint=format_hint,
    )


def _db_pick_field(correct_texts, distractor_texts, pick_count):
    """Inline pick-N field for ``number_fields`` (returns raw, bank, count)."""
    correct_ids = tuple(f'c{i + 1}' for i in range(len(correct_texts)))
    bank = [{'id': cid, 'text': text} for cid, text in zip(correct_ids, correct_texts)]
    for i, text in enumerate(distractor_texts):
        bank.append({'id': f'd{i + 1}', 'text': text})
    random.shuffle(bank)
    raw = f"pick|{pick_count}|{'|'.join(correct_ids)}"
    return raw, bank, pick_count


def _db_sql(query, *, lines=3):
    """Exact SQL grading payload — ``lines`` sets the textarea height (1 or 3)."""
    return graded_answer_sql(query, lines=lines)


# ══════════════════════════════════════════════════════════════════════════════
# FOUNDATIONAL (10)
# ══════════════════════════════════════════════════════════════════════════════

def _db_f1_database():
    q = "What is a <strong>database</strong>? Select one correct answer."
    s = (
        "An organised collection of <strong>structured data</strong> stored electronically "
        "so it can be searched, updated and managed efficiently."
    )
    return q, s, "Think: school pupil records, shop stock.", 1, _db_mcq_payload(
        (
            'Structured electronic data that can be searched and updated',
            'An organised collection of structured data stored electronically for efficient management',
            'An organised collection of structured data stored electronically so it can be searched, updated and managed efficiently',
        ),
        (
            ('A programming language for websites', 'A programming language used only to write websites'),
            ('A type of network cable', 'A type of cable used to connect computers on a network'),
            (
                'An unstructured spreadsheet with no search features',
                'A single spreadsheet file with no structure or search features',
            ),
        ),
    )


def _db_f2_relational():
    q = "What is a <strong>relational database</strong>? Select one correct answer."
    s = (
        "Data is stored in <strong>related tables</strong> (rows and columns) linked by "
        "<strong>keys</strong>, rather than one giant flat file."
    )
    return q, s, "Tables + relationships.", 2, _db_mcq_payload(
        (
            'Data in related tables linked by keys',
            'Data stored in related tables linked by keys instead of one flat file',
            'Data is stored in related tables linked by keys, rather than one giant flat file',
        ),
        (
            ('One unstructured text file', 'Data stored in a single unstructured text file with no links'),
            ('A database with only one table allowed', 'A database that is only allowed to contain one table'),
            ('Records stored as image files', 'A database that stores every record as an image file'),
        ),
    )


def _db_f3_table_record_field():
    q = (
        "Which of these correctly define <strong>table</strong>, <strong>record</strong>, "
        "and <strong>field</strong>? Select the three correct statements."
    )
    s = (
        "<strong>Table</strong> — collection of data about one type of thing (e.g. Pupil). "
        "<strong>Record</strong> — one row (one pupil). "
        "<strong>Field</strong> — one column (e.g. Surname)."
    )
    return q, s, "Table = sheet; record = row; field = column.", 2, _db_pick_from_bank(
        (
            'A table is a collection of data about one type of thing (e.g. Pupil)',
            'A record is one row in a table (e.g. one pupil)',
            'A field is one column in a table (e.g. Surname)',
        ),
        (
            'A record is the same thing as an entire database',
            'A field always contains several values in one cell',
            'A table can only ever contain a single record',
        ),
        3,
        format_hint='Select the three correct definitions',
    )


def _db_f4_primary_key():
    q = "What is a <strong>primary key</strong>? Select one correct answer."
    s = (
        "A field that <strong>uniquely identifies</strong> each record in a table "
        "(e.g. PupilID). No two rows share the same value."
    )
    return q, s, "Unique ID for each row.", 2, _db_mcq_payload(
        (
            'A field that uniquely identifies each record in a table',
            'A field that uniquely identifies each row — no duplicates allowed',
            'A field that uniquely identifies each record in a table — no two rows share the same value',
        ),
        (
            ('A field storing login passwords', 'A field that stores the password used to log into the database'),
            ('A field with the same value in every row', 'A field that must contain the same value in every row'),
            (
                'A field linking to another table\u2019s primary key',
                'A field that links to another table\u2019s primary key',
            ),
        ),
    )


def _db_f5_foreign_key():
    q = "What is a <strong>foreign key</strong>? Select one correct answer."
    s = (
        "A field that <strong>links to the primary key</strong> in another table "
        "(e.g. ClassID in Pupil table links to Class table)."
    )
    return q, s, "Creates a relationship between tables.", 2, _db_mcq_payload(
        (
            'A field linking to a primary key in another table',
            'A field that links to the primary key in another table',
            'A field that references the primary key of a row in a different table to create a link',
        ),
        (
            (
                'A field uniquely identifying its own table\u2019s records',
                'A field that uniquely identifies records in its own table',
            ),
            ('A field that encrypts data automatically', 'A field that encrypts sensitive data automatically'),
            ('The first column in every table', 'A field that is always the first column in a table'),
        ),
    )


def _db_f6_redundancy():
    q = "What is <strong>data redundancy</strong>? Select one correct answer."
    s = (
        "The same data stored <strong>more than once</strong> in different places, "
        "which can cause inconsistency when one copy is updated and another is not."
    )
    return q, s, "Duplicate data = redundancy.", 2, _db_mcq_payload(
        (
            'The same data stored more than once',
            'Duplicate data stored in multiple places in a database',
            'The same data stored more than once in different places',
        ),
        (
            ('Data permanently deleted from a table', 'Data that has been permanently deleted from a table'),
            ('A field that must never be empty', 'A field that is never allowed to be empty'),
            (
                'Data linked by a foreign key',
                'Data stored using a foreign key relationship',
            ),
        ),
    )


def _db_f7_select():
    q = "What does <code>SELECT</code> do in SQL? Select one correct answer."
    s = (
        "<code>SELECT</code> chooses <strong>which columns</strong> to return from a query "
        "(e.g. <code>SELECT FirstName, Surname</code>)."
    )
    return q, s, "SELECT = which fields to show.", 1, _db_mcq_payload(
        (
            'Chooses which columns to return',
            'Selects which columns appear in the query results',
            'Chooses which columns to return from a query',
        ),
        (
            ('Deletes rows matching a condition', 'Deletes rows that match a condition'),
            ('Names the table to read from', 'Names the table the query reads from'),
            ('Sorts returned rows into order', 'Sorts the returned rows into an order'),
        ),
    )


def _db_f8_from():
    q = "What does <code>FROM</code> do in SQL? Select one correct answer."
    s = (
        "<code>FROM</code> names the <strong>table</strong> to read data from "
        "(e.g. <code>FROM Pupil</code>)."
    )
    return q, s, "FROM = which table.", 1, _db_mcq_payload(
        (
            'Names the table to read from',
            'Names the table the query reads data from',
            'Specifies which table in the database the query reads data from',
        ),
        (
            ('Chooses which columns are returned', 'Chooses which columns are returned'),
            ('Filters rows by a condition', 'Filters out rows that do not match a condition'),
            ('Sorts rows ascending or descending', 'Sorts rows into ascending or descending order'),
        ),
    )


def _db_f9_where():
    q = "What does <code>WHERE</code> do in SQL? Select one correct answer."
    s = (
        "<code>WHERE</code> <strong>filters</strong> records — only rows matching the "
        "condition are returned (e.g. <code>WHERE YearGroup = 11</code>)."
    )
    return q, s, "WHERE = filter rows.", 2, _db_mcq_payload(
        (
            'Filters rows by a condition',
            'Returns only rows that match the condition',
            'Filters records so only rows matching the condition are returned',
        ),
        (
            ('Names which table to read from', 'Names which table the query reads from'),
            ('Chooses which columns to display', 'Chooses which columns are displayed'),
            ('Sorts results alphabetically', 'Sorts the results alphabetically'),
        ),
    )


def _db_f10_data_type():
    q = "Which <strong>two</strong> of these are valid data types for database fields?"
    s = (
        "Examples: <strong>INTEGER</strong> (whole numbers), <strong>TEXT/VARCHAR</strong> "
        "(strings), <strong>BOOLEAN</strong>, <strong>REAL</strong> (decimals), <strong>DATE</strong>."
    )
    return q, s, "Match type to the data stored.", 2, _db_pick_from_bank(
        (
            'INTEGER — for whole numbers',
            'TEXT / VARCHAR — for strings of characters',
            'BOOLEAN — for true/false values',
            'DATE — for calendar dates',
        ),
        (
            'PRIMARY — for values that must be unique',
            'RELATION — for linking two tables together',
            'QUERY — for storing a saved SQL statement',
        ),
        2,
        format_hint='Select two valid data types',
    )


# ══════════════════════════════════════════════════════════════════════════════
# INTERMEDIATE (10)
# ══════════════════════════════════════════════════════════════════════════════

def _db_i1_select_star():
    q = "Write SQL to list <strong>all columns</strong> from table <code>Pupil</code>."
    s = "<pre>SELECT * FROM Pupil;</pre>"
    return q, s, "<code>*</code> means all fields.", 2, _db_sql('SELECT * FROM Pupil', lines=1)


def _db_i2_where_example():
    q = "Write SQL to show surnames of pupils in <strong>Year 11</strong> from <code>Pupil</code>."
    s = (
        "<pre>SELECT Surname FROM Pupil WHERE YearGroup = 11;</pre>"
    )
    return q, s, "SELECT columns FROM table WHERE condition.", 2, _db_sql(
        'SELECT Surname FROM Pupil WHERE YearGroup = 11',
        lines=1,
    )


def _db_i3_order_by():
    q = "What does <code>ORDER BY Surname ASC</code> do? Select one correct answer."
    s = (
        "Sorts results <strong>alphabetically by Surname</strong> ascending (A→Z). "
        "<code>DESC</code> would sort descending (Z→A)."
    )
    return q, s, "ORDER BY = sort results.", 2, _db_mcq_payload(
        (
            'Sorts by Surname ascending (A to Z)',
            'Sorts results by Surname in ascending order',
            'Sorts results alphabetically by Surname, ascending (A to Z)',
        ),
        (
            ('Filters out empty Surname values', 'Filters out rows where Surname is empty'),
            (
                'Sorts by Surname descending (Z to A)',
                'Sorts results by Surname, descending (Z to A)',
                'Sorts results by Surname in descending order from Z down to A',
            ),
            (
                'Groups rows with the same Surname',
                'Groups rows that share the same Surname',
                'Combines all rows that share the same Surname into a single grouped result row',
            ),
        ),
    )


def _db_i4_insert():
    q = "Write SQL to <strong>insert</strong> a new pupil: ID 42, name Ali, year 10."
    s = (
        "<pre>INSERT INTO Pupil (PupilID, FirstName, YearGroup)\n"
        "VALUES (42, 'Ali', 10);</pre>"
    )
    return q, s, "INSERT INTO … VALUES …", 3, _db_sql(
        "INSERT INTO Pupil (PupilID, FirstName, YearGroup) VALUES (42, 'Ali', 10)",
    )


def _db_i5_update():
    q = "Write SQL to change pupil <strong>42</strong> to Year <strong>11</strong>."
    s = (
        "<pre>UPDATE Pupil SET YearGroup = 11 WHERE PupilID = 42;</pre>"
    )
    return q, s, "UPDATE … SET … WHERE …", 3, _db_sql(
        'UPDATE Pupil SET YearGroup = 11 WHERE PupilID = 42',
    )


def _db_i6_delete():
    q = "Write SQL to <strong>delete</strong> the pupil with ID 99."
    s = "<pre>DELETE FROM Pupil WHERE PupilID = 99;</pre>"
    return q, s, "DELETE FROM … WHERE … — WHERE avoids deleting all rows.", 2, _db_sql(
        'DELETE FROM Pupil WHERE PupilID = 99',
        lines=1,
    )


def _db_i7_consistency():
    q = "How do relational databases help <strong>data consistency</strong>? Select one correct answer."
    s = (
        "Each fact is stored <strong>once</strong> in the correct table; linked by keys. "
        "Updating the teacher in <code>Class</code> updates it for all linked pupils automatically."
    )
    return q, s, "Less duplication = fewer conflicting copies.", 2, _db_mcq_payload(
        (
            'Each fact is stored once and linked by keys',
            'Facts are stored once in the right table and linked by keys',
            'Each fact is stored once and linked by keys, so updating it in one place updates it everywhere it is used',
        ),
        (
            (
                'Every table copies all other tables completely',
                'Every table stores a full copy of every other table',
                'Every table stores a complete duplicate of all data from every other table in the database',
            ),
            (
                'UPDATE statements are never allowed',
                'Consistency is guaranteed by never allowing UPDATE statements',
                'Data stays consistent because UPDATE and DELETE statements are blocked entirely',
            ),
            (
                'Data is duplicated to speed up queries',
                'Data is duplicated across tables to make queries faster',
                'Duplicating data across many tables makes every query run faster automatically',
            ),
        ),
    )


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
    return q, s, "Link tables with WHERE on matching keys.", 4, _db_sql(
        'SELECT Pupil.Surname, Class.ClassName FROM Pupil, Class '
        'WHERE Pupil.ClassID = Class.ClassID',
    )


def _db_i9_count():
    q = "Write SQL to count how many pupils are in <code>Pupil</code>."
    s = "<pre>SELECT COUNT(*) FROM Pupil;</pre>"
    return q, s, "COUNT(*) counts rows.", 2, _db_sql('SELECT COUNT(*) FROM Pupil', lines=1)


def _db_i10_validation():
    q = "Why should a <strong>primary key</strong> never be empty (NULL)? Select one correct answer."
    s = (
        "Every record must be <strong>uniquely identifiable</strong>; NULL would mean "
        "you cannot reliably link or update that row."
    )
    return q, s, "PK must be unique and present.", 2, _db_mcq_payload(
        (
            'NULL means a record cannot be uniquely identified',
            'Every record must be uniquely identifiable — NULL breaks that',
            'Every record must be uniquely identifiable, and NULL means it cannot be reliably linked or updated',
        ),
        (
            ('NULL deletes the whole record', 'NULL values automatically delete the whole record'),
            ('NULL makes queries run faster', 'A NULL primary key makes queries run faster'),
            (
                'Primary keys are only for sorting',
                'Primary keys are only used for sorting, so NULL has no effect',
                'A NULL primary key is acceptable because keys are only used to sort rows, not identify them',
            ),
        ),
    )


# ══════════════════════════════════════════════════════════════════════════════
# DIFFICULT (10)
# ══════════════════════════════════════════════════════════════════════════════

def _db_d1_flat_vs_relational():
    q = (
        "Give <strong>two</strong> disadvantages of storing all school data in one "
        "spreadsheet with facts duplicated on every row."
    )
    s = (
        "<strong>Redundancy</strong> — class teacher name repeated for every pupil. "
        "<strong>Inconsistency</strong> — change one cell, others may stay wrong."
    )
    return q, s, "Relational design splits data into linked tables.", 3, _db_pick_from_bank(
        (
            'Redundancy — the same fact (e.g. teacher name) is repeated on every row',
            'Inconsistency — updating one copy of a fact can leave other copies wrong',
        ),
        (
            'Spreadsheets automatically enforce referential integrity',
            'A single flat file always uses less storage than related tables',
            'Flat files make it impossible to search for data',
        ),
        2,
        format_hint='Select two disadvantages',
    )


def _db_d2_order_desc():
    q = "Write SQL: top 5 highest <code>Score</code> values from <code>Grade</code>, highest first."
    s = (
        "<pre>SELECT Score FROM Grade ORDER BY Score DESC LIMIT 5;</pre>"
        " (LIMIT optional at GCSE — check paper wording.)"
    )
    return q, s, "ORDER BY … DESC = largest first.", 3, _db_sql(
        'SELECT Score FROM Grade ORDER BY Score DESC LIMIT 5',
    )


def _db_d3_update_multiple():
    q = "Write SQL to set <code>Teacher</code> to <code>'Ms Lee'</code> for <code>ClassID</code> 7."
    s = "<pre>UPDATE Class SET Teacher = 'Ms Lee' WHERE ClassID = 7;</pre>"
    return q, s, "One UPDATE fixes all records matching WHERE.", 3, _db_sql(
        "UPDATE Class SET Teacher = 'Ms Lee' WHERE ClassID = 7",
    )


def _db_d4_delete_care():
    q = "Why is <code>DELETE FROM Pupil;</code> without <code>WHERE</code> dangerous? Select one correct answer."
    s = (
        "It deletes <strong>every record</strong> in the table. Always use "
        "<code>WHERE</code> unless you truly intend to remove all rows."
    )
    return q, s, "Missing WHERE = all rows affected.", 2, _db_mcq_payload(
        (
            'It deletes every row in the table',
            'It removes all records in the table, not just one',
            'It deletes every record in the table, not just the ones you meant to remove',
        ),
        (
            ('It deletes only the first record', 'It only deletes the first record in the table'),
            (
                'It asks for confirmation before deleting',
                'It asks for confirmation before deleting anything',
            ),
            (
                'It deletes the table structure but keeps data',
                'It deletes the table structure but keeps the data',
            ),
        ),
    )


def _db_d5_trace_query():
    q = (
        "What does this return?<br>"
        "<code>SELECT FirstName FROM Pupil WHERE YearGroup &gt; 10 ORDER BY FirstName ASC;</code>"
    )
    s = (
        "<strong>First names</strong> of pupils in years <strong>11 and above</strong>, "
        "sorted A→Z by first name."
    )
    return q, s, "Read SELECT, FROM (implied Pupil), WHERE, ORDER BY in order.", 3, _db_mcq_payload(
        (
            'First names for year 11+, sorted A to Z',
            'First names of pupils in years 11 and above, sorted A to Z',
            'First names of pupils in years 11 and above, sorted A to Z by first name',
        ),
        (
            (
                'All columns for year 10 or below',
                'Every column for pupils in year 10 or below, unsorted',
            ),
            (
                'First names for year 11+, sorted Z to A',
                'First names of pupils in years 11 and above, sorted Z to A',
            ),
            (
                'A count per year group',
                'A count of how many pupils are in each year group',
            ),
        ),
    )


def _db_d6_fk_integrity():
    q = "A pupil has <code>ClassID = 99</code> but no class 99 exists. What problem is this? Select one correct answer."
    s = (
        "<strong>Referential integrity</strong> failure — foreign key points to a "
        "non-existent primary key; the link is invalid."
    )
    return q, s, "FK must match an existing PK.", 3, _db_mcq_payload(
        (
            'Referential integrity failure — invalid foreign key',
            'Referential integrity failure — the foreign key points to a missing row',
            'Referential integrity failure — the foreign key points to a primary key that does not exist',
        ),
        (
            ('Data redundancy in the Pupil table', 'Data redundancy — the class information is duplicated'),
            ('A primary key violation in Pupil', 'A primary key violation in the Pupil table'),
            (
                'A data type mismatch between keys',
                'A data type mismatch between ClassID and PupilID',
            ),
        ),
    )


def _db_d7_insert_columns():
    q = "Why list column names in <code>INSERT INTO Pupil (FirstName, YearGroup) VALUES (...)</code>? Select one correct answer."
    s = (
        "You control <strong>which fields</strong> receive values; other columns can use "
        "defaults or NULL. Order of values must match column list."
    )
    return q, s, "Column list maps to VALUES list.", 3, _db_mcq_payload(
        (
            'It controls which columns receive the values listed',
            'It sets values only for the named columns',
            'It controls which fields receive the listed values, leaving other columns as default/NULL',
        ),
        (
            (
                'Required syntax with no effect on columns',
                'It is required syntax with no effect on which columns are filled',
            ),
            ('It deletes unnamed columns', 'It deletes any columns not named in the list'),
            (
                'It renames columns to match VALUES',
                'It renames the columns listed to match the VALUES given',
            ),
        ),
    )


def _db_d8_entity_diagram():
    q = "How does an <strong>entity-relationship diagram (ERD)</strong> help before creating tables? Select one correct answer."
    s = (
        "Shows <strong>entities</strong> (tables), <strong>attributes</strong> (fields), and "
        "<strong>relationships</strong> (keys) — plan structure before writing SQL."
    )
    return q, s, "Design first, implement in SQL second.", 3, _db_mcq_payload(
        (
            'It shows entities, attributes and relationships before building tables',
            'It maps entities, attributes and relationships for planning table design',
            'It shows entities, attributes, and relationships so the structure can be planned before writing SQL',
        ),
        (
            (
                'It writes CREATE TABLE statements automatically',
                'It automatically writes the SQL CREATE TABLE statements',
            ),
            (
                'It removes the need for keys',
                'It replaces the need for primary and foreign keys',
            ),
            (
                'It only shows existing table data',
                'It only shows what data currently exists in the tables',
            ),
        ),
    )


def _db_d9_sql_injection_link():
    q = "How does poor SQL input handling relate to <strong>SQL injection</strong>? Select one correct answer."
    s = (
        "If user input is pasted straight into a query, attackers can add malicious SQL "
        "(e.g. <code>' OR '1'='1</code>). Use <strong>parameterised queries</strong> and validation."
    )
    return q, s, "Never trust raw user input in SQL strings.", 3, _db_mcq_payload(
        (
            'Raw input in queries lets attackers inject malicious SQL',
            'Pasting user input into queries allows SQL injection attacks',
            'If user input is pasted straight into a query, attackers can inject malicious SQL — use parameterised queries and validation',
        ),
        (
            (
                'Injection only affects databases with foreign keys',
                'SQL injection only affects databases that use foreign keys',
            ),
            (
                'Poor input handling only speeds up queries',
                'Poor input handling makes queries run faster but is otherwise harmless',
            ),
            (
                'SELECT prevents injection automatically',
                'SQL injection is prevented automatically by using SELECT instead of UPDATE',
            ),
        ),
    )


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
    return q, s, "AQA: max two tables in one query — link with WHERE.", 4, _db_sql(
        "SELECT Book.Title FROM Book, Author "
        "WHERE Book.AuthorID = Author.AuthorID AND Author.Name = 'Rowling'",
    )


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
    return q, s, "COUNT with GROUP BY — one row per year group.", 4, _db_sql(
        'SELECT YearGroup, COUNT(PupilID) FROM Pupil GROUP BY YearGroup',
    )


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
    return q, s, "UPDATE … SET … WHERE limits which rows change.", 3, _db_sql(
        'UPDATE Pupil SET YearGroup = 12 WHERE YearGroup = 11',
    )


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
        "<strong>c)</strong> Select which field is the most suitable <strong>primary key</strong>. [2]"
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
    pk_raw, pk_bank, pk_pick = _db_pick_field(
        (
            'MemberID — it is unique for every member',
        ),
        (
            'FirstName — every member has a different first name',
            'Surname — surnames are always unique in a database',
            'Town — the town field identifies each member uniquely',
        ),
        1,
    )
    return q, s, "SELECT fields FROM table WHERE condition ORDER BY field; PK must be unique.", 7, graded_answer_number_fields(
        (
            "SELECT FirstName, Surname FROM Member WHERE Town = 'Leeds'",
            "SELECT * FROM Member WHERE Age >= 18 ORDER BY Surname ASC",
            pk_raw,
        ),
        ('Leeds query', 'Adults sorted by surname', 'Primary key'),
        field_types=('sql', 'sql', 'pick'),
        field_options=(None, None, pk_bank),
        field_pick_counts=(None, None, pk_pick),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


def _db_d14_multipart_relational_design():
    q = (
        "A school currently stores all data in a <strong>single flat-file table</strong> that "
        "repeats the teacher's name on every pupil's row.<br><br>"
        "<strong>a)</strong> Select the <strong>one</strong> problem caused by storing the "
        "data this way. [1]<br>"
        "<strong>b)</strong> The school splits the data into a <code>Pupil</code> table and a "
        "<code>Teacher</code> table. Explain how a <strong>foreign key</strong> is used to "
        "link them. [2]<br>"
        "<strong>c)</strong> Select <strong>two</strong> benefits of using a relational "
        "database instead of the flat file. [2]"
    )
    s = (
        "<strong>a)</strong> <strong>Data redundancy</strong> — the same teacher "
        "name is stored many times, wasting space and risking inconsistency.<br><br>"
        "<strong>b)</strong> The <code>Pupil</code> table stores a "
        "<strong>foreign key</strong> (e.g. <code>TeacherID</code>) that matches the "
        "<strong>primary key</strong> of the <code>Teacher</code> table. This links each "
        "pupil to one teacher without repeating the teacher's full details.<br><br>"
        "<strong>c)</strong> Any two: <strong>less data redundancy</strong>; "
        "<strong>easier to update</strong> data consistently in one place; "
        "<strong>better data integrity</strong>; data can be queried and combined "
        "flexibly."
    )
    problem_raw, problem_bank, problem_pick = _db_pick_field(
        (
            'Data redundancy — the teacher\u2019s name is stored many times, wasting space',
        ),
        (
            'The database becomes automatically encrypted',
            'Queries run faster because there is only one table',
            'Primary keys are no longer needed',
        ),
        1,
    )
    benefits_raw, benefits_bank, benefits_pick = _db_pick_field(
        (
            'Less data redundancy',
            'Easier to update data consistently in one place',
            'Better data integrity',
            'Data can be queried and combined flexibly',
        ),
        (
            'Guarantees the database never needs backing up',
            'Removes the need for any primary keys',
            'Makes every query run without a WHERE clause',
        ),
        2,
    )
    return q, s, "Flat files repeat data; relational design links tables with keys.", 5, graded_answer_number_fields(
        (
            problem_raw,
            '1@foreign|key|teacherid|links|matches|primary',
            benefits_raw,
        ),
        ('Problem caused', 'How the foreign key links', 'Benefits of relational design'),
        field_types=('pick', 'text', 'pick'),
        field_options=(problem_bank, None, benefits_bank),
        field_pick_counts=(problem_pick, None, benefits_pick),
        row_sizes=(1, 1, 1),
        group_labels=('(a)', '(b)', '(c)'),
        inline_sections=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# MCQ BANK (17)
# ══════════════════════════════════════════════════════════════════════════════

_DB_MCQ_BANK = [
    {"q": "A row in a database table is called a:",
     "correct": ("row", "record", "a record (one row in the table)"),
     "wrong": (
         ("column", "field"),
         ("primary key", "a primary key value"),
         ("query", "an SQL query"),
     ),
     "marks": 1,
     "sol": "One <strong>record</strong> = one row. Answer: B",
     "hint": "Row = record."},
    {"q": "A primary key must be:",
     "correct": ("unique for each record", "unique per row", "different for every record in the table"),
     "wrong": (
         ("the same for every record", "identical in every row"),
         ("always text", "text only"),
         ("optional", "not required"),
     ),
     "marks": 1,
     "sol": "<strong>Unique</strong> per record. Answer: B",
     "hint": "Identifies each row."},
    {"q": "SELECT * FROM Pupil means:",
     "correct": (
         "show all columns from Pupil",
         "return every column from the Pupil table",
         "display all fields stored in the Pupil table",
     ),
     "wrong": (
         ("delete all pupils", "remove every pupil record", "delete every pupil row from the Pupil table permanently"),
         ("insert a pupil", "add a new pupil row", "insert a brand-new pupil record into the Pupil table"),
         ("update pupils", "change existing pupil data", "modify every column in every pupil record automatically"),
     ),
     "marks": 2,
     "sol": "<code>*</code> = all columns. Answer: B",
     "hint": "SELECT reads data."},
    {"q": "WHERE YearGroup = 10 filters:",
     "correct": (
         "rows matching the condition",
         "only rows where YearGroup is 10",
         "records that meet the YearGroup = 10 condition",
     ),
     "wrong": (
         ("columns", "which columns are shown", "which columns are displayed in the final result set"),
         ("tables", "which tables are used", "which tables in the database are being joined together"),
         ("databases", "which database is open", "which database server instance is currently connected"),
     ),
     "marks": 2,
     "sol": "<strong>Filters rows</strong>. Answer: B",
     "hint": "WHERE = row filter."},
    {"q": "ORDER BY Score DESC sorts:",
     "correct": (
         "highest scores first",
         "from highest to lowest score",
         "scores in descending order (largest first)",
     ),
     "wrong": (
         ("lowest scores first", "from lowest to highest score"),
         ("alphabetically A\u2013Z", "names in A to Z order"),
         ("random order", "rows in a random sequence"),
     ),
     "marks": 2,
     "sol": "<strong>DESC</strong> = descending. Answer: B",
     "hint": "DESC = high to low."},
    {"q": "A foreign key:",
     "correct": (
         "links to a primary key in another table",
         "references a primary key in a different table",
         "connects a row to a primary key value held in another table",
     ),
     "wrong": (
         ("must be text only", "can only store text values", "must always be a text or VARCHAR field and never a number"),
         ("deletes records", "removes rows when used", "automatically deletes related rows in other tables when updated"),
         ("encrypts data", "scrambles stored data automatically", "encrypts every value in the column so it cannot be read"),
     ),
     "marks": 2,
     "sol": "Links tables together. Answer: A",
     "hint": "FK = link between tables."},
    {"q": "Data redundancy means:",
     "correct": (
         "duplicate data in multiple places",
         "the same data stored more than once",
         "identical data repeated across different locations",
     ),
     "wrong": (
         ("data stored only once", "each fact kept in one place only", "every piece of data is stored in exactly one location with no copies"),
         ("no keys used", "tables without any keys", "tables that do not use primary keys or foreign keys at all"),
         ("encrypted data", "data that has been encrypted", "data that has been scrambled so only authorised users can read it"),
     ),
     "marks": 2,
     "sol": "<strong>Duplicate</strong> storage. Answer: B",
     "hint": "Redundant = repeated."},
    {"q": "INSERT INTO is used to:",
     "correct": ("add new records", "insert new rows", "add a new row to a table"),
     "wrong": (
         ("remove records", "delete existing rows"),
         ("sort records", "order rows by a column"),
         ("rename tables", "change a table\u2019s name"),
     ),
     "marks": 2,
     "sol": "<strong>Add</strong> new rows. Answer: A",
     "hint": "INSERT = add."},
    {"q": "UPDATE \u2026 SET \u2026 WHERE is used to:",
     "correct": (
         "change existing data",
         "modify values in existing rows",
         "update data in rows that match the WHERE condition",
     ),
     "wrong": (
         ("create tables", "define new tables"),
         ("list databases", "show all databases on a server"),
         ("only delete data", "remove rows without changing values"),
     ),
     "marks": 2,
     "sol": "<strong>Modify</strong> existing rows. Answer: A",
     "hint": "UPDATE = edit."},
    {"q": "DELETE FROM Pupil WHERE PupilID = 3:",
     "correct": (
         "deletes pupil 3 only",
         "removes the row where PupilID is 3",
         "deletes only the pupil record with PupilID = 3",
     ),
     "wrong": (
         ("deletes all pupils", "removes every row in Pupil"),
         ("shows pupil 3", "displays pupil 3\u2019s details"),
         ("adds pupil 3", "creates a new pupil with ID 3"),
     ),
     "marks": 2,
     "sol": "<strong>WHERE</strong> limits delete. Answer: A",
     "hint": "WHERE targets one row."},
    {"q": "Relational databases reduce inconsistency by:",
     "correct": (
         "linking related data in separate tables",
         "storing each fact once in linked tables",
         "splitting data into related tables connected by keys",
     ),
     "wrong": (
         ("storing everything in one cell", "putting all data in a single cell", "keeping every field from every table inside one spreadsheet cell"),
         ("removing primary keys", "not using primary keys", "deleting all primary keys so rows can be matched freely"),
         ("using only one table", "keeping all data in one table", "storing the entire database in a single table with no relationships"),
     ),
     "marks": 2,
     "sol": "Normalised <strong>linked tables</strong>. Answer: B",
     "hint": "Split data logically."},
    {"q": "FROM Pupil in a query specifies:",
     "correct": ("the table", "which table to read from", "the source table for the query"),
     "wrong": (
         ("the sort order", "how results are ordered"),
         ("the primary key only", "only the primary key column"),
         ("the password", "the database login password"),
     ),
     "marks": 1,
     "sol": "Names the <strong>table</strong>. Answer: A",
     "hint": "FROM = table name."},
    {"q": "INTEGER is a suitable type for:",
     "correct": (
         "a pupil\u2019s year group number",
         "whole numbers such as a year group",
         "a numeric whole-number field like YearGroup",
     ),
     "wrong": (
         ("a long essay", "a paragraph of text"),
         ("a photo file", "an image stored in the database"),
         ("today\u2019s date only", "calendar dates only"),
     ),
     "marks": 2,
     "sol": "Whole numbers \u2192 <strong>INTEGER</strong>. Answer: A",
     "hint": "Match type to data."},
    {"q": "OCR GCSE SQL for searching mainly requires:",
     "correct": (
         "SELECT, FROM, WHERE",
         "SELECT, FROM and WHERE clauses",
         "SELECT, FROM, WHERE only (basic querying commands)",
     ),
     "wrong": (
         ("only DELETE", "DELETE statements only"),
         ("only CREATE TABLE", "CREATE TABLE statements only"),
         ("HTML tags", "HTML markup tags"),
     ),
     "marks": 2,
     "sol": "OCR focuses on <strong>querying</strong>. Answer: A",
     "hint": "Read data commands."},
    {"q": "AQA allows SQL to modify data using:",
     "correct": (
         "INSERT, UPDATE, DELETE",
         "INSERT, UPDATE and DELETE statements",
         "INSERT, UPDATE, DELETE (add, change and remove data)",
     ),
     "wrong": (
         ("only SELECT", "SELECT queries only", "SELECT statements only — no INSERT, UPDATE or DELETE allowed"),
         ("only PRINT", "PRINT commands only", "PRINT commands only, which display messages but never change data"),
         ("only JOIN", "JOIN operations only", "JOIN operations only, which combine tables but never modify rows"),
     ),
     "marks": 2,
     "sol": "Full <strong>CRUD</strong> on AQA. Answer: A",
     "hint": "Add, change, remove."},
    {"q": "COUNT(*) in a SELECT query:",
     "correct": (
         "counts rows matching the query",
         "returns the number of rows found",
         "counts how many records the query returns",
     ),
     "wrong": (
         ("deletes duplicate tables", "removes duplicate table definitions"),
         ("sorts columns alphabetically", "orders column names A to Z"),
         ("encrypts the database", "encrypts all stored data"),
     ),
     "marks": 2,
     "sol": "<strong>Counts records</strong> returned. Answer: A",
     "hint": "Aggregate function."},
    {"q": "VARCHAR is suitable for:",
     "correct": (
         "a pupil\u2019s first name",
         "text such as a first name",
         "variable-length text like a pupil\u2019s name",
     ),
     "wrong": (
         ("a whole photo file", "binary image data"),
         ("CPU core count", "the number of cores in a CPU"),
         ("today\u2019s date only", "calendar dates only"),
     ),
     "marks": 2,
     "sol": "<strong>Variable-length text</strong>. Answer: A",
     "hint": "Text field type."},
    {"q": "A column in a database table is also called a:",
     "correct": ("field", "a field", "a field (one column in the table)"),
     "wrong": (
         ("record", "a record (one row)"),
         ("query", "an SQL query"),
         ("report", "a printed report"),
     ),
     "marks": 1,
     "sol": "One <strong>field</strong> = one column. Answer: B",
     "hint": "Row = record, column = field."},
    {"q": "SELECT Name, Score FROM Pupil returns:",
     "correct": (
         "only the Name and Score columns",
         "just the Name and Score fields",
         "the Name and Score columns only, not every column",
     ),
     "wrong": (
         ("every column in the table", "all columns including every field"),
         ("no data", "an empty result set always"),
         ("only primary keys", "primary key values only"),
     ),
     "marks": 2,
     "sol": "Lists <strong>named columns only</strong>. Answer: A",
     "hint": "Contrast with SELECT *."},
    {"q": "A composite primary key means:",
     "correct": (
         "two or more columns together identify a record",
         "a combination of fields uniquely identifies each row",
         "two or more columns together uniquely identify a record",
     ),
     "wrong": (
         ("one column identifies each record alone", "a single column is the only identifier", "one column on its own always uniquely identifies every record in the table"),
         ("no key is used", "the table has no key at all", "the table has no primary key or any other way to identify rows"),
         ("every field is text", "all fields must be text type", "every field in the table must be stored as a text or VARCHAR type"),
     ),
     "marks": 2,
     "sol": "Combination of fields is <strong>unique</strong>. Answer: B",
     "hint": "Common in link tables."},
    {"q": "Flat-file storage compared with a relational database often causes:",
     "correct": (
         "more redundancy and inconsistency",
         "duplicate data and conflicting copies",
         "more data redundancy and inconsistency",
     ),
     "wrong": (
         ("less duplication", "less repeated data", "less repeated data because every fact is stored in only one row"),
         ("automatic encryption", "built-in encryption of all files", "automatic encryption of every file so data cannot be read without a key"),
         ("faster networks", "faster network connections", "faster network connections because all data is sent in one packet"),
     ),
     "marks": 2,
     "sol": "Repeating data in one file \u2192 <strong>redundancy</strong>. Answer: B",
     "hint": "Same customer address stored many times."},
    {"q": "SELECT AVG(Score) FROM Pupil calculates:",
     "correct": (
         "the average score",
         "the mean of all Score values",
         "the average (mean) score across matching rows",
     ),
     "wrong": (
         ("the highest score only", "only the maximum score"),
         ("the number of tables", "how many tables exist"),
         ("the primary key", "the primary key value"),
     ),
     "marks": 2,
     "sol": "<strong>AVG</strong> returns the mean value. Answer: A",
     "hint": "Another aggregate like COUNT and MAX."},
]


def db_sql_mcq():
    item = random.choice(_DB_MCQ_BANK)
    opts, ans = _db_mcq_options(item["correct"], item["wrong"])
    return item["q"], item["sol"], item["hint"], item["marks"], opts, ans


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

    return _db_problem_from_output(variant(), difficulty)
