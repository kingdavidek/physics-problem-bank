(function (global) {
  'use strict';

  var PYODIDE_INDEX = '/static/vendor/pyodide/';
  var loadPromise = null;
  var runnerReady = false;

  var STUDENT_RUNNER_PY = [
    'def __run_student_with_capture__():',
    '    import json',
    '    import io',
    '    import contextlib',
    '    import traceback',
    '    setup = __setup_code__ or ""',
    '    if setup.strip():',
    '        try:',
    "            exec(compile(setup, '<setup>', 'exec'), {'__name__': '__main__'})",
    '        except Exception:',
    '            return json.dumps({"ok": False, "error": "Test could not be run."})',
    '    code = __student_code__',
    '    try:',
    "        compiled = compile(code, '<student>', 'exec')",
    '    except SyntaxError as exc:',
    '        line = exc.lineno or 1',
    '        text = exc.text.rstrip("\\n") if exc.text else ""',
    '        offset = exc.offset or 0',
    '        parts = ["  File \\"<student>\\", line %d" % line]',
    '        if text:',
    '            parts.append("    " + text.rstrip())',
    '            if offset > 0:',
    '                parts.append("    " + (" " * (offset - 1)) + "^")',
    '        parts.append("SyntaxError: %s" % (exc.msg or exc))',
    '        return json.dumps({"ok": False, "error": "\\n".join(parts)})',
    '    __captured_stdout__ = io.StringIO()',
    '    try:',
    '        with contextlib.redirect_stdout(__captured_stdout__):',
    "            exec(compiled, {'__name__': '__main__'})",
    '        return json.dumps({"ok": True, "stdout": __captured_stdout__.getvalue()})',
    '    except Exception as exc:',
    '        tb_lines = []',
    '        for frame in traceback.extract_tb(exc.__traceback__):',
    "            if frame.filename == '<student>':",
    '                tb_lines.append(',
    '                    "  File \\"<student>\\", line %d, in <module>" % frame.lineno',
    '                )',
    '                if frame.line:',
    '                    tb_lines.append("    " + frame.line.rstrip())',
    '        if not tb_lines:',
    '            tb_lines.append("  File \\"<student>\\", line 1, in <module>")',
    '        tb_lines.append("%s: %s" % (type(exc).__name__, exc))',
    '        return json.dumps({"ok": False, "error": "\\n".join(tb_lines)})',
  ].join('\n');

  function normalizeStdout(value) {
    return String(value || '').replace(/\r\n/g, '\n').replace(/\r/g, '\n').trim();
  }

  function formatStudentError(raw) {
    return String(raw || '')
      .replace(/"<student>"/g, 'your code')
      .replace(/<student>/g, 'your code')
      .trim();
  }

  function loadPyodideRuntime() {
    if (global.__pythonRunGraderPyodide) {
      return Promise.resolve(global.__pythonRunGraderPyodide);
    }
    if (loadPromise) {
      return loadPromise;
    }
    loadPromise = new Promise(function (resolve, reject) {
      if (typeof global.loadPyodide === 'function') {
        global.loadPyodide({ indexURL: PYODIDE_INDEX }).then(resolve).catch(reject);
        return;
      }
      var script = document.createElement('script');
      script.src = PYODIDE_INDEX + 'pyodide.js';
      script.onload = function () {
        global.loadPyodide({ indexURL: PYODIDE_INDEX }).then(resolve).catch(reject);
      };
      script.onerror = function () {
        reject(new Error('Could not load Python runner.'));
      };
      document.head.appendChild(script);
    }).then(function (pyodide) {
      global.__pythonRunGraderPyodide = pyodide;
      return pyodide;
    });
    return loadPromise;
  }

  function ensureStudentRunner(pyodide) {
    if (runnerReady) {
      return;
    }
    pyodide.runPython(STUDENT_RUNNER_PY);
    runnerReady = true;
  }

  function stdinLines(stdinValue) {
    if (stdinValue == null) {
      return [];
    }
    return String(stdinValue).split('\n');
  }

  function readInputCallCount(pyodide) {
    try {
      return pyodide.runPython('int(_input_call_count)');
    } catch (readErr) {
      return 0;
    }
  }

  function parseRunnerResult(raw) {
    var text = raw;
    if (text != null && typeof text !== 'string') {
      text = String(text);
    }
    return JSON.parse(text || '{}');
  }

  function runOneTest(pyodide, code, lines, setup, files) {
    pyodide.setStdout({ batched: function () {} });
    pyodide.setStderr({ batched: function () {} });
    pyodide.globals.set('__student_code__', code);
    pyodide.globals.set('__setup_code__', setup || '');
    pyodide.globals.set('__stdin_lines__', lines);
    pyodide.globals.set('__virtual_files_json__', JSON.stringify(files || {}));
    var bootstrap = [
      'import io',
      'import json',
      'import builtins',
      '_lines = list(__stdin_lines__)',
      '_i = 0',
      '_input_call_count = 0',
      '_virtual_files = json.loads(__virtual_files_json__)',
      'def input(prompt=""):',
      '    global _i, _input_call_count',
      '    _input_call_count += 1',
      '    if _i >= len(_lines):',
      '        return ""',
      '    v = _lines[_i]',
      '    _i += 1',
      '    return v',
      'builtins.input = input',
      'def open(path, mode="r", *args, **kwargs):',
      '    name = str(path)',
      '    if name not in _virtual_files:',
      '        raise FileNotFoundError(2, "No such file or directory", name)',
      '    return io.StringIO(_virtual_files[name])',
      'builtins.open = open',
    ].join('\n');
    pyodide.runPython(bootstrap);
    ensureStudentRunner(pyodide);
    var resultJson = pyodide.runPython('__run_student_with_capture__()');
    var result = parseRunnerResult(resultJson);
    var inputCalls = readInputCallCount(pyodide);
    if (!result.ok) {
      return {
        stdout: '',
        error: formatStudentError(result.error),
        input_calls: inputCalls,
      };
    }
    return {
      stdout: normalizeStdout(result.stdout),
      error: '',
      input_calls: inputCalls,
    };
  }

  function runPythonRunTests(code, tests) {
    var cases = Array.isArray(tests) ? tests : [];
    return loadPyodideRuntime().then(function (pyodide) {
      var results = [];
      for (var i = 0; i < cases.length; i += 1) {
        var testCase = cases[i] || {};
        try {
          var outcome = runOneTest(
            pyodide,
            code,
            stdinLines(testCase.stdin),
            testCase.setup || '',
            testCase.files || {}
          );
          var row = {
            stdout: outcome.stdout,
            input_calls: outcome.input_calls || 0,
          };
          if (outcome.error) {
            row.error = outcome.error;
          }
          results.push(row);
        } catch (err) {
          results.push({
            stdout: '',
            error: 'Your code could not be run — try Check again.',
          });
        }
      }
      return results;
    });
  }

  global.runPythonRunTests = runPythonRunTests;
})(typeof window !== 'undefined' ? window : globalThis);
