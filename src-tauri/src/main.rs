// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use chrono::Local;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tauri::{
    CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu, SystemTrayMenuItem,
};

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ClipboardEntry {
    timestamp: String,
    text: String,
}

#[derive(Debug, Clone)]
struct AppState {
    monitoring_enabled: Arc<Mutex<bool>>,
    history: Arc<Mutex<Vec<ClipboardEntry>>>,
    storage_path: PathBuf,
}

impl AppState {
    fn new() -> Self {
        let storage_path = std::env::current_dir()
            .unwrap_or_else(|_| PathBuf::from("."))
            .join("clipboard_history.json");

        Self {
            monitoring_enabled: Arc::new(Mutex::new(true)),
            history: Arc::new(Mutex::new(Vec::new())),
            storage_path,
        }
    }

    fn load_history(&self) -> Result<Vec<ClipboardEntry>, String> {
        if self.storage_path.exists() {
            let content = fs::read_to_string(&self.storage_path)
                .map_err(|e| format!("Failed to read history file: {}", e))?;
            let history: Vec<ClipboardEntry> = serde_json::from_str(&content)
                .map_err(|e| format!("Failed to parse history: {}", e))?;
            Ok(history)
        } else {
            Ok(Vec::new())
        }
    }

    fn save_history(&self, history: &Vec<ClipboardEntry>) -> Result<(), String> {
        let content = serde_json::to_string_pretty(history)
            .map_err(|e| format!("Failed to serialize history: {}", e))?;
        fs::write(&self.storage_path, content)
            .map_err(|e| format!("Failed to write history file: {}", e))?;
        Ok(())
    }
}

#[tauri::command]
fn get_history(state: tauri::State<AppState>) -> Result<Vec<ClipboardEntry>, String> {
    let history = state.history.lock().unwrap();
    Ok(history.clone())
}

#[tauri::command]
fn add_to_history(text: String, state: tauri::State<AppState>) -> Result<ClipboardEntry, String> {
    let monitoring = state.monitoring_enabled.lock().unwrap();
    if !*monitoring {
        return Err("Monitoring is disabled".to_string());
    }
    drop(monitoring);

    let timestamp = Local::now().format("%Y-%m-%d %H:%M:%S").to_string();
    let entry = ClipboardEntry {
        timestamp: timestamp.clone(),
        text: text.clone(),
    };

    let mut history = state.history.lock().unwrap();
    history.insert(0, entry.clone());

    // Save to file
    state.save_history(&history)?;

    Ok(entry)
}

#[tauri::command]
fn clear_history(state: tauri::State<AppState>) -> Result<(), String> {
    let mut history = state.history.lock().unwrap();
    history.clear();
    state.save_history(&history)?;
    Ok(())
}

#[tauri::command]
fn toggle_monitoring(state: tauri::State<AppState>) -> Result<bool, String> {
    let mut monitoring = state.monitoring_enabled.lock().unwrap();
    *monitoring = !*monitoring;
    Ok(*monitoring)
}

#[tauri::command]
fn get_monitoring_status(state: tauri::State<AppState>) -> Result<bool, String> {
    let monitoring = state.monitoring_enabled.lock().unwrap();
    Ok(*monitoring)
}

#[tauri::command]
fn export_history(file_path: String, state: tauri::State<AppState>) -> Result<(), String> {
    let history = state.history.lock().unwrap();
    let mut content = String::new();

    for entry in history.iter() {
        content.push_str(&format!("{}\n{}\n\n", entry.timestamp, entry.text));
    }

    fs::write(&file_path, content).map_err(|e| format!("Failed to export history: {}", e))?;

    Ok(())
}

fn create_system_tray() -> SystemTray {
    let show = CustomMenuItem::new("show".to_string(), "显示主窗口");
    let toggle = CustomMenuItem::new("toggle".to_string(), "关闭监听");
    let quit = CustomMenuItem::new("quit".to_string(), "退出");

    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(toggle)
        .add_native_item(SystemTrayMenuItem::Separator)
        .add_item(quit);

    SystemTray::new().with_menu(tray_menu)
}

fn main() {
    let app_state = AppState::new();

    // Load history on startup
    if let Ok(history) = app_state.load_history() {
        let mut hist = app_state.history.lock().unwrap();
        *hist = history;
    }

    tauri::Builder::default()
        .manage(app_state)
        .system_tray(create_system_tray())
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick {
                position: _,
                size: _,
                ..
            } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                    window.set_focus().unwrap();
                }
                "toggle" => {
                    let state = app.state::<AppState>();
                    let mut monitoring = state.monitoring_enabled.lock().unwrap();
                    *monitoring = !*monitoring;

                    let tray_handle = app.tray_handle();
                    let menu_item = tray_handle.get_item("toggle");
                    if *monitoring {
                        menu_item.set_title("关闭监听").unwrap();
                    } else {
                        menu_item.set_title("开启监听").unwrap();
                    }

                    // Emit event to frontend
                    app.emit_all("monitoring-changed", *monitoring).unwrap();
                }
                "quit" => {
                    std::process::exit(0);
                }
                _ => {}
            },
            _ => {}
        })
        .invoke_handler(tauri::generate_handler![
            get_history,
            add_to_history,
            clear_history,
            toggle_monitoring,
            get_monitoring_status,
            export_history,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
