const { app, BrowserWindow } = require("electron");
const path = require("path");
const { spawn } = require("child_process");
const net = require("net");

const BACKEND_PORT = 8000;
const BACKEND_HOST = "127.0.0.1";

let backendProcess = null;

function getBackendPaths() {
  const resourcesRoot = app.isPackaged
    ? process.resourcesPath
    : path.resolve(__dirname, "../../");
  const backendRoot = app.isPackaged
    ? path.join(resourcesRoot, "backend")
    : path.join(resourcesRoot, "backend");

  const pythonBin = app.isPackaged
    ? path.join(backendRoot, "venv", "bin", "python")
    : path.join(backendRoot, "venv", "bin", "python");

  const runnerScript = path.join(backendRoot, "desktop_runner.py");

  return { backendRoot, pythonBin, runnerScript };
}

function waitForBackend(timeoutMs = 15000) {
  const start = Date.now();

  return new Promise((resolve, reject) => {
    const check = () => {
      const socket = new net.Socket();
      socket.setTimeout(1000);
      socket.connect(BACKEND_PORT, BACKEND_HOST, () => {
        socket.destroy();
        resolve();
      });
      socket.on("error", () => {
        socket.destroy();
        if (Date.now() - start > timeoutMs) {
          reject(new Error("Backend startup timed out."));
        } else {
          setTimeout(check, 300);
        }
      });
      socket.on("timeout", () => {
        socket.destroy();
        if (Date.now() - start > timeoutMs) {
          reject(new Error("Backend startup timed out."));
        } else {
          setTimeout(check, 300);
        }
      });
    };

    check();
  });
}

function startBackend() {
  const { backendRoot, pythonBin, runnerScript } = getBackendPaths();

  backendProcess = spawn(pythonBin, [runnerScript], {
    cwd: backendRoot,
    env: {
      ...process.env,
      BACKSTAB_DESKTOP: "1",
      DJANGO_SETTINGS_MODULE: "core.settings",
      PYTHONUNBUFFERED: "1"
    },
    stdio: "pipe"
  });

  backendProcess.stdout.on("data", (chunk) => {
    process.stdout.write(`[backend] ${chunk}`);
  });

  backendProcess.stderr.on("data", (chunk) => {
    process.stderr.write(`[backend] ${chunk}`);
  });

  backendProcess.on("exit", (code) => {
    backendProcess = null;
    if (code !== 0) {
      console.error(`Backend process exited with code ${code}`);
    }
  });
}

function stopBackend() {
  if (!backendProcess) {
    return;
  }
  backendProcess.kill("SIGTERM");
}

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 780,
    webPreferences: {
      contextIsolation: true,
      nodeIntegration: false
    }
  });

  const indexPath = app.isPackaged
    ? path.join(process.resourcesPath, "frontend-dist", "index.html")
    : path.resolve(__dirname, "../../front-end/dist/index.html");

  win.loadFile(indexPath);
}

app.whenReady().then(async () => {
  startBackend();
  await waitForBackend();
  createWindow();
});

app.on("before-quit", () => {
  stopBackend();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});
