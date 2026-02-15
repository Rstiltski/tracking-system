/**
 * DataExport Module - Handles data export functionality (CSV/JSON)
 */

const DataExport = {
    // Export all data as JSON
    exportAsJSON() {
        try {
            const allData = {
                habits: Storage.getHabits(),
                habitLogs: Storage.getHabitLogs(),
                tasks: Storage.getTasks(),
                transactions: Storage.getTransactions(),
                budgets: Storage.getBudgets(),
                health: Storage.getHealthData(),
                timeEntries: Storage.getTimeEntries(),
                goals: Storage.getGoals(),
                achievements: Storage.getAchievements(),
                userData: Storage.getUserData(),
                settings: Storage.getSettings(),
                exportedAt: new Date().toISOString()
            };

            const dataStr = JSON.stringify(allData, null, 2);
            const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
            
            const exportFileName = `tracklife_export_${new Date().toISOString().split('T')[0]}.json`;
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileName);
            linkElement.click();
            
            App.showToast('Data exported successfully!', 'success');
        } catch (error) {
            console.error('Error exporting data as JSON:', error);
            App.showToast('Error exporting data', 'error');
        }
    },

    // Export all data as CSV
    exportAsCSV() {
        try {
            let csvContent = '';
            
            // Export habits
            csvContent += 'Habits\n';
            csvContent += 'ID,Name,Icon,Color,Frequency,Created At,Streak\n';
            const habits = Storage.getHabits();
            habits.forEach(habit => {
                csvContent += `"${habit.id}","${habit.name}","${habit.icon}","${habit.color}","${habit.frequency || 'daily'}","${habit.createdAt || ''}",${habit.streak || 0}\n`;
            });
            csvContent += '\n';
            
            // Export tasks
            csvContent += 'Tasks\n';
            csvContent += 'ID,Title,Description,Due Date,Priority,Category,Completed,Created At\n';
            const tasks = Storage.getTasks();
            tasks.forEach(task => {
                csvContent += `"${task.id}","${task.title}","${task.description || ''}","${task.dueDate || ''}","${task.priority || 'medium'}","${task.category || 'personal'}",${task.completed || false},"${task.createdAt || ''}"\n`;
            });
            csvContent += '\n';
            
            // Export transactions
            csvContent += 'Transactions\n';
            csvContent += 'ID,Description,Amount,Type,Category,Date,Created At\n';
            const transactions = Storage.getTransactions();
            transactions.forEach(transaction => {
                csvContent += `"${transaction.id}","${transaction.description || ''}",${transaction.amount},"${transaction.type || 'expense'}","${transaction.category || 'other'}","${transaction.date || ''}","${transaction.createdAt || ''}"\n`;
            });
            csvContent += '\n';
            
            // Export goals
            csvContent += 'Goals\n';
            csvContent += 'ID,Title,Description,Target,Current,Unit,Deadline,Created At\n';
            const goals = Storage.getGoals();
            goals.forEach(goal => {
                csvContent += `"${goal.id}","${goal.title}","${goal.description || ''}",${goal.target || 0},${goal.current || 0},"${goal.unit || ''}","${goal.deadline || ''}","${goal.createdAt || ''}"\n`;
            });
            csvContent += '\n';
            
            // Export time entries
            csvContent += 'Time Entries\n';
            csvContent += 'ID,Category,Duration,Date,Created At\n';
            const timeEntries = Storage.getTimeEntries();
            timeEntries.forEach(entry => {
                csvContent += `"${entry.id}","${entry.category || 'work'}",${entry.duration || 0},"${entry.date || ''}","${entry.createdAt || ''}"\n`;
            });
            
            const dataUri = 'data:text/csv;charset=utf-8,'+ encodeURIComponent(csvContent);
            const exportFileName = `tracklife_export_${new Date().toISOString().split('T')[0]}.csv`;
            
            const linkElement = document.createElement('a');
            linkElement.setAttribute('href', dataUri);
            linkElement.setAttribute('download', exportFileName);
            linkElement.click();
            
            App.showToast('Data exported successfully!', 'success');
        } catch (error) {
            console.error('Error exporting data as CSV:', error);
            App.showToast('Error exporting data', 'error');
        }
    },

    // Import data from JSON
    importFromJSON(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = (event) => {
                try {
                    const importedData = JSON.parse(event.target.result);
                    
                    // Validate that it's a proper export
                    if (!importedData.exportedAt) {
                        throw new Error('Invalid export file format');
                    }
                    
                    // Confirm overwrite
                    if (!confirm('This will overwrite all your current data. Are you sure?')) {
                        reject(new Error('Import cancelled'));
                        return;
                    }
                    
                    // Import all data
                    Storage.saveHabits(importedData.habits || []);
                    Storage.saveHabitLogs(importedData.habitLogs || {});
                    Storage.saveTasks(importedData.tasks || []);
                    Storage.saveTransactions(importedData.transactions || []);
                    Storage.saveBudgets(importedData.budgets || []);
                    Storage.saveHealthData(importedData.health || { weight: [], sleep: [], mood: [] });
                    Storage.saveTimeEntries(importedData.timeEntries || []);
                    Storage.saveGoals(importedData.goals || []);
                    Storage.saveAchievements(importedData.achievements || []);
                    Storage.saveUserData(importedData.userData || {});
                    Storage.saveSettings(importedData.settings || {});
                    
                    App.showToast('Data imported successfully!', 'success');
                    App.updateAll(); // Refresh all modules
                    
                    resolve(true);
                } catch (error) {
                    console.error('Error importing data:', error);
                    App.showToast('Error importing data. Invalid file format.', 'error');
                    reject(error);
                }
            };
            
            reader.onerror = () => {
                reject(new Error('Error reading file'));
            };
            
            reader.readAsText(file);
        });
    },

    // Show export modal
    showExportModal() {
        const modalContent = {
            title: 'Export Data',
            body: `
                <div class="form-group">
                    <p>Choose the format to export your data:</p>
                </div>
                <div class="form-group">
                    <button class="btn btn-primary" style="margin-right: 10px;" onclick="DataExport.exportAsJSON()">
                        Export as JSON
                    </button>
                    <button class="btn btn-secondary" onclick="DataExport.exportAsCSV()">
                        Export as CSV
                    </button>
                </div>
                <div class="form-group">
                    <small class="text-muted">Your data includes all habits, tasks, finances, health metrics, time entries, goals, and achievements.</small>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Close</button>
            `
        };

        App.showModal(modalContent);
    },

    // Show import modal
    showImportModal() {
        const modalContent = {
            title: 'Import Data',
            body: `
                <div class="form-group">
                    <label class="form-label">Select JSON file to import</label>
                    <input type="file" class="form-input" id="importFile" accept=".json">
                </div>
                <div class="form-group">
                    <small class="text-muted">Warning: This will overwrite all your current data.</small>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="DataExport.handleImport()">Import Data</button>
            `
        };

        App.showModal(modalContent);
    },

    // Show backup/restore modal
    showBackupRestoreModal() {
        const modalContent = {
            title: 'Backup & Restore',
            body: `
                <div class="backup-restore-section">
                    <h4>Backup Data</h4>
                    <p>Create a backup of your current data</p>
                    <button class="btn btn-primary" style="margin-bottom: 20px;" onclick="DataExport.exportAsJSON()">
                        Create Backup
                    </button>
                </div>
                
                <div class="backup-restore-section">
                    <h4>Restore Data</h4>
                    <p>Restore from a previously created backup</p>
                    <input type="file" class="form-input" id="restoreFile" accept=".json" style="margin-bottom: 10px;">
                    <button class="btn btn-secondary" onclick="DataExport.handleRestore()">
                        Restore from Backup
                    </button>
                </div>
                
                <div class="backup-restore-section">
                    <h4>Data Reset</h4>
                    <p>Reset all your data (cannot be undone)</p>
                    <button class="btn btn-danger" onclick="DataExport.showResetModal()">
                        Reset All Data
                    </button>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Close</button>
            `
        };

        App.showModal(modalContent);
    },

    // Handle restore from backup
    async handleRestore() {
        const fileInput = document.getElementById('restoreFile');
        if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
            App.showToast('Please select a backup file to restore', 'error');
            return;
        }

        const file = fileInput.files[0];
        if (file.type !== 'application/json') {
            App.showToast('Please select a valid JSON backup file', 'error');
            return;
        }

        try {
            await this.importFromJSON(file);
            App.closeModal();
            App.showToast('Data restored successfully!', 'success');
        } catch (error) {
            console.error('Restore failed:', error);
        }
    },

    // Show reset confirmation modal
    showResetModal() {
        const modalContent = {
            title: 'Reset All Data',
            body: `
                <div class="form-group">
                    <p class="warning-text">⚠️ WARNING: This will permanently delete ALL your data including habits, tasks, finances, health metrics, goals, and achievements.</p>
                    <p>This action cannot be undone. Are you sure you want to continue?</p>
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-danger" onclick="DataExport.resetAllData()">Reset Everything</button>
            `
        };

        App.showModal(modalContent);
    },

    // Reset all data
    resetAllData() {
        if (!confirm('This will permanently delete ALL your data. Are you absolutely sure?')) {
            return;
        }

        try {
            Storage.clearAll();
            App.showToast('All data has been reset', 'success');
            App.closeModal();

            // Refresh the app to update all views
            App.updateAll();
        } catch (error) {
            console.error('Error resetting data:', error);
            App.showToast('Error resetting data', 'error');
        }
    },

    // Handle import from modal
    async handleImport() {
        const fileInput = document.getElementById('importFile');
        if (!fileInput || !fileInput.files || fileInput.files.length === 0) {
            App.showToast('Please select a file to import', 'error');
            return;
        }

        const file = fileInput.files[0];
        if (file.type !== 'application/json') {
            App.showToast('Please select a valid JSON file', 'error');
            return;
        }

        try {
            await this.importFromJSON(file);
            App.closeModal();
        } catch (error) {
            console.error('Import failed:', error);
        }
    }
};

// Export for use in other modules
window.DataExport = DataExport;