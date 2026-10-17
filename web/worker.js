// Runs the Python model in Pyodide off the main thread so the sliders stay responsive.
// Messages in:  {type: 'init', pyodideBase} then {type: 'run', id, preset, settings}
// Messages out: {type: 'progress', text}, {type: 'ready', preset}, {type: 'result', id, data, ms},
//               {type: 'error', id, message}

let py = null;

function progress(text) {
  postMessage({ type: 'progress', text });
}

async function init(pyodideBase) {
  progress('Downloading Python (about 10 MB)');
  const { loadPyodide } = await import(pyodideBase + 'pyodide.mjs');
  py = await loadPyodide({ indexURL: pyodideBase });
  progress('Downloading numpy and scipy (about 17 MB)');
  await py.loadPackage(['numpy', 'scipy']);
  progress('Loading the model');
  const [zip, runner] = await Promise.all([
    fetch('model.zip').then((r) => { if (!r.ok) throw new Error('model.zip not found; run python web/bundle.py'); return r.arrayBuffer(); }),
    fetch('runner.py').then((r) => r.text()),
  ]);
  py.unpackArchive(zip, 'zip', { extractDir: '/home/pyodide/app' });
  await py.runPythonAsync(runner);
}

async function handle(msg) {
  if (msg.type === 'init') {
    await init(msg.pyodideBase);
    postMessage({ type: 'ready' });
  } else if (msg.type === 'run') {
    const t0 = performance.now();
    const call = py.globals.get('run');
    try {
      const out = call(msg.preset, JSON.stringify(msg.settings));
      postMessage({ type: 'result', id: msg.id, data: JSON.parse(out), ms: performance.now() - t0 });
    } finally {
      call.destroy();
    }
  } else if (msg.type === 'preset') {
    progress('Calibrating the ' + msg.label + ' preset');
    const call = py.globals.get('preset_info');
    try {
      postMessage({ type: 'preset', preset: msg.preset, info: JSON.parse(call(msg.preset)) });
    } finally {
      call.destroy();
    }
  }
}

// Messages are handled one at a time, in order.
let queue = Promise.resolve();
onmessage = (event) => {
  const msg = event.data;
  queue = queue.then(() => handle(msg)).catch((err) => {
    const text = String(err && err.message ? err.message : err);
    // Python tracebacks end with the useful line.
    const last = text.trim().split('\n').pop();
    postMessage({ type: 'error', id: msg.id, stage: msg.type, message: last });
  });
};
