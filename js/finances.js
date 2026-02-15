/**
 * Finances Module - Handles financial tracking and budgeting
 */

const Finances = {
    // Transaction categories
    expenseCategories: [
        { id: 'food', name: 'Food & Dining', icon: '🍔' },
        { id: 'transport', name: 'Transportation', icon: '🚗' },
        { id: 'entertainment', name: 'Entertainment', icon: '🎬' },
        { id: 'shopping', name: 'Shopping', icon: '🛍️' },
        { id: 'bills', name: 'Bills & Utilities', icon: '📄' },
        { id: 'health', name: 'Health', icon: '💊' },
        { id: 'other', name: 'Other', icon: '📌' }
    ],

    incomeCategories: [
        { id: 'salary', name: 'Salary', icon: '💰' },
        { id: 'freelance', name: 'Freelance', icon: '💻' },
        { id: 'investment', name: 'Investment', icon: '📈' },
        { id: 'gift', name: 'Gift', icon: '🎁' },
        { id: 'other', name: 'Other', icon: '📌' }
    ],

    // Initialize finances module
    init() {
        this.bindEvents();
        this.render();
    },

    // Bind event listeners
    bindEvents() {
        document.getElementById('addTransactionBtn')?.addEventListener('click', () => {
            this.showAddModal();
        });
    },

    // Render finances view
    render() {
        this.renderSummary();
        this.renderTransactions();
        this.renderBudgets();
        Charts.initExpensesChart('expensesChart');
        Charts.initFinancialTrendsChart('financialTrendsChart');
    },

    // Render financial summary
    renderSummary() {
        const transactions = Storage.getTransactions();
        const currentMonth = new Date().getMonth();
        const currentYear = new Date().getFullYear();

        // Calculate totals for current month
        const monthlyTransactions = transactions.filter(t => {
            const date = new Date(t.createdAt);
            return date.getMonth() === currentMonth && date.getFullYear() === currentYear;
        });

        const totalIncome = monthlyTransactions
            .filter(t => t.type === 'income')
            .reduce((sum, t) => sum + t.amount, 0);

        const totalExpenses = monthlyTransactions
            .filter(t => t.type === 'expense')
            .reduce((sum, t) => sum + t.amount, 0);

        const balance = totalIncome - totalExpenses;

        // Update UI
        document.getElementById('totalIncome').textContent = this.formatCurrency(totalIncome);
        document.getElementById('totalExpenses').textContent = this.formatCurrency(totalExpenses);
        document.getElementById('totalBalance').textContent = this.formatCurrency(balance);
        document.getElementById('currentBalance').textContent = this.formatCurrency(balance);
    },

    // Render transactions list
    renderTransactions() {
        const container = document.getElementById('transactionsList');
        if (!container) return;

        const transactions = Storage.getTransactions().slice(0, 10);

        if (transactions.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 20px;">
                    <div class="empty-state-icon">💰</div>
                    <div class="empty-state-text">No transactions yet</div>
                </div>
            `;
            return;
        }

        container.innerHTML = transactions.map(t => this.createTransactionItem(t)).join('');

        // Bind delete events
        container.querySelectorAll('.transaction-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const transactionId = e.currentTarget.dataset.transactionId;
                this.deleteTransaction(transactionId);
            });
        });
    },

    // Create transaction item HTML
    createTransactionItem(transaction) {
        const isExpense = transaction.type === 'expense';
        const category = isExpense 
            ? this.expenseCategories.find(c => c.id === transaction.category) 
            : this.incomeCategories.find(c => c.id === transaction.category);
        const icon = category?.icon || '📌';
        const date = new Date(transaction.createdAt).toLocaleDateString();

        return `
            <div class="transaction-item">
                <div class="transaction-icon ${transaction.type}">
                    ${icon}
                </div>
                <div class="transaction-info">
                    <div class="transaction-title">${transaction.description || category?.name || 'Transaction'}</div>
                    <div class="transaction-date">${date}</div>
                </div>
                <div class="transaction-amount ${transaction.type}">
                    ${isExpense ? '-' : '+'}${this.formatCurrency(transaction.amount)}
                </div>
                <button class="habit-action-btn transaction-delete" data-transaction-id="${transaction.id}" title="Delete">🗑️</button>
            </div>
        `;
    },

    // Render budget categories
    renderBudgets() {
        const container = document.getElementById('budgetCategories');
        if (!container) return;

        const budgets = Storage.getBudgets();
        const transactions = Storage.getTransactions();
        const currentMonth = new Date().getMonth();
        const currentYear = new Date().getFullYear();

        if (budgets.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 15px;">
                    <div class="empty-state-text">No budgets set</div>
                </div>
            `;
            return;
        }

        container.innerHTML = budgets.map(budget => {
            const spent = transactions
                .filter(t => {
                    const date = new Date(t.createdAt);
                    return t.type === 'expense' && 
                           t.category === budget.category &&
                           date.getMonth() === currentMonth && 
                           date.getFullYear() === currentYear;
                })
                .reduce((sum, t) => sum + t.amount, 0);

            const percentage = Math.min((spent / budget.amount) * 100, 100);
            const category = this.expenseCategories.find(c => c.id === budget.category);
            const isOverBudget = spent > budget.amount;

            return `
                <div class="budget-category">
                    <div class="budget-category-header">
                        <span>${category?.icon || '📌'} ${category?.name || budget.category}</span>
                        <span class="${isOverBudget ? 'text-danger' : ''}">${this.formatCurrency(spent)} / ${this.formatCurrency(budget.amount)}</span>
                    </div>
                    <div class="budget-bar">
                        <div class="budget-fill" style="width: ${percentage}%; background: ${isOverBudget ? '#ef4444' : '#10b981'}"></div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // Show add transaction modal
    showAddModal() {
        const modalContent = {
            title: 'Add Transaction',
            body: `
                <div class="form-group">
                    <label class="form-label">Type</label>
                    <div class="view-toggle" style="width: 100%;">
                        <button class="view-btn active" id="typeExpense" onclick="Finances.selectType('expense')">Expense</button>
                        <button class="view-btn" id="typeIncome" onclick="Finances.selectType('income')">Income</button>
                    </div>
                </div>
                <div class="form-group">
                    <label class="form-label">Amount</label>
                    <input type="number" class="form-input" id="transactionAmount" placeholder="0.00" step="0.01" min="0">
                </div>
                <div class="form-group">
                    <label class="form-label">Category</label>
                    <select class="form-select" id="transactionCategory">
                        ${this.expenseCategories.map(c => `<option value="${c.id}">${c.icon} ${c.name}</option>`).join('')}
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Description (optional)</label>
                    <input type="text" class="form-input" id="transactionDescription" placeholder="Add a description...">
                </div>
                <div class="form-group">
                    <label class="form-label">Date</label>
                    <input type="date" class="form-input" id="transactionDate" value="${Storage.getTodayString()}">
                </div>
            `,
            footer: `
                <button class="btn btn-secondary" onclick="App.closeModal()">Cancel</button>
                <button class="btn btn-primary" onclick="Finances.addTransaction()">Add Transaction</button>
            `
        };

        App.showModal(modalContent);
        this.selectedType = 'expense';
    },

    // Selected transaction type
    selectedType: 'expense',

    // Select transaction type
    selectType(type) {
        this.selectedType = type;
        
        // Update button states
        document.getElementById('typeExpense')?.classList.toggle('active', type === 'expense');
        document.getElementById('typeIncome')?.classList.toggle('active', type === 'income');

        // Update category dropdown
        const categorySelect = document.getElementById('transactionCategory');
        if (categorySelect) {
            const categories = type === 'expense' ? this.expenseCategories : this.incomeCategories;
            categorySelect.innerHTML = categories.map(c => 
                `<option value="${c.id}">${c.icon} ${c.name}</option>`
            ).join('');
        }
    },

    // Add transaction
    addTransaction() {
        const amount = parseFloat(document.getElementById('transactionAmount')?.value);
        const category = document.getElementById('transactionCategory')?.value;
        const description = document.getElementById('transactionDescription')?.value.trim();
        const date = document.getElementById('transactionDate')?.value;

        if (!amount || amount <= 0) {
            App.showToast('Please enter a valid amount', 'error');
            return;
        }

        Storage.addTransaction({
            type: this.selectedType,
            amount,
            category,
            description,
            date
        });

        App.closeModal();
        App.showToast('Transaction added!', 'success');
        this.render();
        App.updateDashboard();

        // Check for first transaction achievement
        const transactions = Storage.getTransactions();
        if (transactions.length === 1) {
            Achievements.unlock('first_transaction');
        }
        
        // Update chart
        Charts.updateChart('expensesChart');
    },

    // Delete transaction
    deleteTransaction(transactionId) {
        if (confirm('Are you sure you want to delete this transaction?')) {
            Storage.deleteTransaction(transactionId);
            App.showToast('Transaction deleted', 'warning');
            this.render();
            App.updateDashboard();
        }
    },

    // Format currency
    formatCurrency(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },

    // Get total balance
    getTotalBalance() {
        const transactions = Storage.getTransactions();
        const income = transactions.filter(t => t.type === 'income').reduce((sum, t) => sum + t.amount, 0);
        const expenses = transactions.filter(t => t.type === 'expense').reduce((sum, t) => sum + t.amount, 0);
        return income - expenses;
    }
};

// Export for use in other modules
window.Finances = Finances;