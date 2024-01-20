const { app, BrowserWindow } = require('electron');
const path = require('path');

function createWindow() {
    const win = new BrowserWindow({
        width: 1000,
        height: 800,
        devTools: false,
        icon: path.join(__dirname, 'static/img/icon.ico'),
        webPreferences: {
            nodeIntegration: true,
        },
    });

    // Establecer el título personalizado de la ventana
    win.setTitle('CyberChef');
    // Carga la aplicación Flask en la ventana de Electron
    win.loadURL('http://34.41.25.134:8080');
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
            createWindow();
        }
    });
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});
