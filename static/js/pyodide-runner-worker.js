/* Pyodide runner worker — blocking stdin via SharedArrayBuffer + Atomics.wait */
let pyodide = null;
let stdinControl = null;
let stdinBytes = null;
let pyodideLoading = null;

function loadPyodideRuntime() {
  if (pyodide) {
    return Promise.resolve(pyodide);
  }
  if (!pyodideLoading) {
    pyodideLoading = new Promise((resolve, reject) => {
      try {
        importScripts('https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js');
        loadPyodide()
          .then((instance) => {
            pyodide = instance;
            resolve(instance);
          })
          .catch(reject);
      } catch (err) {
        reject(err);
      }
    });
  }
  return pyodideLoading;
}

function waitForStdinLine() {
  Atomics.store(stdinControl, 0, 0);
  Atomics.store(stdinControl, 1, 0);
  self.postMessage({ type: 'stdin_request' });

  while (Atomics.load(stdinControl, 0) === 0) {
    const result = Atomics.wait(stdinControl, 0, 0, 100);
    if (result === 'timed-out') {
      pyodide.checkInterrupt();
    }
  }

  const len = Atomics.load(stdinControl, 1);
  Atomics.store(stdinControl, 0, 0);
  Atomics.store(stdinControl, 1, 0);
  return len;
}

function setupStreams() {
  pyodide.setStdout({
    raw: (byte) => {
      self.postMessage({ type: 'stdout', text: String.fromCharCode(byte) });
    },
  });
  pyodide.setStderr({
    batched: (text) => {
      self.postMessage({ type: 'stderr', text: text });
    },
  });
  pyodide.setStdin({
    isatty: true,
    read: (buffer) => {
      const len = waitForStdinLine();
      if (len <= 0) {
        return 0;
      }
      buffer.set(stdinBytes.subarray(0, Math.min(len, buffer.length)));
      return Math.min(len, buffer.length);
    },
  });
}

self.onmessage = async (event) => {
  const msg = event.data;

  if (msg.type === 'init') {
    try {
      stdinControl = new Int32Array(msg.stdinControl);
      stdinBytes = new Uint8Array(msg.stdinBytes);
      await loadPyodideRuntime();
      if (msg.interruptBuffer) {
        pyodide.setInterruptBuffer(msg.interruptBuffer);
      }
      setupStreams();
      self.postMessage({ type: 'ready' });
    } catch (err) {
      self.postMessage({ type: 'init_error', message: err.message || String(err) });
    }
    return;
  }

  if (msg.type === 'run') {
    try {
      await pyodide.runPythonAsync(msg.code);
      self.postMessage({ type: 'done' });
    } catch (err) {
      self.postMessage({ type: 'error', message: err.message });
    }
  }
};
