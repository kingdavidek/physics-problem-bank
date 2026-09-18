(function () {
  'use strict';

  const runBtn = document.getElementById('py-run');
  const WORKER_URL = runBtn && runBtn.getAttribute('data-worker-url');
  if (runBtn) {
    runBtn.addEventListener('click', function () { window.runInteractive(); });
  }

  let pyWorker = null;
  let workerReady = false;
  let workerStarting = false;
  let stdinControl = null;
  let stdinBytes = null;
  let interruptBuffer = null;
  let fallbackPyodide = null;
  let fallbackReady = false;
  let stdinSendHandler = null;
  let stdinKeyHandler = null;
  let pendingStdinEcho = null;

  function getUi() {
    return {
      outputElem: document.getElementById('py-output'),
      inputContainer: document.getElementById('py-input-container'),
      inputField: document.getElementById('py-input'),
      sendBtn: document.getElementById('py-send'),
      runBtn: document.getElementById('py-run'),
      codeElem: document.getElementById('py-code'),
    };
  }

  function appendOutput(text, isStderr) {
    const outputElem = getUi().outputElem;
    if (!text) return;
    if (isStderr && outputElem.textContent && !outputElem.textContent.endsWith('\n')) {
      outputElem.textContent += '\n';
    }
    outputElem.textContent += text;
    if (isStderr && !text.endsWith('\n')) {
      outputElem.textContent += '\n';
    }
  }

  function showInputUi() {
    const ui = getUi();
    ui.inputContainer.style.display = 'flex';
    ui.inputField.value = '';
    ui.inputField.focus();
  }

  function unbindInputHandlers() {
    const ui = getUi();
    if (stdinSendHandler) {
      ui.sendBtn.removeEventListener('click', stdinSendHandler);
      ui.inputField.removeEventListener('keydown', stdinKeyHandler);
      stdinSendHandler = null;
      stdinKeyHandler = null;
    }
  }

  function hideInputUi() {
    const ui = getUi();
    ui.inputContainer.style.display = 'none';
    unbindInputHandlers();
  }

  function echoStdinLine(line) {
    const outputElem = getUi().outputElem;
    if (outputElem.textContent.length > 0) {
      outputElem.textContent += line + '\n';
      return;
    }
    pendingStdinEcho = line;
  }

  function flushPendingStdinEcho() {
    if (pendingStdinEcho === null) {
      return;
    }
    getUi().outputElem.textContent += pendingStdinEcho + '\n';
    pendingStdinEcho = null;
  }

  function deliverStdinLine() {
    const ui = getUi();
    const line = ui.inputField.value;
    const encoded = new TextEncoder().encode(line + '\n');
    const len = Math.min(encoded.length, stdinBytes.length);
    stdinBytes.set(encoded.subarray(0, len));
    Atomics.store(stdinControl, 1, len);
    Atomics.store(stdinControl, 0, 1);
    Atomics.notify(stdinControl, 0);
    echoStdinLine(line);
    hideInputUi();
  }

  function bindInputHandlers() {
    const ui = getUi();
    unbindInputHandlers();
    stdinSendHandler = deliverStdinLine;
    stdinKeyHandler = function (e) {
      if (e.key === 'Enter') {
        e.preventDefault();
        deliverStdinLine();
      }
    };
    ui.sendBtn.addEventListener('click', stdinSendHandler);
    ui.inputField.addEventListener('keydown', stdinKeyHandler);
  }

  function canUseWorkerStdin() {
    if (typeof SharedArrayBuffer === 'undefined' || typeof Worker === 'undefined') {
      return false;
    }
    try {
      new SharedArrayBuffer(8);
      return true;
    } catch (err) {
      return false;
    }
  }

  async function ensureWorker() {
    return new Promise(async function (resolve, reject) {
      if (workerReady) {
        resolve(true);
        return;
      }
      if (workerStarting) {
        const waitReady = function (event) {
          if (event.data.type === 'ready') {
            pyWorker.removeEventListener('message', waitReady);
            resolve(true);
          } else if (event.data.type === 'init_error') {
            pyWorker.removeEventListener('message', waitReady);
            reject(new Error(event.data.message));
          }
        };
        pyWorker.addEventListener('message', waitReady);
        return;
      }

      if (!canUseWorkerStdin()) {
        resolve(false);
        return;
      }

      workerStarting = true;
      const ui = getUi();
      ui.outputElem.textContent = 'Loading Python interpreter... (this may take a few seconds)';

      stdinControl = new Int32Array(new SharedArrayBuffer(8));
      stdinBytes = new Uint8Array(new SharedArrayBuffer(4096));
      interruptBuffer = new Int32Array(new SharedArrayBuffer(4));

      try {
        const workerResponse = await fetch(WORKER_URL);
        if (!workerResponse.ok) {
          throw new Error('Could not load Python worker script.');
        }
        const workerSource = await workerResponse.text();
        const workerBlob = new Blob([workerSource], { type: 'application/javascript' });
        pyWorker = new Worker(URL.createObjectURL(workerBlob));
      } catch (err) {
        workerStarting = false;
        reject(err);
        return;
      }

      pyWorker.onmessage = handleWorkerMessage;
      pyWorker.onerror = function (err) {
        workerStarting = false;
        ui.outputElem.textContent = 'Failed to start Python worker: ' + err.message;
        reject(err);
      };

      pyWorker.addEventListener('message', function onReady(event) {
        if (event.data.type === 'ready') {
          pyWorker.removeEventListener('message', onReady);
          workerReady = true;
          workerStarting = false;
          ui.outputElem.textContent = '';
          resolve(true);
        } else if (event.data.type === 'init_error') {
          pyWorker.removeEventListener('message', onReady);
          workerStarting = false;
          reject(new Error(event.data.message));
        }
      });

      pyWorker.postMessage({
        type: 'init',
        stdinControl: stdinControl.buffer,
        stdinBytes: stdinBytes.buffer,
        interruptBuffer: interruptBuffer.buffer,
      });
    });
  }

  function handleWorkerMessage(event) {
    const msg = event.data;
    const ui = getUi();

    if (msg.type === 'stdout') {
      const outputElem = ui.outputElem;
      outputElem.textContent += msg.text;
      flushPendingStdinEcho();
      return;
    }

    if (msg.type === 'stderr') {
      appendOutput(msg.text, true);
      return;
    }

    if (msg.type === 'stdin_request') {
      showInputUi();
      bindInputHandlers();
      return;
    }

    if (msg.type === 'done') {
      hideInputUi();
      ui.runBtn.disabled = false;
      if (!ui.outputElem.textContent) {
        ui.outputElem.textContent = '(program finished)';
      }
      return;
    }

    if (msg.type === 'error') {
      hideInputUi();
      ui.runBtn.disabled = false;
      appendOutput('Error: ' + msg.message, true);
    }
  }

  function loadFallbackScript() {
    return new Promise(function (resolve, reject) {
      if (window.loadPyodide) {
        resolve();
        return;
      }
      const script = document.createElement('script');
      script.src = '/static/vendor/pyodide/pyodide.js';
      script.onload = resolve;
      script.onerror = function () {
        reject(new Error('Could not load Pyodide.'));
      };
      document.head.appendChild(script);
    });
  }

  async function ensureFallbackPyodide() {
    if (fallbackReady) return true;
    const ui = getUi();
    ui.outputElem.textContent = 'Loading Python interpreter... (this may take a few seconds)';
    await loadFallbackScript();
    fallbackPyodide = await loadPyodide({ indexURL: '/static/vendor/pyodide/' });
    fallbackPyodide.setStdout({
      raw: function (byte) {
        ui.outputElem.textContent += String.fromCharCode(byte);
        flushPendingStdinEcho();
      },
    });
    fallbackPyodide.setStderr({
      batched: function (text) {
        appendOutput(text, true);
      },
    });
    fallbackPyodide.setStdin({
      isatty: true,
      stdin: function () {
        const value = window.prompt('Python is waiting for your input:');
        if (value === null) {
          return undefined;
        }
        echoStdinLine(value);
        return value + '\n';
      },
    });
    fallbackReady = true;
    ui.outputElem.textContent = '';
    return true;
  }

  async function runWithFallback(code) {
    const ui = getUi();
    try {
      await ensureFallbackPyodide();
    } catch (err) {
      ui.outputElem.textContent = 'Failed to load Python interpreter: ' + err.message;
      ui.runBtn.disabled = false;
      return;
    }

    ui.outputElem.textContent = '';
    hideInputUi();

    try {
      await fallbackPyodide.runPythonAsync(code);
      if (!ui.outputElem.textContent) {
        ui.outputElem.textContent = '(program finished)';
      }
    } catch (err) {
      appendOutput('Error: ' + err.message, true);
    }

    ui.runBtn.disabled = false;
  }

  window.runInteractive = async function () {
    const ui = getUi();
    const code = ui.codeElem.value;
    ui.outputElem.textContent = '';
    pendingStdinEcho = null;
    hideInputUi();
    ui.runBtn.disabled = true;

    try {
      const workerOk = await ensureWorker();
      if (workerOk && pyWorker) {
        pyWorker.postMessage({ type: 'run', code: code });
        return;
      }
    } catch (err) {
      console.warn('Pyodide worker unavailable, using fallback input:', err);
    }

    await runWithFallback(code);
  };
})();
